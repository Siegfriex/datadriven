// ========================================
// File: 03_gds_execution.cypher
// Purpose: GDS 분석 파이프라인 (Projection -> Analysis -> Write)
// Prerequisite: 관계 생성 완료
// ========================================

// 1. Graph Projection (메모리 로드)
// Artist 노드와 관계를 투영
// AFFILIATED_WITH를 통해 같은 Institution에 소속된 작가 간 간접 관계 생성
// 기존 프로젝션 삭제 (있으면)
CALL gds.graph.drop('artist-graph', false) YIELD graphName;

// COLLABORATED_WITH 관계가 있으면 우선 사용, 없으면 AFFILIATED_WITH 기반 간접 관계 사용
CALL gds.graph.project(
  'artist-graph',
  'Artist',
  {
    COLLABORATED_WITH: {
      type: 'COLLABORATED_WITH',
      orientation: 'UNDIRECTED',
      properties: ['weight']
    },
    AFFILIATED_WITH: {
      type: 'AFFILIATED_WITH',
      orientation: 'UNDIRECTED',
      aggregation: 'SINGLE'
    }
  },
  {
    nodeProperties: ['composite_score', 'inst_score', 'acad_score', 'network_score']
  }
) YIELD graphName, nodeCount, relationshipCount;

// 2. Degree Centrality (연결정도 중심성)
// 가장 많은 협업을 한 작가 식별
CALL gds.degree.write('artist-graph', {
  writeProperty: 'degree_centrality'
})
YIELD nodePropertiesWritten, computeMillis;

// 3. PageRank (영향력 중심성)
// 네트워크 내 영향력 분석
CALL gds.pageRank.write('artist-graph', {
  maxIterations: 20,
  dampingFactor: 0.85,
  writeProperty: 'pagerank_score'
})
YIELD nodePropertiesWritten, computeMillis;

// 4. Betweenness Centrality (매개 중심성)
// 네트워크 허브 역할 작가 식별 (시간 소요 주의)
CALL gds.betweenness.write('artist-graph', {
  writeProperty: 'betweenness_centrality'
})
YIELD nodePropertiesWritten, computeMillis;

// 5. Eigenvector Centrality (고유벡터 중심성)
// 유력한 작가와 연결된 작가 식별
CALL gds.eigenvector.write('artist-graph', {
  writeProperty: 'eigenvector_centrality'
})
YIELD nodePropertiesWritten, computeMillis;

// 6. Louvain Community Detection (커뮤니티 탐지)
// 협업 그룹(Community) 식별 및 ID 부여
CALL gds.louvain.write('artist-graph', {
  writeProperty: 'community_id'
})
YIELD communityCount, modularity, computeMillis;

// 7. Graph Drop (메모리 해제)
CALL gds.graph.drop('artist-graph') YIELD graphName;
