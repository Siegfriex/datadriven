// ========================================
// Final Validation: 전체 시스템 검증
// ARGO MVP 배포 가능 여부 최종 판정
// Version: 1.0
// Date: 2025-12-10
// ========================================

// === 1. 노드 카운트 최종 ===
CALL {
    MATCH (a:Artist) RETURN 'Artist' AS type, count(a) AS cnt, 100 AS min_required
    UNION ALL
    MATCH (i:Institution) RETURN 'Institution' AS type, count(i) AS cnt, 25 AS min_required
    UNION ALL
    MATCH (e:Exhibition) RETURN 'Exhibition' AS type, count(e) AS cnt, 50 AS min_required
    UNION ALL
    MATCH (w:Artwork) RETURN 'Artwork' AS type, count(w) AS cnt, 200 AS min_required
    UNION ALL
    MATCH (p:Publication) RETURN 'Publication' AS type, count(p) AS cnt, 100 AS min_required
    UNION ALL
    MATCH (c:Cluster) RETURN 'Cluster' AS type, count(c) AS cnt, 3 AS min_required
}
RETURN type, cnt AS actual, min_required,
       CASE WHEN cnt >= min_required THEN 'PASS' ELSE 'FAIL' END AS status;


// === 2. 관계 카운트 최종 ===
CALL {
    MATCH ()-[r:COLLABORATED_WITH]->() RETURN 'COLLABORATED_WITH' AS type, count(r) AS cnt, 10 AS min_required
    UNION ALL
    MATCH ()-[r:AFFILIATED_WITH]->() RETURN 'AFFILIATED_WITH' AS type, count(r) AS cnt, 20 AS min_required
    UNION ALL
    MATCH ()-[r:PARTICIPATED_IN]->() RETURN 'PARTICIPATED_IN' AS type, count(r) AS cnt, 5 AS min_required
    UNION ALL
    MATCH ()-[r:BELONGS_TO]->() RETURN 'BELONGS_TO' AS type, count(r) AS cnt, 50 AS min_required
    UNION ALL
    MATCH ()-[r:CREATED]->() RETURN 'CREATED' AS type, count(r) AS cnt, 50 AS min_required
}
RETURN type, cnt AS actual, min_required,
       CASE WHEN cnt >= min_required THEN 'PASS' ELSE 'FAIL' END AS status;


// === 3. 구조주의 분석 필드 완성도 ===
MATCH (a:Artist)
WITH count(a) AS total,
     sum(CASE WHEN a.composite_score IS NOT NULL THEN 1 ELSE 0 END) AS has_composite,
     sum(CASE WHEN a.dominant_capital IS NOT NULL THEN 1 ELSE 0 END) AS has_dominant,
     sum(CASE WHEN a.field_quadrant IS NOT NULL THEN 1 ELSE 0 END) AS has_quadrant,
     sum(CASE WHEN a.coord_x IS NOT NULL THEN 1 ELSE 0 END) AS has_coords,
     sum(CASE WHEN a.network_score IS NOT NULL THEN 1 ELSE 0 END) AS has_network
RETURN
    total AS total_artists,
    has_composite AS with_composite_score,
    has_dominant AS with_dominant_capital,
    has_quadrant AS with_field_quadrant,
    has_coords AS with_coordinates,
    has_network AS with_network_score,
    round(toFloat(has_quadrant) / total * 100, 1) AS quadrant_coverage_pct,
    round(toFloat(has_coords) / total * 100, 1) AS coordinates_coverage_pct;


// === 4. Field Quadrant 분포 ===
MATCH (a:Artist)
WHERE a.field_quadrant IS NOT NULL
WITH a.field_quadrant AS quadrant, count(*) AS cnt
RETURN quadrant, cnt,
       round(toFloat(cnt) / sum(cnt) OVER () * 100, 1) AS percentage
ORDER BY cnt DESC;


// === 5. Dominant Capital 분포 ===
MATCH (a:Artist)
WHERE a.dominant_capital IS NOT NULL
WITH a.dominant_capital AS capital, count(*) AS cnt
RETURN capital, cnt,
       round(toFloat(cnt) / sum(cnt) OVER () * 100, 1) AS percentage
ORDER BY cnt DESC;


// === 6. Score 통계 ===
MATCH (a:Artist)
WHERE a.composite_score IS NOT NULL
RETURN
    round(avg(a.inst_score), 2) AS avg_inst,
    round(avg(a.acad_score), 2) AS avg_acad,
    round(avg(a.media_score), 2) AS avg_media,
    round(avg(a.network_score), 2) AS avg_network,
    round(avg(a.composite_score), 2) AS avg_composite;


