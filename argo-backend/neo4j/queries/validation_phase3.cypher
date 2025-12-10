// ========================================
// Phase 3 Validation: GDS 분석 결과 검증
// Pass Criteria: network_score, community_id, Cluster 존재
// Version: 1.0
// Date: 2025-12-10
// ========================================

// === 1. Centrality 지표 분포 확인 ===
MATCH (a:Artist)
WHERE a.degree_centrality IS NOT NULL
WITH a
RETURN
    count(a) AS artists_with_centrality,
    round(avg(a.degree_centrality), 4) AS avg_degree,
    round(avg(a.betweenness_centrality), 4) AS avg_betweenness,
    round(avg(a.eigenvector_centrality), 4) AS avg_eigenvector,
    round(max(a.degree_centrality), 4) AS max_degree,
    round(max(a.betweenness_centrality), 4) AS max_betweenness;


// === 2. network_score 분포 확인 ===
MATCH (a:Artist)
WHERE a.network_score IS NOT NULL
WITH a.network_score AS score
RETURN
    count(score) AS artists_with_network_score,
    round(avg(score), 2) AS avg_network_score,
    round(min(score), 2) AS min_score,
    round(max(score), 2) AS max_score,
    percentileDisc(collect(score), 0.5) AS median_score;


// === 3. network_score 분포 히스토그램 ===
MATCH (a:Artist)
WHERE a.network_score IS NOT NULL
WITH a.network_score AS score
RETURN
    '0-20' AS range,
    count(CASE WHEN score < 20 THEN 1 END) AS count
UNION ALL
MATCH (a:Artist)
WHERE a.network_score IS NOT NULL
WITH a.network_score AS score
RETURN
    '20-40' AS range,
    count(CASE WHEN score >= 20 AND score < 40 THEN 1 END) AS count
UNION ALL
MATCH (a:Artist)
WHERE a.network_score IS NOT NULL
WITH a.network_score AS score
RETURN
    '40-60' AS range,
    count(CASE WHEN score >= 40 AND score < 60 THEN 1 END) AS count
UNION ALL
MATCH (a:Artist)
WHERE a.network_score IS NOT NULL
WITH a.network_score AS score
RETURN
    '60-80' AS range,
    count(CASE WHEN score >= 60 AND score < 80 THEN 1 END) AS count
UNION ALL
MATCH (a:Artist)
WHERE a.network_score IS NOT NULL
WITH a.network_score AS score
RETURN
    '80-100' AS range,
    count(CASE WHEN score >= 80 THEN 1 END) AS count;


// === 4. community_id 분포 ===
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
WITH a.community_id AS cid, count(*) AS member_count
RETURN
    count(cid) AS community_count,
    sum(member_count) AS total_assigned,
    round(avg(member_count), 2) AS avg_community_size,
    min(member_count) AS min_size,
    max(member_count) AS max_size;


// === 5. Cluster 노드 확인 ===
MATCH (c:Cluster)
RETURN
    count(c) AS cluster_count,
    collect(c.name) AS cluster_names;


// === 6. BELONGS_TO 관계 확인 ===
MATCH ()-[r:BELONGS_TO]->()
RETURN count(r) AS belongs_to_count;


// === 7. Cluster 품질 검증 ===
MATCH (c:Cluster)
OPTIONAL MATCH (c)<-[:BELONGS_TO]-(a:Artist)
WITH c, count(a) AS actual_members
RETURN
    c.id AS cluster_id,
    c.name AS cluster_name,
    c.artist_count AS stored_count,
    actual_members AS actual_count,
    CASE WHEN c.artist_count = actual_members THEN 'MATCH' ELSE 'MISMATCH' END AS count_status;


// === 8. Pass/Fail 판정 ===
MATCH (a:Artist) WHERE a.network_score IS NOT NULL WITH count(a) AS net_count
MATCH (a:Artist) WITH net_count, count(a) AS total_artists
MATCH (c:Cluster) WITH net_count, total_artists, count(c) AS cluster_count
MATCH ()-[r:BELONGS_TO]->() WITH net_count, total_artists, cluster_count, count(r) AS belongs_count
RETURN
    CASE WHEN toFloat(net_count) / total_artists >= 0.5 THEN 'PASS' ELSE 'FAIL (' + toString(net_count) + '/' + toString(total_artists) + ')' END AS network_score_pass,
    CASE WHEN cluster_count >= 3 THEN 'PASS' ELSE 'FAIL (' + toString(cluster_count) + '/3)' END AS cluster_pass,
    CASE WHEN belongs_count >= 50 THEN 'PASS' ELSE 'FAIL (' + toString(belongs_count) + '/50)' END AS belongs_pass,
    CASE
        WHEN toFloat(net_count) / total_artists >= 0.5 AND cluster_count >= 3 AND belongs_count >= 50
        THEN 'PHASE 3 COMPLETE'
        ELSE 'PHASE 3 INCOMPLETE'
    END AS overall_status;


// === 9. GDS 실행 상태 메타데이터 ===
MATCH (a:Artist)
WHERE a.network_score_computed_at IS NOT NULL
WITH a.network_score_computed_at AS computed_at
ORDER BY computed_at DESC
LIMIT 1
RETURN
    'GDS Analysis' AS process,
    computed_at AS last_executed,
    'network_score, community_id' AS properties_computed;


// === 10. 커뮤니티별 상위 Artist ===
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
WITH a.community_id AS cid, a
ORDER BY a.composite_score DESC
WITH cid, collect(a.name)[0..3] AS top_artists
RETURN cid AS community, top_artists
ORDER BY cid;
