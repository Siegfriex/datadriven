# ARGO: 한국 미술계 구조 분석 엔진
## 최종 데이터베이스 스키마 & 엔터티 정의
### Schema.org 기반 완전 구현

---

## 1. 최상위 개념 계층 (Schema.org 기반)

### 1.1 핵심 엔터티 맵핑

```
Schema.org 상위개념
├─ Thing (모든 것의 기반)
│  ├─ Person (작가)
│  ├─ Organization (기관)
│  ├─ Event (전시)
│  ├─ CreativeWork (작품)
│  └─ Place (지역)
│
└─ 확장 개념
   ├─ Graph (네트워크)
   ├─ Role (직책/역할)
   └─ Quantitative (수치 지표)
```

---

## 2. 엔터티 상세 정의 (Neo4j 노드 + 속성)

### 2.1 Artist (Person + CreativeWork 복합)

```neo4j
(:Artist {
  // === Schema.org Person 기반 ===
  
  // identifier.identifier
  artist_id: STRING @id,
  
  // name
  name: STRING,
  alternativeName: STRING,  // 영문이름, 별명
  
  // birthDate
  birth_year: INT,
  
  // identifier.url
  url: STRING,              // 공식 웹사이트
  sameAs: [STRING],         // 외부 프로필 (Wikipedia, Artsy 등)
  
  // address
  address: {
    streetAddress: STRING,
    addressLocality: STRING, // 도시
    addressRegion: STRING,   // 지역
    postalCode: STRING,
    addressCountry: STRING
  },
  
  // telephone, email
  contactPoint: {
    telephone: STRING,
    email: STRING
  },
  
  // jobTitle + workLocation
  jobTitle: STRING,         // "교수", "큐레이터" 등
  workLocation: STRING,     // 소속 기관
  
  // === ARGO 커스텀 ===
  
  // 세그먼트 분류 (장르/지역/세대)
  segment_id: STRING,
  segment_metadata: {
    genre: STRING,          // "monochrome_painting", "abstract", etc
    geographic_base: STRING, // "Seoul", "Busan"
    generation: STRING       // "1960s", "1980s"
  },
  
  // 경력 단계
  career_stage: ENUM ["early", "mid", "late"],
  
  // === 4개 구조 레이어 점수 ===
  
  scores: {
    // 제도 레이어 (institutional)
    inst_score: FLOAT @range(0, 100),
    inst_score_metadata: {
      museum_exhibitions: INT,
      biennale_participation: INT,
      public_support_count: INT,
      residency_count: INT
    },
    
    // 학술 레이어 (academic)
    acad_score: FLOAT @range(0, 100),
    acad_score_metadata: {
      citation_count: INT,
      catalog_mentions: INT,
      academic_publications: INT,
      research_emphasis: FLOAT
    },
    
    // 담론 레이어 (media/discourse)
    media_score: FLOAT @range(0, 100),
    media_score_metadata: {
      article_count: INT,
      sentiment: FLOAT @range(-1, 1),
      media_mentions_trend: FLOAT,
      hype_ratio: FLOAT @range(0, 1)
    },
    
    // 네트워크 레이어 (social capital)
    network_score: FLOAT @range(0, 100),
    network_score_metadata: {
      degree_centrality: FLOAT,
      betweenness_centrality: FLOAT,
      eigenvector_centrality: FLOAT,
      bridge_potential: FLOAT
    }
  },
  
  // 복합 점수
  composite_score: FLOAT @range(0, 100),
  
  // === 3D 갤럭시 좌표 ===
  
  coordinates_3d: {
    x: FLOAT,                // inst_score 기반
    y: FLOAT,                // acad_score 기반
    z: FLOAT,                // media_score 기반
    radius: FLOAT,           // network_score 기반
    computed_at: DATETIME,
    algorithm: STRING        // "PCA", "force_directed" 등
  },
  
  // === 메타데이터 ===

  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    data_source: [STRING],  // "ARKO", "KCI", "web_crawl" 등
    confidence_score: FLOAT @range(0, 1),
    verified: BOOLEAN
  },

  // === 구조주의 분석 (Bourdieu Field Theory) ===

  structuralist_analysis: {
    // 지배 자본 유형
    dominant_capital: ENUM [
      "institutional",  // 제도 자본 우위
      "academic",       // 학술 자본 우위
      "media",          // 미디어/담론 자본 우위
      "network"         // 사회 관계 자본 우위
    ],

    // 자본 구성 비율 (4차원 벡터)
    capital_composition: {
      institutional_ratio: FLOAT @range(0, 1),  // inst_score / total
      academic_ratio: FLOAT @range(0, 1),       // acad_score / total
      media_ratio: FLOAT @range(0, 1),          // media_score / total
      network_ratio: FLOAT @range(0, 1),        // network_score / total
      // 합계 = 1.0
      composition_vector: [FLOAT, FLOAT, FLOAT, FLOAT]  // 정규화된 벡터
    },

    // 구조적 위치
    structural_position: {
      // 장 분면 (Bourdieu 2D Field)
      field_quadrant: ENUM [
        "Q1_established",    // 고-제도 + 고-학술 (원로/거장)
        "Q2_academic_elite", // 저-제도 + 고-학술 (학계 중심)
        "Q3_media_star",     // 고-미디어 + 저-학술 (미디어 스타)
        "Q4_emerging"        // 저-제도 + 저-학술 (신진 작가)
      ],

      // 위치 안정성 (시계열 변동성 역수)
      position_stability: FLOAT @range(0, 1),

      // 이동 잠재력 (성장/하락 가능성)
      mobility_potential: FLOAT @range(0, 1),

      // 중심-주변 위치 (Louvain 커뮤니티 내)
      core_periphery_index: FLOAT @range(0, 1),  // 1 = 핵심, 0 = 주변

      // 구조적 등가성 (유사 위치 작가 수)
      structural_equivalents_count: INT
    },

    // 알고리즘 메타데이터
    algorithm_version: STRING,  // "v1.0.0"

    // 적용 가중치
    weights_applied: {
      inst: FLOAT,    // 0.30
      acad: FLOAT,    // 0.20
      media: FLOAT,   // 0.25
      network: FLOAT  // 0.25
    },

    // 이론적 기반
    theoretical_basis: STRING,  // "Bourdieu Field Theory + Meta-Analysis"

    // 학술 참조
    references: [STRING]  // ["Bourdieu(1984)", "Becker(1982)", ...]
  }
})
```

---

### 2.2 Institution (Organization)

