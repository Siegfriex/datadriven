// ========================================
// File: 02_cluster_creation.cypher
// Purpose: GDS 분석 결과(Louvain) 기반 Cluster 노드 생성
// Prerequisite: GDS Louvain 실행 완료 (community_id 생성됨)
// ========================================

// 1. 기존 Cluster 삭제 (재실행 시)
// MATCH (c:Cluster) DETACH DELETE c;

// 2. Cluster 노드 생성
// community_id 별로 그룹화하여 Cluster 노드 생성
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
WITH a.community_id AS cid, collect(a) AS members, count(a) AS size
WHERE size > 1  // 2명 이상인 그룹만 클러스터로 인정
MERGE (c:Cluster {id: 'cluster_' + toString(cid)})
ON CREATE SET
  c.community_id = cid,
  c.size = size,
  c.type = 'louvain',
  c.created_at = datetime()
ON MATCH SET
  c.size = size,
  c.updated_at = datetime();

// 3. BELONGS_TO 관계 생성
// Artist -> Cluster 연결
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
MATCH (c:Cluster {community_id: a.community_id})
MERGE (a)-[r:BELONGS_TO]->(c)
ON CREATE SET
  r.membership_strength = 1.0;

// 4. Cluster 속성 업데이트 (중심점 계산 등)
// 클러스터 내 멤버들의 평균 좌표 등을 계산하여 클러스터 속성으로 저장 가능 (추후 구현)
