// ========================================
// Phase 2 Validation: 관계 무결성 검증
// Pass Criteria: 관계 존재 + 고아 관계 없음
// Version: 1.0
// Date: 2025-12-10
// ========================================

// === 1. 관계 타입별 카운트 ===
CALL {
    MATCH ()-[r:COLLABORATED_WITH]->() RETURN 'COLLABORATED_WITH' AS type, count(r) AS cnt
    UNION ALL
    MATCH ()-[r:AFFILIATED_WITH]->() RETURN 'AFFILIATED_WITH' AS type, count(r) AS cnt
    UNION ALL
    MATCH ()-[r:PARTICIPATED_IN]->() RETURN 'PARTICIPATED_IN' AS type, count(r) AS cnt
    UNION ALL
    MATCH ()-[r:DISPLAYED_IN]->() RETURN 'DISPLAYED_IN' AS type, count(r) AS cnt
    UNION ALL
    MATCH ()-[r:CREATED]->() RETURN 'CREATED' AS type, count(r) AS cnt
    UNION ALL
    MATCH ()-[r:AUTHORED]->() RETURN 'AUTHORED' AS type, count(r) AS cnt
}
RETURN type AS 'Relationship Type', cnt AS 'Count';


// === 2. Pass/Fail 판정 ===
MATCH ()-[r:COLLABORATED_WITH]->() WITH count(r) AS collab_count
MATCH ()-[r:AFFILIATED_WITH]->() WITH collab_count, count(r) AS affil_count
MATCH ()-[r:PARTICIPATED_IN]->() WITH collab_count, affil_count, count(r) AS partic_count
MATCH ()-[r:CREATED]->() WITH collab_count, affil_count, partic_count, count(r) AS created_count
RETURN
    CASE WHEN collab_count >= 10 THEN 'PASS' ELSE 'FAIL (' + toString(collab_count) + '/10)' END AS collaborated_pass,
    CASE WHEN affil_count >= 20 THEN 'PASS' ELSE 'FAIL (' + toString(affil_count) + '/20)' END AS affiliated_pass,
    CASE WHEN partic_count >= 5 THEN 'PASS' ELSE 'FAIL (' + toString(partic_count) + '/5)' END AS participated_pass,
    CASE WHEN created_count >= 50 THEN 'PASS' ELSE 'FAIL (' + toString(created_count) + '/50)' END AS created_pass,
    collab_count + affil_count + partic_count + created_count AS total_relations;


// === 3. 고아 관계 검증 ===
// 시작 또는 끝 노드가 없는 관계 (있으면 안됨)
MATCH ()-[r]->()
WHERE NOT exists(startNode(r)) OR NOT exists(endNode(r))
RETURN type(r) AS relationship_type, count(r) AS orphan_count;


// === 4. Artist당 평균 관계 수 ===
MATCH (a:Artist)
OPTIONAL MATCH (a)-[r]-()
WITH a, count(r) AS rel_count
RETURN
    count(a) AS total_artists,
    sum(rel_count) AS total_relationships,
    round(avg(rel_count), 2) AS avg_relations_per_artist,
    min(rel_count) AS min_relations,
    max(rel_count) AS max_relations,
    CASE WHEN avg(rel_count) >= 2.0 THEN 'PASS' ELSE 'FAIL' END AS avg_relations_pass;


// === 5. 연결되지 않은 Artist (고립 노드) ===
MATCH (a:Artist)
WHERE NOT (a)--()
RETURN a.id AS isolated_artist_id, a.name AS name
LIMIT 10;


// === 6. COLLABORATED_WITH 상세 검증 ===
// 양방향 관계 확인 (UNDIRECTED로 사용되어야 함)
MATCH (a:Artist)-[r:COLLABORATED_WITH]->(b:Artist)
WITH a, b, count(r) AS forward_count
OPTIONAL MATCH (b)-[r2:COLLABORATED_WITH]->(a)
WITH a, b, forward_count, count(r2) AS backward_count
WHERE forward_count > 0 AND backward_count = 0
RETURN a.name AS artist1, b.name AS artist2, 'Missing reverse relation' AS issue
LIMIT 5;


// === 7. 관계 속성 완성도 ===
MATCH ()-[r:COLLABORATED_WITH]->()
WITH count(r) AS total,
     sum(CASE WHEN r.strength IS NOT NULL THEN 1 ELSE 0 END) AS has_strength,
     sum(CASE WHEN r.collaboration_type IS NOT NULL THEN 1 ELSE 0 END) AS has_type
RETURN
    'COLLABORATED_WITH' AS relationship,
    total,
    has_strength AS with_strength,
    has_type AS with_collaboration_type,
    round(toFloat(has_strength) / total * 100, 1) AS strength_coverage_pct;


// === 8. AFFILIATED_WITH 검증 ===
MATCH (a:Artist)-[r:AFFILIATED_WITH]->(i:Institution)
WITH count(r) AS total,
     count(DISTINCT a) AS unique_artists,
     count(DISTINCT i) AS unique_institutions
RETURN
    total AS total_affiliations,
    unique_artists AS affiliated_artists,
    unique_institutions AS involved_institutions,
    round(toFloat(total) / unique_artists, 2) AS avg_affiliations_per_artist;


// === 9. 종합 상태 ===
MATCH ()-[r:COLLABORATED_WITH]->() WITH count(r) AS collab
MATCH ()-[r:AFFILIATED_WITH]->() WITH collab, count(r) AS affil
MATCH ()-[r:PARTICIPATED_IN]->() WITH collab, affil, count(r) AS partic
MATCH (a:Artist) WHERE NOT (a)--() WITH collab, affil, partic, count(a) AS isolated
RETURN
    CASE
        WHEN collab >= 10 AND affil >= 20 AND partic >= 5 AND isolated = 0
        THEN 'PHASE 2 COMPLETE'
        ELSE 'PHASE 2 INCOMPLETE'
    END AS overall_status,
    collab AS collaborated_count,
    affil AS affiliated_count,
    partic AS participated_count,
    isolated AS isolated_artists;