// === 7. 좌표 범위 확인 ===
MATCH (a:Artist)
WHERE a.coord_x IS NOT NULL
RETURN
    round(min(a.coord_x), 2) AS min_x,
    round(max(a.coord_x), 2) AS max_x,
    round(min(a.coord_y), 2) AS min_y,
    round(max(a.coord_y), 2) AS max_y,
    round(min(a.coord_z), 2) AS min_z,
    round(max(a.coord_z), 2) AS max_z,
    round(min(a.coord_radius), 2) AS min_radius,
    round(max(a.coord_radius), 2) AS max_radius;


// === 8. API 준비 상태 체크 ===
// 각 주요 API가 필요로 하는 데이터 존재 여부

// GET /v1/api/artists
MATCH (a:Artist) WHERE a.composite_score IS NOT NULL WITH count(a) AS artists_ready

// GET /v1/api/artists/{id}/network
MATCH (a:Artist)-[:COLLABORATED_WITH]-() WITH count(DISTINCT a) AS networked_artists, artists_ready

// GET /v1/api/clusters
MATCH (c:Cluster) WITH count(c) AS clusters_ready, networked_artists, artists_ready

// GET /v1/api/analysis/field-quadrants
MATCH (a:Artist) WHERE a.field_quadrant IS NOT NULL
WITH count(a) AS quadrant_ready, clusters_ready, networked_artists, artists_ready

// GET /v1/api/galaxy-snapshot
MATCH (a:Artist) WHERE a.coord_x IS NOT NULL
WITH count(a) AS galaxy_ready, quadrant_ready, clusters_ready, networked_artists, artists_ready

RETURN
    artists_ready AS 'GET /artists ready',
    networked_artists AS 'GET /artists/{id}/network ready',
    clusters_ready AS 'GET /clusters ready',
    quadrant_ready AS 'GET /analysis/field-quadrants ready',
    galaxy_ready AS 'GET /galaxy-snapshot ready';


// === 9. 최종 MVP 준비 상태 ===
MATCH (a:Artist) WITH count(a) AS artist_cnt
MATCH (a:Artist) WHERE a.composite_score IS NOT NULL WITH artist_cnt, count(a) AS scored_cnt
MATCH (a:Artist) WHERE a.coord_x IS NOT NULL WITH artist_cnt, scored_cnt, count(a) AS coord_cnt
MATCH (a:Artist) WHERE a.field_quadrant IS NOT NULL WITH artist_cnt, scored_cnt, coord_cnt, count(a) AS quad_cnt
MATCH ()-[r:COLLABORATED_WITH]->() WITH artist_cnt, scored_cnt, coord_cnt, quad_cnt, count(r) AS rel_cnt
MATCH (c:Cluster) WITH artist_cnt, scored_cnt, coord_cnt, quad_cnt, rel_cnt, count(c) AS cluster_cnt

WITH artist_cnt, scored_cnt, coord_cnt, quad_cnt, rel_cnt, cluster_cnt,
     CASE WHEN artist_cnt >= 100 THEN 1 ELSE 0 END +
     CASE WHEN toFloat(scored_cnt) / artist_cnt >= 0.8 THEN 1 ELSE 0 END +
     CASE WHEN toFloat(coord_cnt) / artist_cnt >= 0.9 THEN 1 ELSE 0 END +
     CASE WHEN toFloat(quad_cnt) / artist_cnt >= 0.8 THEN 1 ELSE 0 END +
     CASE WHEN rel_cnt >= 10 THEN 1 ELSE 0 END +
     CASE WHEN cluster_cnt >= 3 THEN 1 ELSE 0 END AS pass_count

RETURN
    artist_cnt AS total_artists,
    scored_cnt AS with_scores,
    coord_cnt AS with_coordinates,
    quad_cnt AS with_quadrant,
    rel_cnt AS relationships,
    cluster_cnt AS clusters,
    pass_count AS 'Criteria Passed (out of 6)',
    CASE
        WHEN pass_count = 6 THEN 'MVP READY - DEPLOY OK'
        WHEN pass_count >= 4 THEN 'MVP PARTIAL - REVIEW NEEDED'
        ELSE 'MVP NOT READY - MORE WORK REQUIRED'
    END AS deployment_status;


// === 10. 타임스탬프 ===
RETURN
    'ARGO Neo4j Final Validation' AS report,
    toString(datetime()) AS validated_at,
    'v1.0' AS schema_version;