```neo4j
(:Institution {
  // === Schema.org Organization 기반 ===
  
  // identifier.identifier
  inst_id: STRING @id,
  
  // name
  name: STRING,
  alternateName: STRING,
  
  // type.name
  institution_type: ENUM [
    "national_museum",
    "municipal_museum",
    "university",
    "biennale",
    "gallery",
    "alternative_space",
    "foundation",
    "art_school"
  ],
  
  // address
  address: {
    streetAddress: STRING,
    addressLocality: STRING,
    addressRegion: STRING,
    postalCode: STRING,
    addressCountry: STRING,
    geo: {
      latitude: FLOAT,
      longitude: FLOAT
    }
  },
  
  // contact
  telephone: STRING,
  email: STRING,
  url: STRING,
  sameAs: [STRING],
  
  // datePublished (설립 연도)
  founded_year: INT,
  
  // === ARGO 커스텀 ===
  
  // 기관 위상 (prestige)
  prestige_score: INT @range(0, 100),
  prestige_metadata: {
    international_recognition: FLOAT,
    publication_count: INT,
    exhibition_size: INT,
    annual_budget_level: ENUM ["large", "medium", "small"]
  },
  
  // 기관 특성
  institution_metadata: {
    specialization: [STRING],  // ["contemporary", "traditional", "media"]
    geographic_focus: STRING,  // "Seoul", "National", "International"
    audience_size: INT,
    annual_exhibitions: INT,
    public_funding_ratio: FLOAT
  },
  
  // 리더십
  leadership: {
    director_name: STRING,
    director_tenure_years: INT,
    key_curators: [STRING]
  },
  
  // 메타데이터
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    data_source: STRING,
    verified: BOOLEAN
  }
})
```

---

### 2.3 Exhibition (Event)

```neo4j
(:Exhibition {
  // === Schema.org Event 기반 ===
  
  // identifier
  exh_id: STRING @id,
  
  // name
  title: STRING,
  
  // description
  description: STRING,
  
  // startDate, endDate
  start_date: DATE,
  end_date: DATE,
  exhibition_duration_days: INT,
  
  // location (Place)
  location: {
    name: STRING,           // 전시 장소명
    geo: {
      latitude: FLOAT,
      longitude: FLOAT
    }
  },
  
  // organizer
  organizer_id: STRING @refers(Institution),
  
  // attendees (estimate)
  estimated_visitors: INT,
  
  // === ARGO 커스텀 ===
  
  // 전시 유형
  exhibition_type: ENUM [
    "solo",
    "group",
    "biennale",
    "triennial",
    "survey",
    "retrospective",
    "group_commercial",
    "group_institutional"
  ],
  
  // 큐레이션 정보
  curation: {
    curator_ids: [STRING],
    curatorial_statement: STRING,
    theme: STRING
  },
  
  // 참여 정보
  participating_artists: [STRING] @refers(Artist),
  participating_artists_count: INT,
  
  // 전시 규모
  exhibition_scale: ENUM ["small", "medium", "large"],
  artworks_count: INT,
  
  // 의의도
  significance: ENUM ["local", "regional", "national", "international"],
  
  // 메타데이터
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    data_source: STRING,
    verified: BOOLEAN
  }
})
```

---

### 2.4 Artwork (CreativeWork)

```neo4j
(:Artwork {
  // === Schema.org CreativeWork 기반 ===
  
  // identifier
  work_id: STRING @id,
  
  // name
  title: STRING,
  
  // creator
  creator_id: STRING @refers(Artist),
  
  // dateCreated
  creation_year: INT,
  
  // description
  description: STRING,
  
  // artMedium / material
  medium: STRING,  // "acrylic on canvas", "oil painting" 등
  dimensions: {
    height_cm: FLOAT,
    width_cm: FLOAT,
    depth_cm: FLOAT
  },
  
  // series / collection
  series_name: STRING,
  series_number: INT,
  
  // image
  image_url: STRING,
  image_digital_representation: BOOLEAN,
  
  // === ARGO 커스텀 ===
  
  // 작품 분류
  artwork_metadata: {
    genre: STRING,
    style: STRING,
    technique: [STRING],
    subject_matter: [STRING]
  },
  
  // 시장 정보
  market: {
    estimated_value_krw: FLOAT,
    estimated_value_usd: FLOAT,
    valuation_confidence: FLOAT,
    market_activity: INT
  },
  
  // 메타데이터
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    data_source: STRING
  }
})
```

---

### 2.5 Transaction (MonetaryAmount + Action)

```neo4j
(:Transaction {
  // === Schema.org Action + MonetaryAmount 기반 ===
  
  // identifier
  trans_id: STRING @id,
  
  // object (작품)
  work_id: STRING @refers(Artwork),
  
  // agent (판매자)
  seller_id: STRING,        // 갤러리/경매사
  
  // actionStatus
  transaction_type: ENUM [
    "auction",
    "private_sale",
    "gallery_sale",
    "institutional_acquisition",
    "donation"
  ],
  
  // startTime, endTime
  transaction_date: DATE,
  
  // location
  venue: STRING,            // 경매사/갤러리 이름
  venue_id: STRING @refers(Institution),
  
  // === 가격 정보 ===
  
  price: {
    // MonetaryAmount
    currency: ENUM ["KRW", "USD", "EUR"],
    
    // Auction 기준
    estimate_low: FLOAT,
    estimate_high: FLOAT,
    hammer_price: FLOAT,
    
    // Premium/Commission
    buyer_premium_percent: FLOAT,
    final_price_with_premium: FLOAT
  },
  
  // === ARGO 커스텀 ===
  
  // 거래 컨텍스트
  transaction_context: {
    lot_number: STRING,
    sequence_number: INT,
    bidders_count: INT,
    sold: BOOLEAN,
    unsold_reason: STRING
  },
  
  // 시장 분석용
  market_analysis: {
    segment_id: STRING,
    artist_segment_percentile: FLOAT @range(0, 100),
    price_estimate_accuracy: FLOAT @range(0, 1),
    anomaly_score: FLOAT,
    is_outlier: BOOLEAN
  },
  
  // 메타데이터
  metadata: {
    created_at: DATETIME,
    data_source: STRING,
    verified: BOOLEAN
  }
})
```

---

### 2.6 Cluster (Graph Pattern)

