// ========================================
// ARGO Neo4j Schema Initialization
// Version: 1.0.0 (MVP)
// ========================================

// === UNIQUE 제약조건 ===
CREATE CONSTRAINT artist_id_unique IF NOT EXISTS
FOR (a:Artist) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT institution_id_unique IF NOT EXISTS
FOR (i:Institution) REQUIRE i.id IS UNIQUE;

CREATE CONSTRAINT exhibition_id_unique IF NOT EXISTS
FOR (e:Exhibition) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT cluster_id_unique IF NOT EXISTS
FOR (c:Cluster) REQUIRE c.id IS UNIQUE;

// Phase 2용 (미리 생성해도 무방)
CREATE CONSTRAINT artwork_id_unique IF NOT EXISTS
FOR (w:Artwork) REQUIRE w.id IS UNIQUE;

CREATE CONSTRAINT transaction_id_unique IF NOT EXISTS
FOR (t:Transaction) REQUIRE t.id IS UNIQUE;

// === 성능 인덱스 ===
CREATE INDEX artist_composite_score IF NOT EXISTS
FOR (a:Artist) ON (a.composite_score);

CREATE INDEX artist_segment IF NOT EXISTS
FOR (a:Artist) ON (a.segment_id);

CREATE INDEX artist_field_quadrant IF NOT EXISTS
FOR (a:Artist) ON (a.field_quadrant);

CREATE INDEX artist_community IF NOT EXISTS
FOR (a:Artist) ON (a.community_id);

CREATE INDEX institution_type IF NOT EXISTS
FOR (i:Institution) ON (i.type);

CREATE INDEX institution_prestige IF NOT EXISTS
FOR (i:Institution) ON (i.prestige_score);

CREATE INDEX exhibition_year IF NOT EXISTS
FOR (e:Exhibition) ON (e.year);

CREATE INDEX exhibition_type IF NOT EXISTS
FOR (e:Exhibition) ON (e.type);

// === Fulltext 인덱스 (검색용) ===
CREATE FULLTEXT INDEX artist_name_search IF NOT EXISTS
FOR (a:Artist) ON EACH [a.name, a.name_ko, a.alternateName];

CREATE FULLTEXT INDEX institution_name_search IF NOT EXISTS
FOR (i:Institution) ON EACH [i.name, i.name_en];

CREATE FULLTEXT INDEX exhibition_title_search IF NOT EXISTS
FOR (e:Exhibition) ON EACH [e.title];

