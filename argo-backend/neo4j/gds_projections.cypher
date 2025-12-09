// ========================================
// GDS Graph Projections & Algorithms
// ========================================

// === 1. 협업 네트워크 프로젝션 ===
// 기존 프로젝션이 있으면 삭제 후 재생성
CALL gds.graph.drop('artist-collaboration-graph', false) YIELD graphName;

CALL gds.graph.project(
  'artist-collaboration-graph',
  'Artist',
  {
    COLLABORATED_WITH: {
      type: 'COLLABORATED_WITH',
      orientation: 'UNDIRECTED',
      properties: ['strength']
    }
  },
  {
    nodeProperties: ['composite_score', 'inst_score', 'acad_score', 'network_score']
  }
) YIELD graphName, nodeCount, relationshipCount;

// === 2. Degree Centrality ===
CALL gds.degree.write(
  'artist-collaboration-graph',
  {
    writeProperty: 'degree_centrality',
    relationshipWeightProperty: 'strength'
  }
) YIELD nodePropertiesWritten;

// === 3. Betweenness Centrality ===
CALL gds.betweenness.write(
  'artist-collaboration-graph',
  {
    writeProperty: 'betweenness_centrality'
  }
) YIELD nodePropertiesWritten;

// === 4. Eigenvector Centrality ===
CALL gds.eigenvector.write(
  'artist-collaboration-graph',
  {
    writeProperty: 'eigenvector_centrality',
    maxIterations: 100
  }
) YIELD nodePropertiesWritten;

// === 5. Louvain Community Detection ===
CALL gds.louvain.write(
  'artist-collaboration-graph',
  {
    writeProperty: 'community_id',
    relationshipWeightProperty: 'strength'
  }
) YIELD nodePropertiesWritten, communityCount;

// === 참고: 그래프 프로젝션 삭제 (필요시) ===
// CALL gds.graph.drop('artist-collaboration-graph');