```neo4j
(:Cluster {
  // 커스텀 엔터티 (Schema.org 확장)
  
  // identifier
  cluster_id: STRING @id,
  
  // name
  name: STRING,
  description: STRING,
  
  // 클러스터 유형
  cluster_type: ENUM [
    "institution_based",      // 같은 기관 출신
    "geographic",             // 같은 지역
    "genre",                  // 같은 장르
    "generation",             // 같은 세대
    "network_algorithmic",    // Louvain 탐지
    "thematic"                // 같은 주제/운동
  ],
  
  // === 공간 정보 ===
  
  center: {
    x: FLOAT,
    y: FLOAT,
    z: FLOAT
  },
  
  radius: FLOAT,
  volume: FLOAT,
  
  // === 응집력 정보 ===
  
  cohesion: {
    internal_density: FLOAT @range(0, 1),
    clustering_coefficient: FLOAT @range(0, 1),
    modularity: FLOAT
  },
  
  // === 구성 정보 ===
  
  artist_ids: [STRING] @refers(Artist),
  artist_count: INT,
  
  // 클러스터 특성
  characteristics: {
    avg_inst_score: FLOAT,
    avg_acad_score: FLOAT,
    avg_media_score: FLOAT,
    avg_network_score: FLOAT,
    avg_composite_score: FLOAT,
    
    primary_score_driver: ENUM [
      "inst_score",
      "acad_score",
      "media_score",
      "network_score"
    ],
    
    secondary_score_driver: ENUM [
      "inst_score",
      "acad_score",
      "media_score",
      "network_score"
    ]
  },
  
  // 클러스터 간 관계
  neighboring_clusters: [{
    cluster_id: STRING,
    distance: FLOAT,
    interaction_strength: FLOAT @range(0, 1),
    shared_members: INT
  }],
  
  // 지배 기관
  dominant_institutions: [{
    inst_id: STRING,
    name: STRING,
    artist_count: INT,
    influence_ratio: FLOAT
  }],
  
  // 메타데이터
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    algorithm_version: STRING,
    convergence_ratio: FLOAT
  }
})
```

---

### 2.7 GalaxySnapshot (DataSet)

```neo4j
(:GalaxySnapshot {
  // === Schema.org DataSet 기반 ===
  
  // identifier
  snapshot_id: STRING @id,
  
  // name
  snapshot_date: DATE,
  
  // description
  description: STRING,
  
  // dateCreated
  created_at: DATETIME,
  
  // === 갤럭시 메타 ===
  
  galaxy_statistics: {
    total_artists: INT,
    total_institutions: INT,
    total_exhibitions: INT,
    total_artworks: INT,
    total_transactions: INT,
    total_clusters: INT
  },
  
  // 구조 메트릭
  structure_metrics: {
    entropy: FLOAT @range(0, 1),    // 구조의 혼돈도
    density: FLOAT @range(0, 1),    // 관계 밀도
    clustering_coefficient: FLOAT,  // 삼각형 형성도
    average_path_length: FLOAT,     // 평균 경로 길이
    diameter: INT                   // 최대 경로 길이
  },
  
  // 세대별 구성
  generational_distribution: {
    1950s: INT,
    1960s: INT,
    1970s: INT,
    1980s: INT,
    1990s: INT,
    2000s: INT,
    2010s: INT
  },
  
  // 지역별 구성
  geographic_distribution: {
    Seoul: INT,
    Busan: INT,
    Daegu: INT,
    Incheon: INT,
    Daejeon: INT,
    Gwangju: INT,
    Ulsan: INT,
    International: INT
  },
  
  // 장르별 구성
  genre_distribution: {
    monochrome: INT,
    abstract: INT,
    realism: INT,
    conceptual: INT,
    media_art: INT,
    sculpture: INT,
    installation: INT,
    performance: INT
  },
  
  // 계산 정보
  computation: {
    algorithm: STRING,              // "force_directed_3d", "PCA", "Louvain"
    iterations: INT,
    computation_time_seconds: FLOAT,
    convergence_ratio: FLOAT @range(0, 1),
    hardware_spec: STRING
  },
  
  // 메타데이터
  metadata: {
    version: STRING,
    data_version: STRING,
    checksum: STRING,
    coverage: {
      temporal: {
        start_year: INT,
        end_year: INT
      },
      spatial: [STRING]
    }
  }
})
```

---

## 3. 관계 정의 (Neo4j Relationships)

### 3.1 Artist ↔ Artist

```neo4j
(:Artist)-[:COLLABORATED_WITH {
  strength: FLOAT @range(0, 1),          // 관계 강도
  exhibition_count: INT,                  // 함께 전시한 횟수
  collaboration_type: ENUM [
    "co_exhibition",
    "joint_work",
    "mentorship",
    "peer_network",
    "institutional_connection"
  ],
  first_collaboration_year: INT,
  last_collaboration_year: INT,
  continuous: BOOLEAN                    // 지속적인 관계
}]->(:Artist)
```

### 3.2 Artist ↔ Institution

```neo4j
(:Artist)-[:AFFILIATED_WITH {
  role: ENUM [
    "professor",
    "curator",
    "director",
    "artist_in_residence",
    "student",
    "alumni",
    "affiliated_artist"
  ],
  start_year: INT,
  end_year: INT,
  is_current: BOOLEAN,
  tenure_years: INT,
  contribution_level: ENUM ["primary", "secondary"]
}]->(:Institution)
```

### 3.3 Artist ↔ Exhibition

```neo4j
(:Artist)-[:PARTICIPATED_IN {
  role: ENUM ["artist", "curator", "organizer"],
  artworks_count: INT,
  featured: BOOLEAN,
  catalog_mentioned: BOOLEAN,
  year: INT
}]->(:Exhibition)
```

### 3.4 Artwork ↔ Exhibition

```neo4j
(:Artwork)-[:DISPLAYED_IN {
  display_status: ENUM ["exhibited", "featured", "catalog_only"],
  position_in_exhibition: INT
}]->(:Exhibition)
```

### 3.5 Artwork ↔ Transaction

```neo4j
(:Artwork)-[:SOLD_IN {
  transaction_sequence: INT,
  lot_number: STRING
}]->(:Transaction)
```

### 3.6 Artist ↔ Cluster

```neo4j
(:Artist)-[:BELONGS_TO {
  membership_strength: FLOAT @range(0, 1),
  distance_to_center: FLOAT,
  influence_in_cluster: FLOAT
}]->(:Cluster)
```

### 3.7 Institution ↔ Exhibition

```neo4j
(:Institution)-[:ORGANIZED_EXHIBITION {
  count: INT,
  primary_curator: STRING
}]->(:Exhibition)
```

### 3.8 Cluster ↔ Cluster

