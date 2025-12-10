// ========================================
// 3D Coordinates Update
// API Reference: GET /v1/api/galaxy-snapshot
// TSD Reference: coordinates_3d
// Version: 1.0
// Date: 2025-12-10
// ========================================

// === 1. 기본 3D 좌표 계산 ===
// 좌표 계산 공식 (Bourdieu Field Mapping):
// x = (inst_score - 50) * 0.6   // 범위: -30 ~ +30 (Institutional Capital)
// y = (acad_score - 50) * 0.6   // 범위: -30 ~ +30 (Academic Capital)
// z = (media_score - 50) * 0.6  // 범위: -30 ~ +30 (Media Capital)
// radius = 10 + (network_score / 5)  // 범위: 10 ~ 30 (Network Capital)

MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
SET a.coord_x = round((coalesce(a.inst_score, 50) - 50) * 0.6, 2),
    a.coord_y = round((coalesce(a.acad_score, 50) - 50) * 0.6, 2),
    a.coord_z = round((coalesce(a.media_score, 50) - 50) * 0.6, 2),
    a.coord_radius = round(10.0 + (coalesce(a.network_score, 0) / 5.0), 2),
    a.coord_computed_at = toString(datetime()),
    a.coord_algorithm = 'bourdieu_field_v1'
RETURN count(a) AS coordinates_updated;


// === 2. 좌표 정규화 (필요시) ===
// 전체 좌표를 -1 ~ 1 범위로 정규화

// MATCH (a:Artist)
// WHERE a.coord_x IS NOT NULL
// WITH max(abs(a.coord_x)) AS max_x,
//      max(abs(a.coord_y)) AS max_y,
//      max(abs(a.coord_z)) AS max_z
// MATCH (a:Artist)
// WHERE a.coord_x IS NOT NULL
// SET a.coord_x_norm = a.coord_x / max_x,
//     a.coord_y_norm = a.coord_y / max_y,
//     a.coord_z_norm = a.coord_z / max_z
// RETURN count(a) AS normalized;


// === 3. 색상 계산 (Field Quadrant 기반) ===
// 시각화용 색상 할당

MATCH (a:Artist)
WHERE a.field_quadrant IS NOT NULL
SET a.color_hex = CASE a.field_quadrant
    WHEN 'Q1_established' THEN '#FFD700'    // Gold - 원로/거장
    WHEN 'Q2_academic_elite' THEN '#4169E1' // Royal Blue - 학계 중심
    WHEN 'Q3_media_star' THEN '#FF6347'     // Tomato - 미디어 스타
    WHEN 'Q4_emerging' THEN '#32CD32'       // Lime Green - 신진 작가
    ELSE '#808080'                          // Gray - 미분류
END,
a.color_rgb = CASE a.field_quadrant
    WHEN 'Q1_established' THEN [255, 215, 0]
    WHEN 'Q2_academic_elite' THEN [65, 105, 225]
    WHEN 'Q3_media_star' THEN [255, 99, 71]
    WHEN 'Q4_emerging' THEN [50, 205, 50]
    ELSE [128, 128, 128]
END
RETURN count(a) AS colors_assigned;


// === 4. 투명도 계산 (composite_score 기반) ===
// 점수가 높을수록 불투명

MATCH (a:Artist)
WHERE a.composite_score IS NOT NULL
SET a.opacity = round(0.3 + (coalesce(a.composite_score, 0) / 100) * 0.7, 2)
// opacity 범위: 0.3 (최소) ~ 1.0 (최대)
RETURN count(a) AS opacity_calculated;


// === 5. 발광 강도 계산 (network_score 기반) ===
// 네트워크 영향력이 클수록 밝게 발광

MATCH (a:Artist)
WHERE a.network_score IS NOT NULL
SET a.glow_intensity = round(coalesce(a.network_score, 0) / 100, 2),
    a.glow_color = CASE
        WHEN a.network_score >= 80 THEN '#FFFFFF'  // 흰색 (최강)
        WHEN a.network_score >= 60 THEN '#FFFACD'  // 레몬시폰 (강)
        WHEN a.network_score >= 40 THEN '#FFEFD5'  // 파파야휩 (중)
        WHEN a.network_score >= 20 THEN '#FFE4B5'  // 모카신 (약)
        ELSE '#FFF8DC'                              // 콘실크 (최약)
    END
RETURN count(a) AS glow_calculated;


// === 6. Institution 좌표 계산 ===
// Institution도 3D 공간에 배치

MATCH (i:Institution)
SET i.coord_x = CASE i.type
    WHEN 'national_museum' THEN 20      // 오른쪽 (제도적)
    WHEN 'biennale' THEN 15
    WHEN 'university' THEN -10          // 왼쪽 (학술적)
    WHEN 'gallery' THEN 5
    ELSE 0
END,
i.coord_y = CASE i.type
    WHEN 'national_museum' THEN 15
    WHEN 'biennale' THEN 25
    WHEN 'university' THEN 20
    WHEN 'gallery' THEN -5
    ELSE 0
END,
i.coord_z = 0,  // 기관은 중앙 평면에 배치
i.coord_radius = 15,
i.color_hex = '#87CEEB',  // Sky Blue
i.coord_algorithm = 'institution_type_v1'
RETURN count(i) AS institutions_positioned;


// === 7. Exhibition 좌표 계산 ===
// Exhibition은 시간축(z)에 배치

MATCH (e:Exhibition)
WHERE e.year IS NOT NULL
SET e.coord_x = 0,
    e.coord_y = 0,
    e.coord_z = (e.year - 2020) * 5,  // 2020년 기준, 연도당 5 단위
    e.coord_radius = 8,
    e.color_hex = '#DDA0DD',  // Plum
    e.coord_algorithm = 'timeline_v1'
RETURN count(e) AS exhibitions_positioned;


// === 8. Cluster 중심점 시각화 좌표 ===
MATCH (c:Cluster)
SET c.coord_radius = 25,  // 클러스터는 더 크게
    c.color_hex = '#FFB6C1',  // Light Pink
    c.opacity = 0.3  // 반투명
RETURN count(c) AS clusters_styled;


// === 9. 좌표 검증 ===
MATCH (a:Artist)
WHERE a.coord_x IS NOT NULL
WITH count(a) AS with_coords,
     avg(a.coord_x) AS avg_x,
     avg(a.coord_y) AS avg_y,
     avg(a.coord_z) AS avg_z,
     min(a.coord_radius) AS min_radius,
     max(a.coord_radius) AS max_radius
RETURN with_coords AS artists_with_coordinates,
       round(avg_x, 2) AS avg_coord_x,
       round(avg_y, 2) AS avg_coord_y,
       round(avg_z, 2) AS avg_coord_z,
       min_radius,
       max_radius;


// === 10. Galaxy Snapshot 데이터 생성 ===
// API: GET /v1/api/galaxy-snapshot
// 전체 시각화 데이터 반환

MATCH (a:Artist)
WHERE a.coord_x IS NOT NULL
RETURN a.id AS id,
       a.name AS name,
       a.coord_x AS x,
       a.coord_y AS y,
       a.coord_z AS z,
       a.coord_radius AS radius,
       a.color_hex AS color,
       a.opacity AS opacity,
       a.glow_intensity AS glow,
       a.field_quadrant AS quadrant,
       a.dominant_capital AS dominant_capital,
       a.composite_score AS score
ORDER BY a.composite_score DESC
LIMIT 1000;
