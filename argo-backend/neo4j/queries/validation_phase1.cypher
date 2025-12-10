// ========================================
// Phase 1 Validation: 노드 카운트 검증
// Pass Criteria: 모든 노드 타입이 최소 요건 충족
// Version: 1.0
// Date: 2025-12-10
// ========================================

// === 1. 노드 타입별 카운트 ===
MATCH (a:Artist) WITH count(a) AS artist_count
MATCH (i:Institution) WITH artist_count, count(i) AS inst_count
MATCH (e:Exhibition) WITH artist_count, inst_count, count(e) AS exh_count
MATCH (w:Artwork) WITH artist_count, inst_count, exh_count, count(w) AS artwork_count
MATCH (p:Publication) WITH artist_count, inst_count, exh_count, artwork_count, count(p) AS pub_count
RETURN
    artist_count AS 'Artist Count',
    inst_count AS 'Institution Count',
    exh_count AS 'Exhibition Count',
    artwork_count AS 'Artwork Count',
    pub_count AS 'Publication Count',
    artist_count + inst_count + exh_count + artwork_count + pub_count AS 'Total Nodes';


// === 2. Pass/Fail 판정 ===
// 최소 요건: Artist >= 100, Institution >= 25, Exhibition >= 50, Artwork >= 200, Publication >= 100
MATCH (a:Artist) WITH count(a) AS artist_count
MATCH (i:Institution) WITH artist_count, count(i) AS inst_count
MATCH (e:Exhibition) WITH artist_count, inst_count, count(e) AS exh_count
MATCH (w:Artwork) WITH artist_count, inst_count, exh_count, count(w) AS artwork_count
MATCH (p:Publication) WITH artist_count, inst_count, exh_count, artwork_count, count(p) AS pub_count
RETURN
    CASE WHEN artist_count >= 100 THEN 'PASS' ELSE 'FAIL (' + toString(artist_count) + '/100)' END AS artist_pass,
    CASE WHEN inst_count >= 25 THEN 'PASS' ELSE 'FAIL (' + toString(inst_count) + '/25)' END AS inst_pass,
    CASE WHEN exh_count >= 50 THEN 'PASS' ELSE 'FAIL (' + toString(exh_count) + '/50)' END AS exh_pass,
    CASE WHEN artwork_count >= 200 THEN 'PASS' ELSE 'FAIL (' + toString(artwork_count) + '/200)' END AS artwork_pass,
    CASE WHEN pub_count >= 100 THEN 'PASS' ELSE 'FAIL (' + toString(pub_count) + '/100)' END AS pub_pass,
    CASE WHEN artist_count >= 100 AND inst_count >= 25 AND exh_count >= 50 AND artwork_count >= 200 AND pub_count >= 100
         THEN 'PHASE 1 COMPLETE'
         ELSE 'PHASE 1 INCOMPLETE'
    END AS overall_status;


// === 3. Artist 노드 품질 검증 ===
// 필수 필드 존재 여부 확인
MATCH (a:Artist)
WITH count(a) AS total,
     sum(CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END) AS has_id,
     sum(CASE WHEN a.name IS NOT NULL THEN 1 ELSE 0 END) AS has_name,
     sum(CASE WHEN a.segment_id IS NOT NULL THEN 1 ELSE 0 END) AS has_segment,
     sum(CASE WHEN a.inst_score IS NOT NULL THEN 1 ELSE 0 END) AS has_inst_score
RETURN
    total AS total_artists,
    has_id AS with_id,
    has_name AS with_name,
    has_segment AS with_segment_id,
    has_inst_score AS with_inst_score,
    round(toFloat(has_inst_score) / total * 100, 1) AS score_coverage_pct;


// === 4. Institution 노드 품질 검증 ===
MATCH (i:Institution)
WITH count(i) AS total,
     sum(CASE WHEN i.id IS NOT NULL THEN 1 ELSE 0 END) AS has_id,
     sum(CASE WHEN i.name IS NOT NULL THEN 1 ELSE 0 END) AS has_name,
     sum(CASE WHEN i.type IS NOT NULL THEN 1 ELSE 0 END) AS has_type
RETURN
    total AS total_institutions,
    has_id AS with_id,
    has_name AS with_name,
    has_type AS with_type;


// === 5. Artwork 노드 품질 검증 ===
MATCH (w:Artwork)
WITH count(w) AS total,
     sum(CASE WHEN w.id IS NOT NULL THEN 1 ELSE 0 END) AS has_id,
     sum(CASE WHEN w.title IS NOT NULL THEN 1 ELSE 0 END) AS has_title,
     sum(CASE WHEN w.artist_name IS NOT NULL THEN 1 ELSE 0 END) AS has_artist
RETURN
    total AS total_artworks,
    has_id AS with_id,
    has_title AS with_title,
    has_artist AS with_artist_name;


// === 6. Publication 노드 품질 검증 ===
MATCH (p:Publication)
WITH count(p) AS total,
     sum(CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END) AS has_id,
     sum(CASE WHEN p.title IS NOT NULL THEN 1 ELSE 0 END) AS has_title,
     sum(CASE WHEN p.authors IS NOT NULL AND size(p.authors) > 0 THEN 1 ELSE 0 END) AS has_authors
RETURN
    total AS total_publications,
    has_id AS with_id,
    has_title AS with_title,
    has_authors AS with_authors;


// === 7. 중복 ID 검증 ===
// 중복 ID가 있으면 문제
MATCH (a:Artist)
WITH a.id AS id, count(*) AS cnt
WHERE cnt > 1
RETURN 'Artist' AS type, id, cnt AS duplicate_count
UNION ALL
MATCH (w:Artwork)
WITH w.id AS id, count(*) AS cnt
WHERE cnt > 1
RETURN 'Artwork' AS type, id, cnt AS duplicate_count
UNION ALL
MATCH (p:Publication)
WITH p.id AS id, count(*) AS cnt
WHERE cnt > 1
RETURN 'Publication' AS type, id, cnt AS duplicate_count;