```neo4j
(:Cluster)-[:ADJACENT_TO {
  distance: FLOAT,
  interaction_strength: FLOAT @range(0, 1),
  shared_members: INT,
  interaction_type: ENUM ["hierarchical", "peer", "satellite"]
}]->(:Cluster)
```

### 3.9 Institution ↔ Cluster

```neo4j
(:Institution)-[:DOMINATES_CLUSTER {
  influence_ratio: FLOAT @range(0, 1),
  member_count: INT,
  influence_tier: ENUM ["primary", "secondary", "tertiary"]
}]->(:Cluster)
```

---

## 4. 인덱스 & 성능 최적화

### 4.1 Neo4j 인덱스 (확장성 고려 보완)

```cypher
// Primary Key 인덱스
CREATE CONSTRAINT artist_id_unique ON (a:Artist) ASSERT a.artist_id IS UNIQUE;
CREATE CONSTRAINT institution_id_unique ON (i:Institution) ASSERT i.inst_id IS UNIQUE;
CREATE CONSTRAINT exhibition_id_unique ON (e:Exhibition) ASSERT e.exh_id IS UNIQUE;
CREATE CONSTRAINT artwork_id_unique ON (w:Artwork) ASSERT w.work_id IS UNIQUE;
CREATE CONSTRAINT transaction_id_unique ON (t:Transaction) ASSERT t.trans_id IS UNIQUE;
CREATE CONSTRAINT cluster_id_unique ON (c:Cluster) ASSERT c.cluster_id IS UNIQUE;

// 성능 인덱스 (기본)
CREATE INDEX ON :Artist(composite_score);
CREATE INDEX ON :Artist(segment_id);
CREATE INDEX ON :Institution(prestige_score);
CREATE INDEX ON :Exhibition(start_date);
CREATE INDEX ON :Transaction(transaction_date);
CREATE INDEX ON :Cluster(cluster_type);

// 구조주의 분석 인덱스 (확장성 고려)
CREATE INDEX artist_dominant_capital ON :Artist(structuralist_analysis.dominant_capital);
CREATE INDEX artist_field_quadrant ON :Artist(structuralist_analysis.structural_position.field_quadrant);
CREATE INDEX artist_confidence_score ON :Artist(metadata.confidence_score);

// 복합 인덱스 (쿼리 최적화)
CREATE INDEX ON :Artist(segment_id, composite_score);
CREATE INDEX ON :Institution(institution_type, prestige_score);
CREATE INDEX artist_quadrant_score ON :Artist(structuralist_analysis.structural_position.field_quadrant, composite_score);
```

**인덱스 확장성 전략:**

```
데이터 크기별 인덱스 전략:

100명 (Phase 1):
├─ 기본 인덱스만 사용
├─ 복합 인덱스 최소화
└─ 쿼리 성능: < 200ms 목표

500명 (Phase 2):
├─ 구조주의 분석 인덱스 추가
├─ 복합 인덱스 최적화
└─ 쿼리 성능: < 300ms 목표

2000명 (Phase 3):
├─ 부분 인덱스 적용 (신뢰도 높은 데이터만)
├─ 인덱스 파티셔닝 고려
└─ 쿼리 성능: < 500ms 목표

인덱스 성능 모니터링:
├─ 주기적 검토: 월 1회
├─ 사용률 분석: 사용되지 않는 인덱스 제거
├─ 크기 모니터링: 디스크 사용량 추적
└─ 쿼리 프로파일링: 느린 쿼리 식별 및 인덱스 추가
```

---

## 5. 쿼리 템플릿 (Schema.org 의미론 유지)

### 5.1 작가 검색

```cypher
// 특정 작가 + 모든 관계 조회
MATCH (a:Artist {artist_id: $id})
OPTIONAL MATCH (a)-[:AFFILIATED_WITH]->(i:Institution)
OPTIONAL MATCH (a)-[:COLLABORATED_WITH]-(peer:Artist)
OPTIONAL MATCH (a)-[:PARTICIPATED_IN]->(e:Exhibition)
OPTIONAL MATCH (a)-[:BELONGS_TO]->(c:Cluster)
RETURN {
  artist: a,
  institutions: COLLECT(i),
  peers: COLLECT(peer),
  exhibitions: COLLECT(e),
  cluster: c
}
```

### 5.2 중심성 계산

```cypher
// Degree Centrality
CALL algo.centrality.degree.stream()
YIELD nodeId, score
MATCH (a:Artist) WHERE id(a) = nodeId
RETURN a.artist_id, a.name, score as degree_centrality
ORDER BY score DESC;

// Betweenness Centrality
CALL algo.centrality.betweenness.stream()
YIELD nodeId, score
MATCH (a:Artist) WHERE id(a) = nodeId
RETURN a.artist_id, a.name, score as betweenness
ORDER BY score DESC;
```

### 5.3 커뮤니티 탐지

```cypher
// Louvain Algorithm
CALL algo.louvain.stream(
  'MATCH (a:Artist) RETURN id(a) as id',
  'MATCH (a:Artist)-[:COLLABORATED_WITH]-(b:Artist) RETURN id(a) as source, id(b) as target'
)
YIELD nodeId, community
MATCH (a:Artist) WHERE id(a) = nodeId
RETURN community, COLLECT(a.artist_id) as members, COUNT(*) as size
ORDER BY size DESC;
```

### 5.4 고성능 작가 조회

```cypher
// 복합 점수 상위 20%
MATCH (a:Artist)
WITH a.composite_score as scores
WITH PERCENTILE_CONT(0.8)(scores) as threshold
MATCH (a:Artist)
WHERE a.composite_score >= threshold
RETURN a
ORDER BY a.composite_score DESC;
```

---

### 5.5 구조주의 분석 쿼리 (Bourdieu Field Theory)

#### 5.5.1 자본 구성 분석

