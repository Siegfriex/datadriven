// ========================================
// File: 00_cleanup.cypher
// Purpose: 데이터 초기화 및 롤백 스크립트
// Warning: 실행 시 모든 데이터가 삭제됩니다. 운영 환경 주의.
// ========================================

// 1. 전체 데이터 삭제 (선택적 실행)
// MATCH (n) DETACH DELETE n;

// 2. 특정 노드 타입만 삭제 (롤백용)
// MATCH (a:Artist) DETACH DELETE a;
// MATCH (w:Artwork) DETACH DELETE w;
// MATCH (p:Publication) DETACH DELETE p;
// MATCH (c:Cluster) DETACH DELETE c;

// 3. 제약조건 확인 및 재생성 (APOC 활용)
// CALL apoc.schema.assert(
//   {
//     Artist:['id'],
//     Institution:['id'],
//     Exhibition:['id'],
//     Artwork:['id'],
//     Cluster:['id']
//   },
//   {
//     Artist:['name'],
//     Artwork:['title']
//   }
// );

// 4. 고아 관계(Orphan Relationship) 삭제
// 시작 노드나 끝 노드가 없는 관계 삭제
MATCH ()-[r]->()
WHERE NOT EXISTS((startNode(r))) OR NOT EXISTS((endNode(r)))
DELETE r;

// 5. 고립 노드(Isolated Node) 확인 (검증용)
MATCH (n)
WHERE NOT (n)--()
RETURN labels(n) as label, count(n) as isolated_count;

