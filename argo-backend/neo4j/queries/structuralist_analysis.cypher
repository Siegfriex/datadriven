// ========================================
// Structuralist Analysis Calculations
// ========================================

// === 1. Capital Composition 계산 ===
MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
  AND a.acad_score IS NOT NULL
  AND a.media_score IS NOT NULL
  AND a.network_score IS NOT NULL
WITH a,
     (a.inst_score + a.acad_score + a.media_score + a.network_score) AS total
WHERE total > 0
SET a.capital_composition = {
  institutional: round(a.inst_score / total, 4),
  academic: round(a.acad_score / total, 4),
  media: round(a.media_score / total, 4),
  network: round(a.network_score / total, 4)
}
RETURN count(a) AS updated_artists;

// === 2. Dominant Capital 결정 ===
MATCH (a:Artist)
WHERE a.capital_composition IS NOT NULL
WITH a,
     a.capital_composition.institutional AS inst_ratio,
     a.capital_composition.academic AS acad_ratio,
     a.capital_composition.media AS media_ratio,
     a.capital_composition.network AS network_ratio
SET a.dominant_capital =
  CASE
    WHEN inst_ratio >= acad_ratio AND inst_ratio >= media_ratio AND inst_ratio >= network_ratio
      THEN 'institutional'
    WHEN acad_ratio >= inst_ratio AND acad_ratio >= media_ratio AND acad_ratio >= network_ratio
      THEN 'academic'
    WHEN media_ratio >= inst_ratio AND media_ratio >= acad_ratio AND media_ratio >= network_ratio
      THEN 'media'
    ELSE 'network'
  END
RETURN count(a) AS updated_artists;

// === 3. Field Quadrant 분류 ===
// 먼저 중앙값 계산
MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL AND a.acad_score IS NOT NULL
WITH percentileDisc(a.inst_score, 0.5) AS inst_median,
     percentileDisc(a.acad_score, 0.5) AS acad_median

MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL AND a.acad_score IS NOT NULL
SET a.field_quadrant =
  CASE
    WHEN a.inst_score >= inst_median AND a.acad_score >= acad_median
      THEN 'Q1_established'
    WHEN a.inst_score < inst_median AND a.acad_score >= acad_median
      THEN 'Q2_academic_elite'
    WHEN a.inst_score >= inst_median AND a.acad_score < acad_median
      THEN 'Q3_media_star'
    ELSE 'Q4_emerging'
  END
RETURN count(a) AS updated_artists;

// === 4. 3D Coordinates 계산 (coordinates_3d 객체로 저장) ===
// 주의: Neo4j에서 datetime() 함수는 ISO 형식 문자열로 변환 필요
// Python에서 계산된 좌표를 사용하거나, 여기서는 기본 계산만 수행
MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
  AND a.acad_score IS NOT NULL
  AND a.media_score IS NOT NULL
  AND a.network_score IS NOT NULL
WITH a,
     round((a.inst_score - 50) * 0.6, 2) AS x,
     round((a.acad_score - 50) * 0.6, 2) AS y,
     round((a.media_score - 50) * 0.6, 2) AS z,
     round(10.0 + (a.network_score / 5.0), 2) AS radius
SET a.coordinates_3d = {
  x: x,
  y: y,
  z: z,
  radius: radius,
  computed_at: toString(datetime()),
  algorithm: 'normalize_v1'
}
RETURN count(a) AS updated_artists;

// === 5. Network Score 업데이트 (GDS 중심성 기반) ===
MATCH (a:Artist)
WHERE a.degree_centrality IS NOT NULL
  AND a.betweenness_centrality IS NOT NULL
  AND a.eigenvector_centrality IS NOT NULL
WITH a,
     // 정규화된 중심성 가중 평균
     (a.degree_centrality * 0.25 +
      a.betweenness_centrality * 0.35 +
      a.eigenvector_centrality * 0.40) * 100 AS raw_network_score
SET a.network_score = round(CASE
  WHEN raw_network_score > 100 THEN 100
  WHEN raw_network_score < 0 THEN 0
  ELSE raw_network_score
END, 2)
RETURN count(a) AS updated_artists;