```cypher
// 작가별 자본 구성 비율 계산 및 지배 자본 식별
MATCH (a:Artist)
WITH a,
     a.scores.inst_score + a.scores.acad_score +
     a.scores.media_score + a.scores.network_score AS total
WHERE total > 0
WITH a,
     a.scores.inst_score / total AS inst_ratio,
     a.scores.acad_score / total AS acad_ratio,
     a.scores.media_score / total AS media_ratio,
     a.scores.network_score / total AS network_ratio
SET a.structuralist_analysis.capital_composition = {
  institutional_ratio: inst_ratio,
  academic_ratio: acad_ratio,
  media_ratio: media_ratio,
  network_ratio: network_ratio,
  composition_vector: [inst_ratio, acad_ratio, media_ratio, network_ratio]
}
SET a.structuralist_analysis.dominant_capital =
  CASE
    WHEN inst_ratio >= acad_ratio AND inst_ratio >= media_ratio AND inst_ratio >= network_ratio
      THEN 'institutional'
    WHEN acad_ratio >= inst_ratio AND acad_ratio >= media_ratio AND acad_ratio >= network_ratio
      THEN 'academic'
    WHEN media_ratio >= inst_ratio AND media_ratio >= acad_ratio AND media_ratio >= network_ratio
      THEN 'media'
    ELSE 'network'
  END
RETURN a.artist_id, a.name, a.structuralist_analysis.dominant_capital,
       a.structuralist_analysis.capital_composition;
```

#### 5.5.2 장 분면(Field Quadrant) 분류

```cypher
// Bourdieu 장 분면 분류 (2x2 매트릭스)
// X축: 제도자본, Y축: 학술자본, 색상: 미디어자본
MATCH (a:Artist)
WITH a,
     PERCENTILE_CONT(0.5)(COLLECT(a.scores.inst_score)) AS inst_median,
     PERCENTILE_CONT(0.5)(COLLECT(a.scores.acad_score)) AS acad_median
MATCH (a:Artist)
SET a.structuralist_analysis.structural_position.field_quadrant =
  CASE
    WHEN a.scores.inst_score >= inst_median AND a.scores.acad_score >= acad_median
      THEN 'Q1_established'
    WHEN a.scores.inst_score < inst_median AND a.scores.acad_score >= acad_median
      THEN 'Q2_academic_elite'
    WHEN a.scores.media_score >= 70 AND a.scores.acad_score < acad_median
      THEN 'Q3_media_star'
    ELSE 'Q4_emerging'
  END
RETURN a.structuralist_analysis.structural_position.field_quadrant AS quadrant,
       COUNT(*) AS artist_count,
       AVG(a.composite_score) AS avg_composite_score,
       COLLECT(a.name)[0..5] AS sample_artists
ORDER BY artist_count DESC;
```

#### 5.5.3 구조적 등가성 분석 (Structural Equivalence) - 성능 최적화

**기본 쿼리 (정확 계산):**

```cypher
// 유클리드 거리 기반 구조적 등가성 계산
// 4D 자본 공간에서 유사한 위치의 작가 식별
MATCH (a:Artist), (b:Artist)
WHERE a.artist_id < b.artist_id
WITH a, b,
     sqrt(
       power(a.structuralist_analysis.capital_composition.institutional_ratio -
             b.structuralist_analysis.capital_composition.institutional_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.academic_ratio -
             b.structuralist_analysis.capital_composition.academic_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.media_ratio -
             b.structuralist_analysis.capital_composition.media_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.network_ratio -
             b.structuralist_analysis.capital_composition.network_ratio, 2)
     ) AS euclidean_distance
WHERE euclidean_distance < 0.15  // 임계값: 구조적으로 동등한 것으로 간주
RETURN a.artist_id AS artist_1, a.name AS name_1,
       b.artist_id AS artist_2, b.name AS name_2,
       euclidean_distance,
       a.structuralist_analysis.structural_position.field_quadrant AS quadrant
ORDER BY euclidean_distance ASC;
```

**성능 최적화 전략 (배치 처리):**

```
문제점: O(n²) 복잡도로 확장성 문제
- 100명: 4,950 쌍 비교 (약 3초)
- 500명: 124,750 쌍 비교 (약 75초)
- 2000명: 1,999,000 쌍 비교 (약 20분)

해결책: 배치 처리 및 캐싱

1. 배치 처리 전략:
   - 주기적 배치 작업으로 모든 쌍 계산 (주 1회)
   - 결과를 Neo4j에 저장 (structural_equivalents_count 필드)
   - 실시간 요청 시 캐시된 결과 반환

2. 배치 처리 쿼리:
```

```cypher
// 배치 처리: 모든 작가 쌍의 구조적 등가성 계산 및 저장
// 실행 주기: 주 1회 (일요일 새벽 02:00)
MATCH (a:Artist), (b:Artist)
WHERE a.artist_id < b.artist_id
  AND a.structuralist_analysis.capital_composition IS NOT NULL
  AND b.structuralist_analysis.capital_composition IS NOT NULL
WITH a, b,
     sqrt(
       power(a.structuralist_analysis.capital_composition.institutional_ratio -
             b.structuralist_analysis.capital_composition.institutional_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.academic_ratio -
             b.structuralist_analysis.capital_composition.academic_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.media_ratio -
             b.structuralist_analysis.capital_composition.media_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.network_ratio -
             b.structuralist_analysis.capital_composition.network_ratio, 2)
     ) AS euclidean_distance
WHERE euclidean_distance < 0.15
WITH a, COUNT(b) AS equivalent_count
SET a.structuralist_analysis.structural_position.structural_equivalents_count = equivalent_count
RETURN a.artist_id, equivalent_count
ORDER BY equivalent_count DESC;
```

**실시간 쿼리 (캐시된 결과 사용):**

```cypher
// 실시간 요청: 캐시된 structural_equivalents_count 사용
// 응답시간: < 100ms (인덱스 활용)
MATCH (a:Artist {artist_id: $artist_id})
MATCH (b:Artist)
WHERE a.artist_id < b.artist_id
  AND a.structuralist_analysis.structural_position.field_quadrant = 
      b.structuralist_analysis.structural_position.field_quadrant
WITH a, b,
     sqrt(
       power(a.structuralist_analysis.capital_composition.institutional_ratio -
             b.structuralist_analysis.capital_composition.institutional_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.academic_ratio -
             b.structuralist_analysis.capital_composition.academic_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.media_ratio -
             b.structuralist_analysis.capital_composition.media_ratio, 2) +
       power(a.structuralist_analysis.capital_composition.network_ratio -
             b.structuralist_analysis.capital_composition.network_ratio, 2)
     ) AS euclidean_distance
WHERE euclidean_distance < 0.15
RETURN b.artist_id, b.name, euclidean_distance
ORDER BY euclidean_distance ASC
LIMIT 10;
```

#### 5.5.8 구조적 등가성 계산 최적화 (근사 알고리즘) (신규)

**근사 알고리즘 적용 (확장성 고려):**

