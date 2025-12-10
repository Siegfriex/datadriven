// ========================================
// ARGO API Query Templates
// API Reference: ARGO_API_COMPLETE_SPECIFICATION.md Part I
// Usage: API 라우터에서 파라미터화하여 사용
// Version: 1.0
// Date: 2025-12-10
// ========================================

// ============================================================
// ARTISTS ENDPOINTS
// ============================================================

// === GET /v1/api/artists ===
// Parameters: $skip, $limit, $segment_id, $min_score, $genre
MATCH (a:Artist)
WHERE ($segment_id IS NULL OR a.segment_id = $segment_id)
  AND ($min_score IS NULL OR a.composite_score >= $min_score)
  AND ($genre IS NULL OR a.genre = $genre)
RETURN a {
    .id, .name, .alternateName, .segment_id, .genre,
    .inst_score, .acad_score, .media_score, .network_score,
    .composite_score, .composite_confidence,
    .coord_x, .coord_y, .coord_z, .coord_radius,
    .dominant_capital, .field_quadrant, .color_hex
}
ORDER BY a.composite_score DESC
SKIP $skip
LIMIT $limit;


// === GET /v1/api/artists/{artist_id} ===
// Parameters: $artist_id
MATCH (a:Artist {id: $artist_id})
OPTIONAL MATCH (a)-[collab:COLLABORATED_WITH]-(peer:Artist)
OPTIONAL MATCH (a)-[affil:AFFILIATED_WITH]->(inst:Institution)
OPTIONAL MATCH (a)-[belong:BELONGS_TO]->(cluster:Cluster)
OPTIONAL MATCH (a)-[created:CREATED]->(artwork:Artwork)
RETURN {
    artist: a {.*},
    collaborators: collect(DISTINCT {
        id: peer.id,
        name: peer.name,
        strength: collab.strength,
        collaboration_type: collab.collaboration_type
    })[0..10],
    institutions: collect(DISTINCT {
        id: inst.id,
        name: inst.name,
        role: affil.role
    }),
    cluster: cluster {.id, .name, .cluster_type, .artist_count},
    artworks_count: count(DISTINCT artwork)
} AS result;


// === GET /v1/api/artists/{artist_id}/network ===
// Parameters: $artist_id, $depth (default: 1)
MATCH (center:Artist {id: $artist_id})
OPTIONAL MATCH path = (center)-[:COLLABORATED_WITH*1..2]-(neighbor:Artist)
WHERE neighbor.id <> center.id
WITH center, neighbor, relationships(path) AS rels, length(path) AS depth
WITH center, neighbor, head(rels) AS first_rel, depth
ORDER BY depth, first_rel.strength DESC
WITH center, collect(DISTINCT {
    node: neighbor {.id, .name, .composite_score, .coord_x, .coord_y, .coord_z},
    edge: {strength: first_rel.strength, collaboration_type: first_rel.collaboration_type},
    depth: depth
})[0..50] AS connections
RETURN {
    center: center {.id, .name, .composite_score, .coord_x, .coord_y, .coord_z},
    nodes: connections,
    total_connections: size(connections)
} AS network;


// === GET /v1/api/artists/{artist_id}/capital-composition ===
// Parameters: $artist_id
MATCH (a:Artist {id: $artist_id})
WHERE a.capital_inst_ratio IS NOT NULL
RETURN {
    artist_id: a.id,
    artist_name: a.name,
    capital_composition: {
        institutional: a.capital_inst_ratio,
        academic: a.capital_acad_ratio,
        media: a.capital_media_ratio,
        network: a.capital_network_ratio
    },
    dominant_capital: a.dominant_capital,
    field_quadrant: a.field_quadrant,
    composite_score: a.composite_score
} AS capital;


// === GET /v1/api/artists/{artist_id}/structural-equivalents ===
// Bourdieu Structural Equivalence (Manhattan Distance)
// Parameters: $artist_id, $limit (default: 10)
MATCH (target:Artist {id: $artist_id})
WHERE target.capital_inst_ratio IS NOT NULL
MATCH (other:Artist)
WHERE other.id <> target.id
  AND other.capital_inst_ratio IS NOT NULL
WITH target, other,
     abs(target.capital_inst_ratio - other.capital_inst_ratio) +
     abs(target.capital_acad_ratio - other.capital_acad_ratio) +
     abs(target.capital_media_ratio - other.capital_media_ratio) +
     abs(target.capital_network_ratio - other.capital_network_ratio) AS distance
