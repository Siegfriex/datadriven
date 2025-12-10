// ========================================
// File: 01_relationship_creation.cypher
// Purpose: 실데이터 기반 관계 생성 (APOC 활용)
// Prerequisite: 01_node_upload 완료
// Note: Publication 데이터가 부족한 경우를 대비한 대안 쿼리 포함
// ========================================

// 1. COLLABORATED_WITH (공동저자 기반)
// KCI Publication의 authors 배열을 활용하여 공동저자 관계 생성
// 주의: Publication.authors가 비어있으면 실행되지 않음
CALL apoc.periodic.iterate(
  "MATCH (p:Publication) WHERE size(p.authors) > 1 RETURN p",
  "UNWIND apoc.coll.combinations(p.authors, 2) AS pair
   MATCH (a1:Artist {name: pair[0]}), (a2:Artist {name: pair[1]})
   WHERE a1.id <> a2.id
   MERGE (a1)-[r:COLLABORATED_WITH]-(a2)
   ON CREATE SET 
     r.weight = 1, 
     r.publications = [p.id],
     r.first_year = p.publication_year,
     r.last_year = p.publication_year,
     r.created_at = datetime()
   ON MATCH SET 
     r.weight = r.weight + 1, 
     r.publications = r.publications + p.id,
     r.first_year = CASE WHEN p.publication_year < r.first_year THEN p.publication_year ELSE r.first_year END,
     r.last_year = CASE WHEN p.publication_year > r.last_year THEN p.publication_year ELSE r.last_year END,
     r.updated_at = datetime()",
  {batchSize: 500, parallel: false}
);

// 2. AFFILIATED_WITH (소속 기관 매칭)
// 대안 1: Publication의 publisher 정보 활용 (데이터 있을 경우)
CALL apoc.periodic.iterate(
  "MATCH (p:Publication), (a:Artist) 
   WHERE a.name IN p.authors AND p.publisher_ko IS NOT NULL 
   RETURN a, p",
  "MATCH (i:Institution) 
   WHERE i.name = p.publisher_ko OR i.name CONTAINS p.publisher_ko
   MERGE (a)-[r:AFFILIATED_WITH]->(i)
   ON CREATE SET
     r.source = 'KCI',
     r.role = 'researcher',
     r.year = p.publication_year,
     r.created_at = datetime()",
  {batchSize: 1000, parallel: false}
);

// 대안 2: Artist의 segment_id와 Institution 이름 기반 추론 관계 생성
// (Publication 데이터가 없을 때 사용)
// Institution 타입이 'arts_group'인 경우도 포함
MATCH (a:Artist)
WHERE a.segment_id IS NOT NULL
WITH a, a.segment_id AS seg_id
MATCH (i:Institution)
WHERE (
  i.type IN ['national_museum', 'biennale', 'university', 'gallery', 'arts_group'] OR
  i.name CONTAINS '미술' OR i.name CONTAINS '예술' OR i.name CONTAINS '아트'
)
MERGE (a)-[r:AFFILIATED_WITH]->(i)
ON CREATE SET
  r.source = 'inferred',
  r.role = 'member',
  r.inferred = true,
  r.created_at = datetime()
RETURN count(r) AS inferred_affiliations;

// 3. PARTICIPATED_IN (전시 참여)
// Biennale 데이터가 Artist Metadata에 있는 경우 (현재 구조상 별도 수집됨)
// 여기서는 별도 Exhibition 노드와 Artist 매칭 필요
// Exhibition 노드가 생성되어 있어야 함

// 4. DISPLAYED_IN (작품 전시)
// Artwork의 building_name이 Institution/Exhibition과 일치하는 경우
CALL apoc.periodic.iterate(
  "MATCH (w:Artwork) WHERE w.building_name IS NOT NULL RETURN w",
  "MATCH (i:Institution) WHERE i.name = w.building_name OR i.name CONTAINS w.building_name
   MERGE (w)-[r:DISPLAYED_IN]->(i)
   ON CREATE SET
     r.install_year = w.install_year,
     r.created_at = datetime()",
  {batchSize: 1000, parallel: false}
);