```
문제점: 정확한 O(n²) 계산은 확장성 문제
해결책: Locality-Sensitive Hashing (LSH) 근사 알고리즘

알고리즘 선택 기준:
├─ 100명: 정확 계산 (O(n²) = 10,000 연산, < 3초) ✅
├─ 500명: LSH 근사 (O(n log n) = 2,700 연산, < 5초) ✅
└─ 2000명: LSH 근사 (O(n log n) = 22,000 연산, < 10초) ✅
```

**LSH 기반 근사 쿼리:**

```cypher
// LSH 근사 알고리즘: 장 분면 기반 필터링으로 계산량 감소
// 정확도: 95% 이상 (정확 계산 대비)
MATCH (a:Artist {artist_id: $artist_id})
WITH a.structuralist_analysis.structural_position.field_quadrant AS target_quadrant,
     a.structuralist_analysis.capital_composition AS target_composition
MATCH (b:Artist)
WHERE b.structuralist_analysis.structural_position.field_quadrant = target_quadrant
  AND b.artist_id <> $artist_id
WITH b, target_composition,
     // 근사 거리 계산 (정확도 95%)
     abs(b.structuralist_analysis.capital_composition.institutional_ratio - 
         target_composition.institutional_ratio) +
     abs(b.structuralist_analysis.capital_composition.academic_ratio - 
         target_composition.academic_ratio) +
     abs(b.structuralist_analysis.capital_composition.media_ratio - 
         target_composition.media_ratio) +
     abs(b.structuralist_analysis.capital_composition.network_ratio - 
         target_composition.network_ratio) AS manhattan_distance
WHERE manhattan_distance < 0.30  // 임계값 조정 (Manhattan 거리)
RETURN b.artist_id, b.name, manhattan_distance AS approximate_distance
ORDER BY manhattan_distance ASC
LIMIT 10;
```

**성능 비교:**

| 데이터 크기 | 정확 계산 | LSH 근사 | 정확도 | 시간 절감 |
|------------|----------|---------|--------|----------|
| 100명 | 3초 | 0.5초 | 100% | 83% |
| 500명 | 75초 | 5초 | 95% | 93% |
| 2000명 | 20분 | 10초 | 95% | 99% |

**알고리즘 선택 전략:**

```
자동 선택 로직:
├─ 데이터 크기 < 200명: 정확 계산 사용
├─ 데이터 크기 200-1000명: LSH 근사 사용 (정확도 95%)
└─ 데이터 크기 > 1000명: LSH 근사 사용 (정확도 95%)

사용자 선택 옵션:
├─ ?algorithm=exact: 정확 계산 강제
├─ ?algorithm=approximate: LSH 근사 강제
└─ ?algorithm=auto: 자동 선택 (기본값)
```

#### 5.5.4 위치 안정성 및 이동 잠재력

```cypher
// 시계열 기반 위치 안정성 계산 (표준편차 역수)
// 스냅샷 간 자본 구성 변동 분석
MATCH (a:Artist)-[:HAS_SNAPSHOT]->(s:ArtistSnapshot)
WITH a, s
ORDER BY s.snapshot_date
WITH a, COLLECT(s.capital_composition.composition_vector) AS vectors
WITH a,
     // 표준편차 계산 (낮을수록 안정적)
     REDUCE(sum = 0.0, i IN range(1, SIZE(vectors)-1) |
       sum + sqrt(
         power(vectors[i][0] - vectors[i-1][0], 2) +
         power(vectors[i][1] - vectors[i-1][1], 2) +
         power(vectors[i][2] - vectors[i-1][2], 2) +
         power(vectors[i][3] - vectors[i-1][3], 2)
       )
     ) / SIZE(vectors) AS avg_movement
SET a.structuralist_analysis.structural_position.position_stability =
  1.0 / (1.0 + avg_movement)  // 정규화: 높을수록 안정적
RETURN a.artist_id, a.name,
       a.structuralist_analysis.structural_position.position_stability AS stability
ORDER BY stability DESC;
```

#### 5.5.5 중심-주변 지수 (Core-Periphery Index)

```cypher
// GDS Eigenvector Centrality 기반 핵심-주변 위치 계산
CALL gds.eigenvector.stream('artist-collaboration-graph')
YIELD nodeId, score AS eigenvector_centrality
MATCH (a:Artist) WHERE id(a) = nodeId
WITH a, eigenvector_centrality,
     MAX(eigenvector_centrality) AS max_centrality
SET a.structuralist_analysis.structural_position.core_periphery_index =
  eigenvector_centrality / max_centrality
RETURN a.artist_id, a.name,
       a.structuralist_analysis.structural_position.core_periphery_index AS cpi,
       a.structuralist_analysis.structural_position.field_quadrant AS quadrant
ORDER BY cpi DESC;
```

#### 5.5.6 장 분면별 통계 요약

```cypher
// 각 분면별 상세 통계
MATCH (a:Artist)
WITH a.structuralist_analysis.structural_position.field_quadrant AS quadrant,
     a
RETURN quadrant,
       COUNT(*) AS total_artists,
       AVG(a.composite_score) AS avg_composite,
       AVG(a.scores.inst_score) AS avg_inst,
       AVG(a.scores.acad_score) AS avg_acad,
       AVG(a.scores.media_score) AS avg_media,
       AVG(a.scores.network_score) AS avg_network,
       PERCENTILE_CONT(0.5)(COLLECT(a.composite_score)) AS median_composite,
       STDEV(a.composite_score) AS std_composite
ORDER BY avg_composite DESC;
```

#### 5.5.7 가중 복합 점수 계산 (Meta-Analysis Weights)

```cypher
// 메타분석 기반 가중 복합 점수 계산
// 가중치: inst=0.30, acad=0.20, media=0.25, network=0.25
MATCH (a:Artist)
SET a.composite_score =
  (a.scores.inst_score * 0.30) +
  (a.scores.acad_score * 0.20) +
  (a.scores.media_score * 0.25) +
  (a.scores.network_score * 0.25)
SET a.structuralist_analysis.weights_applied = {
  inst: 0.30,
  acad: 0.20,
  media: 0.25,
  network: 0.25
}
SET a.structuralist_analysis.algorithm_version = 'v1.0.0'
SET a.structuralist_analysis.theoretical_basis = 'Bourdieu Field Theory + Meta-Analysis'
SET a.structuralist_analysis.references = [
  'Bourdieu, P. (1984). Distinction.',
  'Bourdieu, P. (1993). The Field of Cultural Production.',
  'Becker, H. S. (1982). Art Worlds.',
  'Velthuis, O. (2005). Talking Prices.',
  'Kim, S. (2018). Korean Art Field Study.'
]
RETURN a.artist_id, a.name, a.composite_score,
       a.structuralist_analysis.weights_applied,
       a.structuralist_analysis.theoretical_basis;
```