WHERE distance < 0.50
RETURN {
    artist: other {.id, .name, .dominant_capital, .field_quadrant, .composite_score},
    distance: round(distance, 4),
    same_quadrant: other.field_quadrant = target.field_quadrant
} AS equivalent
ORDER BY distance ASC
LIMIT $limit;


// === GET /v1/api/artists/{artist_id}/trajectory ===
// 작가의 자본 변화 궤적 (시계열)
// Parameters: $artist_id
MATCH (a:Artist {id: $artist_id})
OPTIONAL MATCH (a)-[:PARTICIPATED_IN]->(e:Exhibition)
WITH a, e ORDER BY e.year
RETURN {
    artist: a {.id, .name},
    current_position: {
        x: a.coord_x,
        y: a.coord_y,
        z: a.coord_z
    },
    exhibitions_timeline: collect({
        year: e.year,
        exhibition: e.name,
        type: e.type
    })
} AS trajectory;


// ============================================================
// INSTITUTIONS ENDPOINTS
// ============================================================

// === GET /v1/api/institutions ===
// Parameters: $skip, $limit, $type
MATCH (i:Institution)
WHERE ($type IS NULL OR i.type = $type)
OPTIONAL MATCH (i)<-[:AFFILIATED_WITH]-(a:Artist)
WITH i, count(a) AS affiliated_count
RETURN i {
    .id, .name, .type, .location, .established_year,
    .coord_x, .coord_y, .coord_z,
    affiliated_artists: affiliated_count
}
ORDER BY affiliated_count DESC
SKIP $skip
LIMIT $limit;


// === GET /v1/api/institutions/{inst_id}/affiliated-artists ===
// Parameters: $inst_id, $skip, $limit
MATCH (i:Institution {id: $inst_id})
OPTIONAL MATCH (i)<-[r:AFFILIATED_WITH]-(a:Artist)
WITH i, a, r
ORDER BY a.composite_score DESC
RETURN {
    institution: i {.id, .name, .type},
    artists: collect({
        id: a.id,
        name: a.name,
        role: r.role,
        composite_score: a.composite_score
    })[$skip..($skip + $limit)]
} AS result;


// ============================================================
// EXHIBITIONS ENDPOINTS
// ============================================================

// === GET /v1/api/exhibitions ===
// Parameters: $skip, $limit, $type, $year_from, $year_to
MATCH (e:Exhibition)
WHERE ($type IS NULL OR e.type = $type)
  AND ($year_from IS NULL OR e.year >= $year_from)
  AND ($year_to IS NULL OR e.year <= $year_to)
OPTIONAL MATCH (a:Artist)-[:PARTICIPATED_IN]->(e)
WITH e, count(a) AS participant_count
RETURN e {
    .id, .name, .type, .year, .location, .start_date, .end_date,
    .coord_x, .coord_y, .coord_z,
    participants: participant_count
}
ORDER BY e.year DESC, participant_count DESC
SKIP $skip
LIMIT $limit;


// === GET /v1/api/exhibitions/{exh_id} ===
// Parameters: $exh_id
MATCH (e:Exhibition {id: $exh_id})
OPTIONAL MATCH (a:Artist)-[r:PARTICIPATED_IN]->(e)
OPTIONAL MATCH (w:Artwork)-[:DISPLAYED_IN]->(e)
RETURN {
    exhibition: e {.*},
    participants: collect(DISTINCT {
        id: a.id,
        name: a.name,
        role: r.role
    }),
    artworks: collect(DISTINCT {
        id: w.id,
        title: w.title,
        medium: w.medium
    })[0..20]
} AS result;


// ============================================================
// CLUSTERS ENDPOINTS
// ============================================================

// === GET /v1/api/clusters ===
// Parameters: $skip, $limit
MATCH (c:Cluster)
OPTIONAL MATCH (c)<-[:BELONGS_TO]-(a:Artist)
WITH c, collect(a.id) AS member_ids, count(a) AS actual_count
RETURN c {
    .id, .name, .cluster_type, .dominant_genre, .dominant_capital,
    .avg_composite_score, .algorithm_version,
    .center_x, .center_y, .center_z,
    member_ids: member_ids[0..20],
    member_count: actual_count
}
ORDER BY actual_count DESC
SKIP $skip
LIMIT $limit;


// === GET /v1/api/clusters/{cluster_id} ===
// Parameters: $cluster_id
MATCH (c:Cluster {id: $cluster_id})
OPTIONAL MATCH (c)<-[r:BELONGS_TO]-(a:Artist)
WITH c, a, r
ORDER BY r.distance_to_center ASC
RETURN {
    cluster: c {.*},
    members: collect({
        id: a.id,
        name: a.name,
        composite_score: a.composite_score,
        distance_to_center: r.distance_to_center,
        dominant_capital: a.dominant_capital
    })
} AS result;