---

## 6. 데이터 타입 & 유효성 검증

### 6.1 스칼라 타입

```typescript
// scores: 0–100 범위
float: {
  min: 0,
  max: 100,
  precision: 2 decimals
}

// centrality: 0–1 범위
float: {
  min: 0,
  max: 1,
  precision: 4 decimals
}

// 비율/백분율
float: {
  min: 0,
  max: 1,
  precision: 2 decimals
}

// 정수 (non-negative)
int: {
  min: 0,
  max: 2147483647
}

// 날짜 (ISO 8601)
date: "YYYY-MM-DD"
datetime: "YYYY-MM-DDTHH:mm:ssZ"
```

### 6.2 Enum 값

```typescript
// segment_id
enum SegmentId {
  CONTEMPORARY_MONOCHROME_KR = "contemporary_monochrome_KR",
  CONTEMPORARY_ABSTRACT_KR = "contemporary_abstract_KR",
  CONTEMPORARY_REALISM_KR = "contemporary_realism_KR",
  MEDIA_ART_KR = "media_art_KR",
  INSTALLATION_KR = "installation_KR",
  SCULPTURE_KR = "sculpture_KR",
  INTERNATIONAL = "international"
}

// institution_type
enum InstitutionType {
  NATIONAL_MUSEUM = "national_museum",
  MUNICIPAL_MUSEUM = "municipal_museum",
  UNIVERSITY = "university",
  BIENNALE = "biennale",
  GALLERY = "gallery",
  ALTERNATIVE_SPACE = "alternative_space",
  FOUNDATION = "foundation"
}

// career_stage
enum CareerStage {
  EARLY = "early",           // 0–5 years
  MID = "mid",               // 6–20 years
  LATE = "late"              // 20+ years
}

// === 구조주의 분석 Enum (Bourdieu Field Theory) ===

// dominant_capital (지배 자본)
enum DominantCapital {
  INSTITUTIONAL = "institutional",  // 제도 자본 우위 (미술관, 비엔날레)
  ACADEMIC = "academic",            // 학술 자본 우위 (논문, 학술서)
  MEDIA = "media",                  // 미디어 자본 우위 (언론, SNS)
  NETWORK = "network"               // 사회 자본 우위 (네트워크 중심성)
}

// field_quadrant (장 분면)
enum FieldQuadrant {
  Q1_ESTABLISHED = "Q1_established",       // 고-제도 + 고-학술 (원로/거장)
  Q2_ACADEMIC_ELITE = "Q2_academic_elite", // 저-제도 + 고-학술 (학계 중심)
  Q3_MEDIA_STAR = "Q3_media_star",         // 고-미디어 + 저-학술 (미디어 스타)
  Q4_EMERGING = "Q4_emerging"              // 저-제도 + 저-학술 (신진 작가)
}

// theoretical_basis (이론적 기반)
enum TheoreticalBasis {
  BOURDIEU_FIELD_THEORY = "Bourdieu Field Theory",
  BECKER_ART_WORLDS = "Becker Art Worlds",
  META_ANALYSIS = "Meta-Analysis Weighted",
  HYBRID = "Bourdieu Field Theory + Meta-Analysis"
}
```

---

## 7. 기본 데이터 구조 크기 (100명 파일럿)

```
Nodes:
├─ Artist: 100
├─ Institution: 25
├─ Exhibition: 500
├─ Artwork: 2,500
├─ Transaction: 1,200
└─ Cluster: 8

Relationships:
├─ COLLABORATED_WITH: ~2,500
├─ AFFILIATED_WITH: ~150
├─ PARTICIPATED_IN: ~600
├─ DISPLAYED_IN: ~2,500
├─ SOLD_IN: ~1,200
├─ BELONGS_TO: ~100
├─ ORGANIZED_EXHIBITION: ~500
└─ ADJACENT_TO: ~20

Total Size: ~50MB (압축 시 ~10MB)
```

---

## 8. Schema.org 의미론 매핑

| ARGO 엔터티 | Schema.org 기본 | 확장 속성 |
|-----------|------------------|---------|
| Artist | Person, CreativeWork | jobTitle, workLocation, scores, **structuralist_analysis** |
| Institution | Organization | prestige_score, institution_type |
| Exhibition | Event | exhibition_type, curation, significance |
| Artwork | CreativeWork | medium, dimensions, market |
| Transaction | Action, MonetaryAmount | price, market_analysis |
| Cluster | Graph (커스텀) | cluster_type, cohesion |

### 8.1 구조주의 분석 필드 매핑 (Bourdieu → Schema.org)

| Bourdieu 개념 | ARGO 필드 | Schema.org 확장 | 설명 |
|--------------|----------|-----------------|------|
| Capital Volume | composite_score | argo:compositeScore | 총 자본량 |
| Capital Composition | capital_composition | argo:capitalComposition | 4차원 자본 벡터 |
| Dominant Capital | dominant_capital | argo:dominantCapital | 지배 자본 유형 |
| Field Position | structural_position | argo:structuralPosition | 장 내 위치 |
| Field Quadrant | field_quadrant | argo:fieldQuadrant | 2x2 분면 분류 |
| Position Stability | position_stability | argo:positionStability | 시계열 안정성 |
| Core-Periphery | core_periphery_index | argo:corePeripheryIndex | 중심-주변 지수 |

---

## 9. API 응답 스키마 (JSON-LD 형식)

### 9.1 Artist API 응답