// ============================================================
// ANALYSIS ENDPOINTS
// ============================================================

// === GET /v1/api/analysis/field-quadrants ===
MATCH (a:Artist)
WHERE a.field_quadrant IS NOT NULL
WITH a.field_quadrant AS quadrant, collect(a) AS artists
RETURN {
    quadrant: quadrant,
    description: CASE quadrant
        WHEN 'Q1_established' THEN '원로/거장 - 고제도+고학술'
        WHEN 'Q2_academic_elite' THEN '학계 중심 - 저제도+고학술'
        WHEN 'Q3_media_star' THEN '미디어 스타 - 고제도+저학술'
        WHEN 'Q4_emerging' THEN '신진 작가 - 저제도+저학술'
        ELSE '미분류'
    END,
    artist_count: size(artists),
    avg_composite: round(avg([art IN artists | art.composite_score]), 2),
    sample_artists: [art IN artists | {id: art.id, name: art.name}][0..5]
} AS quadrant_stats
ORDER BY quadrant;


// === GET /v1/api/analysis/score-distribution ===
MATCH (a:Artist)
WHERE a.composite_score IS NOT NULL
WITH a.composite_score AS score
RETURN {
    total_artists: count(score),
    score_distribution: {
        '0-20': count(CASE WHEN score < 20 THEN 1 END),
        '20-40': count(CASE WHEN score >= 20 AND score < 40 THEN 1 END),
        '40-60': count(CASE WHEN score >= 40 AND score < 60 THEN 1 END),
        '60-80': count(CASE WHEN score >= 60 AND score < 80 THEN 1 END),
        '80-100': count(CASE WHEN score >= 80 THEN 1 END)
    },
    statistics: {
        min: min(score),
        max: max(score),
        avg: round(avg(score), 2),
        median: percentileDisc(collect(score), 0.5)
    }
} AS distribution;


// === GET /v1/api/galaxy-snapshot ===
// Galaxy 시각화용 전체 데이터
// Parameters: $limit (default: 1000)
MATCH (a:Artist)
WHERE a.coord_x IS NOT NULL
OPTIONAL MATCH (a)-[r:COLLABORATED_WITH]-(peer:Artist)
WITH a, count(r) AS connection_count
RETURN {
    id: a.id,
    name: a.name,
    position: {
        x: a.coord_x,
        y: a.coord_y,
        z: a.coord_z
    },
    visual: {
        radius: a.coord_radius,
        color: a.color_hex,
        opacity: a.opacity,
        glow_intensity: a.glow_intensity
    },
    data: {
        composite_score: a.composite_score,
        dominant_capital: a.dominant_capital,
        field_quadrant: a.field_quadrant,
        connections: connection_count
    }
} AS node
ORDER BY a.composite_score DESC
LIMIT $limit;


// === POST /v1/api/analysis/calculate-structuralist ===
// (실행 쿼리 - 결과 반환용)
MATCH (a:Artist)
WHERE a.composite_score IS NOT NULL
WITH count(a) AS total,
     sum(CASE WHEN a.dominant_capital IS NOT NULL THEN 1 ELSE 0 END) AS with_dominant,
     sum(CASE WHEN a.field_quadrant IS NOT NULL THEN 1 ELSE 0 END) AS with_quadrant
RETURN {
    status: 'completed',
    total_artists: total,
    with_dominant_capital: with_dominant,
    with_field_quadrant: with_quadrant,
    completion_rate: round(toFloat(with_quadrant) / total * 100, 1)
} AS result;


// ============================================================
// SEARCH ENDPOINTS
// ============================================================

// === GET /v1/api/search ===
// Full-text search across entities
// Parameters: $query, $type (artist|institution|exhibition), $limit
MATCH (n)
WHERE (n:Artist OR n:Institution OR n:Exhibition)
  AND ($type IS NULL OR labels(n)[0] = $type)
  AND (toLower(n.name) CONTAINS toLower($query)
       OR ($type = 'Artist' AND toLower(n.alternateName) CONTAINS toLower($query)))
RETURN {
    type: labels(n)[0],
    id: n.id,
    name: n.name,
    score: CASE WHEN n:Artist THEN n.composite_score ELSE null END
} AS result
ORDER BY result.score DESC NULLS LAST
LIMIT $limit;