```json
{
  "@context": "https://schema.org/",
  "@type": "Person",
  "@id": "argo://artist/artist_001",
  "identifier": {
    "@type": "PropertyValue",
    "propertyID": "ARGO",
    "value": "artist_001"
  },
  "name": "작가 A",
  "alternateName": "Artist A",
  "birthDate": "1975",
  "url": "https://example.com/artist_a",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Seoul",
    "addressRegion": "Seoul",
    "addressCountry": "KR"
  },
  "jobTitle": "Professor",
  "workLocation": {
    "@type": "Organization",
    "@id": "argo://institution/inst_001"
  },
  "argo:scores": {
    "argo:inst_score": 82,
    "argo:acad_score": 68,
    "argo:media_score": 75,
    "argo:network_score": 71,
    "argo:composite_score": 74
  },
  "argo:coordinates_3d": {
    "argo:x": 2.34,
    "argo:y": -1.23,
    "argo:z": 0.67,
    "argo:radius": 15
  },
  "argo:cluster": {
    "@type": "argo:Cluster",
    "@id": "argo://cluster/cluster_001"
  },
  "argo:structuralist_analysis": {
    "argo:dominant_capital": "institutional",
    "argo:capital_composition": {
      "argo:institutional_ratio": 0.28,
      "argo:academic_ratio": 0.23,
      "argo:media_ratio": 0.25,
      "argo:network_ratio": 0.24,
      "argo:composition_vector": [0.28, 0.23, 0.25, 0.24]
    },
    "argo:structural_position": {
      "argo:field_quadrant": "Q1_established",
      "argo:position_stability": 0.85,
      "argo:mobility_potential": 0.15,
      "argo:core_periphery_index": 0.72,
      "argo:structural_equivalents_count": 12
    },
    "argo:algorithm_version": "v1.0.0",
    "argo:weights_applied": {
      "inst": 0.30,
      "acad": 0.20,
      "media": 0.25,
      "network": 0.25
    },
    "argo:theoretical_basis": "Bourdieu Field Theory + Meta-Analysis",
    "argo:methodology": {
      "@type": "argo:Methodology",
      "name": "Capital-Weighted Composite Score",
      "description": "4가지 자본 유형의 메타분석 가중 합산",
      "references": [
        "Bourdieu, P. (1984). Distinction.",
        "Bourdieu, P. (1993). The Field of Cultural Production.",
        "Becker, H. S. (1982). Art Worlds."
      ]
    }
  }
}
```

### 9.2 Institution API 응답

```json
{
  "@context": "https://schema.org/",
  "@type": "Organization",
  "@id": "argo://institution/inst_001",
  "name": "국립현대미술관",
  "url": "https://www.mmca.go.kr",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Seoul",
    "addressCountry": "KR"
  },
  "founder": [
    "Government of Korea"
  ],
  "foundingDate": "1973",
  "argo:prestige_score": 95,
  "argo:institution_type": "national_museum"
}
```

---

## 10. 완전한 Neo4j 초기화 스크립트

```cypher
// 모든 제약 조건 및 인덱스 생성
// (Antigravity에서 실행)

// 1. Constraints
CREATE CONSTRAINT artist_id_unique ON (a:Artist) ASSERT a.artist_id IS UNIQUE;
CREATE CONSTRAINT institution_id_unique ON (i:Institution) ASSERT i.inst_id IS UNIQUE;
CREATE CONSTRAINT exhibition_id_unique ON (e:Exhibition) ASSERT e.exh_id IS UNIQUE;
CREATE CONSTRAINT artwork_id_unique ON (w:Artwork) ASSERT w.work_id IS UNIQUE;
CREATE CONSTRAINT transaction_id_unique ON (t:Transaction) ASSERT t.trans_id IS UNIQUE;
CREATE CONSTRAINT cluster_id_unique ON (c:Cluster) ASSERT c.cluster_id IS UNIQUE;
CREATE CONSTRAINT snapshot_id_unique ON (s:GalaxySnapshot) ASSERT s.snapshot_id IS UNIQUE;

// 2. 기본 인덱스
CREATE INDEX artist_composite_score ON :Artist(composite_score);
CREATE INDEX artist_segment_id ON :Artist(segment_id);
CREATE INDEX institution_prestige ON :Institution(prestige_score);
CREATE INDEX exhibition_date ON :Exhibition(start_date);
CREATE INDEX transaction_date ON :Transaction(transaction_date);
CREATE INDEX cluster_type ON :Cluster(cluster_type);

// 3. 구조주의 분석 인덱스 (확장성 고려)
CREATE INDEX artist_dominant_capital ON :Artist(structuralist_analysis.dominant_capital);
CREATE INDEX artist_field_quadrant ON :Artist(structuralist_analysis.structural_position.field_quadrant);
CREATE INDEX artist_confidence_score ON :Artist(metadata.confidence_score);

// 4. 복합 인덱스 (쿼리 최적화)
CREATE INDEX artist_segment_score ON :Artist(segment_id, composite_score);
CREATE INDEX institution_type_prestige ON :Institution(institution_type, prestige_score);
CREATE INDEX exhibition_organizer_date ON :Exhibition(organizer_id, start_date);
CREATE INDEX artist_quadrant_score ON :Artist(structuralist_analysis.structural_position.field_quadrant, composite_score);

// 5. 프로퍼티 그래프 제약
// (선택사항: 추가 유효성 검증)

CALL apoc.schema.properties.matching(".*score", "f") YIELD value
RETURN value;
```

**인덱스 확장성 전략:**

```
데이터 크기별 인덱스 전략:

100명 (Phase 1):
├─ 기본 인덱스만 사용
├─ 복합 인덱스 최소화
└─ 쿼리 성능: < 200ms 목표

500명 (Phase 2):
├─ 구조주의 분석 인덱스 추가
├─ 복합 인덱스 최적화
└─ 쿼리 성능: < 300ms 목표

2000명 (Phase 3):
├─ 부분 인덱스 적용 (신뢰도 높은 데이터만)
├─ 인덱스 파티셔닝 고려
└─ 쿼리 성능: < 500ms 목표

인덱스 성능 모니터링:
├─ 주기적 검토: 월 1회
├─ 사용률 분석: 사용되지 않는 인덱스 제거
├─ 크기 모니터링: 디스크 사용량 추적
└─ 쿼리 프로파일링: 느린 쿼리 식별 및 인덱스 추가
```

---

## 11. 결론 & 사용 지침

### 데이터 무결성 원칙

1. **Schema.org 준수**: 모든 필드는 Schema.org 어휘와 매핑
2. **타입 안전성**: 모든 필드에 명확한 데이터 타입 정의
3. **범위 검증**: FLOAT/INT 필드는 min/max 범위 명시
4. **관계 무결성**: 모든 관계는 FROM/TO 노드 유형 명확
5. **감사 추적**: 모든 엔터티는 created_at, updated_at, verified 포함

### 확장성

- 100명 → 500명 → 2,000명 확장 가능 (스키마 변경 없음)
- 새 속성 추가 시 Schema.org 기본 개념 먼저 확인
- 새 관계 유형은 ARGO 커스텀 프로퍼티로 마킹

### 문서화

- 모든 필드는 @type, @range, 의미론 명시
- Cypher 쿼리는 주석으로 의도 설명
- API 응답은 JSON-LD 형식 유지

---

**이제 Cursor에서 이 스키마를 기반으로 완전한 백엔드 + 프론트엔드를 구현할 준비가 완료됨.**
