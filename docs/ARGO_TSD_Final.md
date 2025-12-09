# ARGO: 한국 미술계 구조 분석 엔진
## Technical Specification Document (TSD)
### 최종 통합 기술 명세서

**Version**: 2.0  
**Last Updated**: 2025-12-08  
**Status**: Production Ready  
**Document Owner**: Engineering & Architecture Team

---

## Executive Summary

**TSD는 BRD(비즈니스) + PRD(제품) + 스키마(데이터)**의 통합 기술 명세다.

**동기화 원칙:**
- BRD의 비즈니스 목표 → PRD의 기능 요구사항 → TSD의 기술 구현
- 모든 데이터 엔터티는 Schema.org 표준 기반 (국제 호환성)
- 모든 API는 JSON-LD 형식 (의미론적 웹 표준)
- 모든 쿼리는 Cypher 공개 (투명성 원칙)

---

## GCP 프로젝트 정보

**프로젝트 이름**: ARTDRIVE  
**프로젝트 ID**: artdrive1208  
**리전**: asia-northeast3 (서울)

### Firebase 설정
- **API Key**: AIzaSyC4XxekCt6Ob1ufyuRucrHMqXvEInkCpsg
- **Auth Domain**: artdrive1208.firebaseapp.com
- **Project ID**: artdrive1208
- **Storage Bucket**: artdrive1208.firebasestorage.app
- **Messaging Sender ID**: 55248184822
- **App ID**: 1:55248184822:web:cef02018a4af9dbbdd93d7
- **Measurement ID**: G-DJ2C6DBJ2Q

### 초기 도메인
- **프론트엔드**: https://artdrive1208.web.app
- **백엔드 API**: https://artdrive1208-api-xxx.run.app (Cloud Run 자동 생성)
- **향후 커스텀 도메인**: argo.art, api.argo.art (추가 예정)

---

## 1. 아키텍처 개요

### 1.1 3계층 통합 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                   프론트엔드 (Presentation)              │
│   Vite + React 18 + Three.js (3D 갤럭시 시각화)         │
│   ├─ 홈화면: 갤럭시 (60% 캔버스)                        │
│   ├─ 좌패널: 필터 & 통계 (20%)                         │
│   ├─ 우패널: 선택정보 (20%)                            │
│   └─ 8개 섹션 (분석, 군집, 이상치, 방법론, 비교, 프로필)
└─────────────────────────────────────────────────────────┘
                          ↓ (REST API)
┌─────────────────────────────────────────────────────────┐
│                    백엔드 (Business Logic)               │
│   FastAPI + Python 3.10+ (고성능 비동기 처리)           │
│   ├─ Artist API (/api/artists)                          │
│   ├─ Institution API (/api/institutions)                │
│   ├─ Cluster API (/api/clusters)                        │
│   ├─ Transaction API (/api/transactions)                │
│   ├─ Analysis API (/api/analysis/centrality)            │
│   ├─ Anomaly API (/api/anomalies)                       │
│   └─ Search API (/api/search)                           │
└─────────────────────────────────────────────────────────┘
                          ↓ (Cypher Query)
┌─────────────────────────────────────────────────────────┐
│                 데이터베이스 (Data Layer)                 │
│   Neo4j Aura Cloud (그래프 데이터베이스)                 │
│   ├─ 7개 노드 타입 (Artist, Institution, Exhibition...) │
│   ├─ 9개 관계 타입 (COLLABORATED_WITH, AFFILIATED_WITH..)
│   ├─ 100명 + 1,200건 거래 + 500개 전시                 │
│   └─ 인덱스 & 제약조건 (성능 최적화)                   │
└─────────────────────────────────────────────────────────┘
```

### 1.2 데이터 흐름도

```
사용자 입력 (필터 선택)
    ↓
프론트엔드 상태 관리 (React Hooks)
    ↓
백엔드 API 호출 (FastAPI)
    ↓
Cypher 쿼리 생성 (동적)
    ↓
Neo4j 실행
    ↓
결과 JSON-LD 변환 (Schema.org)
    ↓
프론트엔드 렌더링 (Three.js + React)
    ↓
사용자 화면 (3D 갤럭시 + 정보 패널)
```

---

## 2. 데이터베이스 계층 (Neo4j)

### 2.1 엔터티 정의 (Schema.org 매핑)

#### 2.1.1 Artist (Person + CreativeWork)

```cypher
(:Artist {
  // === Schema.org Person 기반 ===
  artist_id: STRING @id,                    // person.identifier
  name: STRING,                             // person.name
  alternativeName: STRING,                  // 영문이름, 별명
  birth_year: INT,                          // person.birthDate
  url: STRING,                              // person.url (공식 웹사이트)
  sameAs: [STRING],                         // 외부 프로필 (Wikipedia, Artsy)
  
  // === 주소 정보 ===
  address: {
    streetAddress: STRING,
    addressLocality: STRING,                // 도시 (Seoul, Busan, etc)
    addressRegion: STRING,                  // 지역
    postalCode: STRING,
    addressCountry: STRING                  // KR
  },
  
  // === 연락처 ===
  contactPoint: {
    telephone: STRING,
    email: STRING
  },
  
  // === 경력 정보 ===
  jobTitle: STRING,                         // "교수", "큐레이터", "작가"
  workLocation: STRING,                     // 현재 소속 기관명
  
  // === ARGO 커스텀: 세그먼트 분류 ===
  segment_id: STRING,                       // "contemporary_monochrome_KR"
  segment_metadata: {
    genre: STRING,                          // "monochrome_painting", "abstract"
    geographic_base: STRING,                // "Seoul", "Busan", "International"
    generation: STRING                      // "1960s", "1980s", "1990s"
  },
  
  // === 경력 단계 ===
  career_stage: ENUM ["early", "mid", "late"],
  
  // === 4개 구조 레이어 점수 ===
  scores: {
    // 1. 제도 레이어 (Institutional)
    inst_score: FLOAT @range(0, 100),
    inst_score_metadata: {
      museum_exhibitions: INT,
      biennale_participation: INT,
      public_support_count: INT,
      residency_count: INT
    },
    
    // 2. 학술 레이어 (Academic)
    acad_score: FLOAT @range(0, 100),
    acad_score_metadata: {
      citation_count: INT,
      catalog_mentions: INT,
      academic_publications: INT,
      research_emphasis: FLOAT @range(0, 1)
    },
    
    // 3. 담론 레이어 (Media/Discourse)
    media_score: FLOAT @range(0, 100),
    media_score_metadata: {
      article_count: INT,
      sentiment: FLOAT @range(-1, 1),
      media_mentions_trend: FLOAT,
      hype_ratio: FLOAT @range(0, 1)
    },
    
    // 4. 네트워크 레이어 (Social Capital)
    network_score: FLOAT @range(0, 100),
    network_score_metadata: {
      degree_centrality: FLOAT @range(0, 1),
      betweenness_centrality: FLOAT @range(0, 1),
      eigenvector_centrality: FLOAT @range(0, 1),
      bridge_potential: FLOAT @range(0, 1)
    }
  },
  
  // === 복합 점수 (4개 레이어 가중 평균) ===
  composite_score: FLOAT @range(0, 100),
  // 계산: (inst*0.3 + acad*0.2 + media*0.25 + network*0.25)
  composite_confidence: FLOAT @range(0, 1),  // 신뢰도

  // === 구조주의 분석 필드 (v1.0_structuralist 신규) ===
  structuralist_analysis: {
    // 지배적 자본 유형
    dominant_capital: ENUM ["institutional", "academic", "media", "network"],

    // 자본 구성 비율
    capital_composition: {
      institutional_ratio: FLOAT @range(0, 1),
      academic_ratio: FLOAT @range(0, 1),
      media_ratio: FLOAT @range(0, 1),
      network_ratio: FLOAT @range(0, 1)
    },

    // 구조적 위치 지표
    structural_position: {
      field_quadrant: ENUM ["Q1_established", "Q2_academic_elite", "Q3_media_star", "Q4_emerging"],
      position_stability: FLOAT @range(0, 1),     // 위치 안정성
      mobility_potential: FLOAT @range(0, 1)      // 이동 가능성
    },

    // 알고리즘 버전 (재현성)
    algorithm_version: STRING,                    // "v1.0_structuralist"
    weights_applied: {
      inst: FLOAT,    // 0.30
      acad: FLOAT,    // 0.20
      media: FLOAT,   // 0.25
      network: FLOAT  // 0.25
    },

    // 이론적 기반
    theoretical_basis: STRING,                    // "Bourdieu_Field_Theory"
    references: [STRING]                          // 학술 인용 목록
  },

  // === 3D 갤럭시 좌표 ===
  coordinates_3d: {
    x: FLOAT,                                // inst_score 정규화 (-10 ~ 10)
    y: FLOAT,                                // acad_score 정규화 (-10 ~ 10)
    z: FLOAT,                                // media_score 정규화 (-10 ~ 10)
    radius: FLOAT,                           // network_score 기반 (10 + score/5)
    computed_at: DATETIME,
    algorithm: STRING                        // "force_directed_3d", "PCA"
  },
  
  // === 메타데이터 ===
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    data_source: [STRING],                  // "ARKO", "KCI", "web_crawl"
    confidence_score: FLOAT @range(0, 1),   // 데이터 신뢰도
    verified: BOOLEAN
  }
})
```

#### 2.1.2 Institution (Organization)

```cypher
(:Institution {
  // === Schema.org Organization 기반 ===
  inst_id: STRING @id,
  name: STRING,
  alternateName: STRING,
  
  // === 기관 유형 ===
  institution_type: ENUM [
    "national_museum",                      // 국립미술관
    "municipal_museum",                     // 시립미술관
    "university",                           // 대학
    "biennale",                             // 비엔날레
    "gallery",                              // 갤러리
    "alternative_space",                    // 대안공간
    "foundation",                           // 재단
    "art_school"                            // 미술학교
  ],
  
  // === 주소 정보 ===
  address: {
    streetAddress: STRING,
    addressLocality: STRING,                // Seoul, Busan, etc
    addressRegion: STRING,
    postalCode: STRING,
    addressCountry: STRING,
    geo: {
      latitude: FLOAT,
      longitude: FLOAT
    }
  },
  
  // === 연락처 ===
  telephone: STRING,
  email: STRING,
  url: STRING,
  sameAs: [STRING],
  
  // === 기관 정보 ===
  founded_year: INT,
  prestige_score: INT @range(0, 100),      // 기관 위상 점수
  prestige_metadata: {
    international_recognition: FLOAT,
    publication_count: INT,
    exhibition_size: INT,
    annual_budget_level: ENUM ["large", "medium", "small"]
  },
  
  institution_metadata: {
    specialization: [STRING],               // ["contemporary", "traditional", "media"]
    geographic_focus: STRING,               // "Seoul", "National", "International"
    audience_size: INT,
    annual_exhibitions: INT,
    public_funding_ratio: FLOAT @range(0, 1)
  },
  
  // === 리더십 ===
  leadership: {
    director_name: STRING,
    director_tenure_years: INT,
    key_curators: [STRING]
  },
  
  // === 메타데이터 ===
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    data_source: STRING,
    verified: BOOLEAN
  }
})
```

#### 2.1.3 Exhibition (Event)

```cypher
(:Exhibition {
  // === Schema.org Event 기반 ===
  exh_id: STRING @id,
  title: STRING,
  description: STRING,
  
  // === 날짜 정보 ===
  start_date: DATE,
  end_date: DATE,
  exhibition_duration_days: INT,
  
  // === 장소 정보 ===
  location: {
    name: STRING,
    geo: {
      latitude: FLOAT,
      longitude: FLOAT
    }
  },
  
  // === 주최 기관 ===
  organizer_id: STRING @refers(Institution),
  
  // === 참여 정보 ===
  estimated_visitors: INT,
  
  // === ARGO 커스텀 ===
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
  
  curation: {
    curator_ids: [STRING],
    curatorial_statement: STRING,
    theme: STRING
  },
  
  participating_artists: [STRING] @refers(Artist),
  participating_artists_count: INT,
  
  exhibition_scale: ENUM ["small", "medium", "large"],
  artworks_count: INT,
  
  significance: ENUM ["local", "regional", "national", "international"],
  
  // === 메타데이터 ===
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    data_source: STRING,
    verified: BOOLEAN
  }
})
```

#### 2.1.4 Artwork (CreativeWork)

```cypher
(:Artwork {
  work_id: STRING @id,
  title: STRING,
  creator_id: STRING @refers(Artist),
  
  creation_year: INT,
  description: STRING,
  
  medium: STRING,                           // "acrylic on canvas"
  dimensions: {
    height_cm: FLOAT,
    width_cm: FLOAT,
    depth_cm: FLOAT
  },
  
  series_name: STRING,
  series_number: INT,
  
  image_url: STRING,
  image_digital_representation: BOOLEAN,
  
  artwork_metadata: {
    genre: STRING,
    style: STRING,
    technique: [STRING],
    subject_matter: [STRING]
  },
  
  market: {
    estimated_value_krw: FLOAT,
    estimated_value_usd: FLOAT,
    valuation_confidence: FLOAT,
    market_activity: INT
  },
  
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    data_source: STRING
  }
})
```

#### 2.1.5 Transaction (MonetaryAmount + Action)

```cypher
(:Transaction {
  trans_id: STRING @id,
  work_id: STRING @refers(Artwork),
  seller_id: STRING,                        // 갤러리/경매사
  
  transaction_type: ENUM [
    "auction",
    "private_sale",
    "gallery_sale",
    "institutional_acquisition",
    "donation"
  ],
  
  transaction_date: DATE,
  venue: STRING,
  venue_id: STRING @refers(Institution),
  
  // === 가격 정보 ===
  price: {
    currency: ENUM ["KRW", "USD", "EUR"],
    estimate_low: FLOAT,
    estimate_high: FLOAT,
    hammer_price: FLOAT,
    buyer_premium_percent: FLOAT,
    final_price_with_premium: FLOAT
  },
  
  // === 거래 컨텍스트 ===
  transaction_context: {
    lot_number: STRING,
    sequence_number: INT,
    bidders_count: INT,
    sold: BOOLEAN,
    unsold_reason: STRING
  },
  
  // === 시장 분석용 ===
  market_analysis: {
    segment_id: STRING,
    artist_segment_percentile: FLOAT @range(0, 100),
    price_estimate_accuracy: FLOAT @range(0, 1),
    anomaly_score: FLOAT,
    is_outlier: BOOLEAN
  },
  
  // === 메타데이터 ===
  metadata: {
    created_at: DATETIME,
    data_source: STRING,
    verified: BOOLEAN
  }
})
```

#### 2.1.6 Cluster (Graph Pattern)

```cypher
(:Cluster {
  cluster_id: STRING @id,
  name: STRING,
  description: STRING,
  
  cluster_type: ENUM [
    "institution_based",                    // 같은 기관 출신
    "geographic",                           // 같은 지역
    "genre",                                // 같은 장르
    "generation",                           // 같은 세대
    "network_algorithmic",                  // Louvain 탐지
    "thematic"                              // 같은 주제/운동
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
  
  characteristics: {
    avg_inst_score: FLOAT,
    avg_acad_score: FLOAT,
    avg_media_score: FLOAT,
    avg_network_score: FLOAT,
    avg_composite_score: FLOAT,
    
    primary_score_driver: ENUM [
      "inst_score", "acad_score", "media_score", "network_score"
    ],
    
    secondary_score_driver: ENUM [
      "inst_score", "acad_score", "media_score", "network_score"
    ]
  },
  
  neighboring_clusters: [{
    cluster_id: STRING,
    distance: FLOAT,
    interaction_strength: FLOAT @range(0, 1),
    shared_members: INT
  }],
  
  dominant_institutions: [{
    inst_id: STRING,
    name: STRING,
    artist_count: INT,
    influence_ratio: FLOAT
  }],
  
  // === 메타데이터 ===
  metadata: {
    created_at: DATETIME,
    updated_at: DATETIME,
    algorithm_version: STRING,
    convergence_ratio: FLOAT
  }
})
```

#### 2.1.7 GalaxySnapshot (DataSet)

```cypher
(:GalaxySnapshot {
  snapshot_id: STRING @id,
  snapshot_date: DATE,
  description: STRING,
  created_at: DATETIME,
  
  // === 갤럭시 통계 ===
  galaxy_statistics: {
    total_artists: INT,
    total_institutions: INT,
    total_exhibitions: INT,
    total_artworks: INT,
    total_transactions: INT,
    total_clusters: INT
  },
  
  // === 구조 메트릭 ===
  structure_metrics: {
    entropy: FLOAT @range(0, 1),
    density: FLOAT @range(0, 1),
    clustering_coefficient: FLOAT,
    average_path_length: FLOAT,
    diameter: INT
  },
  
  // === 분포 정보 ===
  generational_distribution: {
    "1950s": INT,
    "1960s": INT,
    "1970s": INT,
    "1980s": INT,
    "1990s": INT,
    "2000s": INT,
    "2010s": INT
  },
  
  geographic_distribution: {
    "Seoul": INT,
    "Busan": INT,
    "Daegu": INT,
    "Incheon": INT,
    "Daejeon": INT,
    "Gwangju": INT,
    "Ulsan": INT,
    "International": INT
  },
  
  genre_distribution: {
    "monochrome": INT,
    "abstract": INT,
    "realism": INT,
    "conceptual": INT,
    "media_art": INT,
    "sculpture": INT,
    "installation": INT,
    "performance": INT
  },
  
  // === 계산 정보 ===
  computation: {
    algorithm: STRING,
    iterations: INT,
    computation_time_seconds: FLOAT,
    convergence_ratio: FLOAT @range(0, 1),
    hardware_spec: STRING
  },
  
  // === 메타데이터 ===
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

### 2.2 관계 정의 (9가지)

```cypher
// 1. Artist ↔ Artist: 협력 관계
(:Artist)-[:COLLABORATED_WITH {
  strength: FLOAT @range(0, 1),
  exhibition_count: INT,
  collaboration_type: ENUM [
    "co_exhibition",
    "joint_work",
    "mentorship",
    "peer_network",
    "institutional_connection"
  ],
  first_collaboration_year: INT,
  last_collaboration_year: INT,
  continuous: BOOLEAN
}]->(:Artist)

// 2. Artist ↔ Institution: 소속 관계
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

// 3. Artist ↔ Exhibition: 참여 관계
(:Artist)-[:PARTICIPATED_IN {
  role: ENUM ["artist", "curator", "organizer"],
  artworks_count: INT,
  featured: BOOLEAN,
  catalog_mentioned: BOOLEAN,
  year: INT
}]->(:Exhibition)

// 4. Artwork ↔ Exhibition: 전시 관계
(:Artwork)-[:DISPLAYED_IN {
  display_status: ENUM ["exhibited", "featured", "catalog_only"],
  position_in_exhibition: INT
}]->(:Exhibition)

// 5. Artwork ↔ Transaction: 거래 관계
(:Artwork)-[:SOLD_IN {
  transaction_sequence: INT,
  lot_number: STRING
}]->(:Transaction)

// 6. Artist ↔ Cluster: 소속 관계
(:Artist)-[:BELONGS_TO {
  membership_strength: FLOAT @range(0, 1),
  distance_to_center: FLOAT,
  influence_in_cluster: FLOAT
}]->(:Cluster)

// 7. Institution ↔ Exhibition: 주최 관계
(:Institution)-[:ORGANIZED_EXHIBITION {
  count: INT,
  primary_curator: STRING
}]->(:Exhibition)

// 8. Cluster ↔ Cluster: 인접 관계
(:Cluster)-[:ADJACENT_TO {
  distance: FLOAT,
  interaction_strength: FLOAT @range(0, 1),
  shared_members: INT,
  interaction_type: ENUM ["hierarchical", "peer", "satellite"]
}]->(:Cluster)

// 9. Institution ↔ Cluster: 지배 관계
(:Institution)-[:DOMINATES_CLUSTER {
  influence_ratio: FLOAT @range(0, 1),
  member_count: INT,
  influence_tier: ENUM ["primary", "secondary", "tertiary"]
}]->(:Cluster)
```

### 2.3 인덱스 & 제약조건 (확장성 고려 보완)

```cypher
// === PRIMARY KEY 제약조건 ===
CREATE CONSTRAINT artist_id_unique ON (a:Artist) ASSERT a.artist_id IS UNIQUE;
CREATE CONSTRAINT institution_id_unique ON (i:Institution) ASSERT i.inst_id IS UNIQUE;
CREATE CONSTRAINT exhibition_id_unique ON (e:Exhibition) ASSERT e.exh_id IS UNIQUE;
CREATE CONSTRAINT artwork_id_unique ON (w:Artwork) ASSERT w.work_id IS UNIQUE;
CREATE CONSTRAINT transaction_id_unique ON (t:Transaction) ASSERT t.trans_id IS UNIQUE;
CREATE CONSTRAINT cluster_id_unique ON (c:Cluster) ASSERT c.cluster_id IS UNIQUE;
CREATE CONSTRAINT snapshot_id_unique ON (s:GalaxySnapshot) ASSERT s.snapshot_id IS UNIQUE;

// === 성능 인덱스 (기본) ===
CREATE INDEX artist_composite_score ON :Artist(composite_score);
CREATE INDEX artist_segment_id ON :Artist(segment_id);
CREATE INDEX artist_career_stage ON :Artist(career_stage);
CREATE INDEX institution_prestige ON :Institution(prestige_score);
CREATE INDEX institution_type ON :Institution(institution_type);
CREATE INDEX exhibition_date ON :Exhibition(start_date);
CREATE INDEX exhibition_type ON :Exhibition(exhibition_type);
CREATE INDEX transaction_date ON :Transaction(transaction_date);
CREATE INDEX transaction_anomaly ON :Transaction(market_analysis.is_outlier);
CREATE INDEX cluster_type ON :Cluster(cluster_type);

// === 구조주의 분석 인덱스 (확장성 고려) ===
CREATE INDEX artist_dominant_capital ON :Artist(structuralist_analysis.dominant_capital);
CREATE INDEX artist_field_quadrant ON :Artist(structuralist_analysis.structural_position.field_quadrant);
CREATE INDEX artist_confidence_score ON :Artist(metadata.confidence_score);

// === 복합 인덱스 (쿼리 최적화) ===
CREATE INDEX artist_segment_score ON :Artist(segment_id, composite_score);
CREATE INDEX institution_type_prestige ON :Institution(institution_type, prestige_score);
CREATE INDEX exhibition_organizer_date ON :Exhibition(organizer_id, start_date);
CREATE INDEX artist_quadrant_score ON :Artist(structuralist_analysis.structural_position.field_quadrant, composite_score);

// === 확장성 최적화 전략 ===
// 100명 → 500명 → 2000명 확장 시 인덱스 전략:
// 1. 쿼리 프로파일링: 느린 쿼리 식별 및 인덱스 추가
// 2. 인덱스 선택성 모니터링: 선택성이 낮은 인덱스 제거 고려
// 3. 복합 인덱스 최적화: 자주 함께 사용되는 필드 조합
// 4. 부분 인덱스: 특정 조건의 노드만 인덱싱 (예: confidence_score > 0.85)
```

**인덱스 성능 모니터링:**

```
주기적 검토 (월 1회):
├─ 인덱스 사용률 확인 (사용되지 않는 인덱스 제거)
├─ 인덱스 크기 모니터링 (디스크 사용량)
├─ 쿼리 성능 분석 (느린 쿼리 식별)
└─ 인덱스 선택성 검토 (낮은 선택성 인덱스 최적화)

확장 시점별 인덱스 전략:
├─ 100명: 기본 인덱스만 (현재 상태)
├─ 500명: 구조주의 분석 인덱스 추가
└─ 2000명: 부분 인덱스 및 복합 인덱스 최적화
```

### 2.4 데이터 버전 관리 전략 (신규)

#### 2.4.1 스키마 버전 관리

**버전 관리 원칙:**

```
스키마 버전 형식: v{Major}.{Minor}.{Patch}
├─ Major: 호환되지 않는 변경 (예: 필드 삭제)
├─ Minor: 호환되는 추가 (예: 새 필드 추가)
└─ Patch: 버그 수정 (예: 타입 수정)

현재 버전: v1.0.0 (초기 릴리스)
```

**스키마 변경 프로세스:**

```
Step 1: 변경 제안 (Schema Change Proposal)
├─ 변경 사유 문서화
├─ 영향도 분석 (기존 데이터, API, 쿼리)
└─ 마이그레이션 계획 수립

Step 2: 개발 환경 테스트
├─ 새 스키마 적용
├─ 마이그레이션 스크립트 테스트
└─ 데이터 무결성 검증

Step 3: 스테이징 환경 배포
├─ 스테이징 데이터 마이그레이션
├─ API 호환성 테스트
└─ 성능 테스트

Step 4: 프로덕션 배포
├─ 백업 생성
├─ 마이그레이션 스크립트 실행
├─ 롤백 계획 준비
└─ 검증 및 모니터링
```

#### 2.4.2 데이터 버전 관리

**데이터 버전 필드:**

```cypher
// 모든 엔터티에 버전 정보 추가
metadata: {
  created_at: DATETIME,
  updated_at: DATETIME,
  data_version: STRING,        // "v1.0.0"
  schema_version: STRING,      // "v1.0.0"
  migration_history: [STRING]  // 마이그레이션 이력
}
```

**데이터 마이그레이션 전략:**

```
마이그레이션 유형:
├─ Forward Migration: 스키마 업그레이드
├─ Backward Migration: 스키마 다운그레이드 (롤백)
└─ Data Migration: 데이터 변환 (예: 필드명 변경)

마이그레이션 스크립트:
├─ Cypher 스크립트로 작성
├─ 트랜잭션 단위 실행 (원자성 보장)
├─ 롤백 가능 (실패 시 자동 롤백)
└─ 버전 관리 (Git 저장소)

마이그레이션 실행:
├─ 자동 실행: 스키마 버전 불일치 감지 시
├─ 수동 실행: 관리자 명령으로 실행
└─ 검증: 마이그레이션 후 데이터 무결성 검증
```

#### 2.4.3 스냅샷 버전 관리

**GalaxySnapshot 버전 관리:**

```
스냅샷 버전 형식: snapshot_{YYYYMMDD}_{version}
예: snapshot_20251208_v1.0.0

버전 관리 전략:
├─ 일일 스냅샷: 매일 자동 생성
├─ 주간 스냅샷: 매주 일요일 보관 (30일간)
├─ 월간 스냅샷: 매월 1일 보관 (1년간)
└─ 이벤트 스냅샷: 주요 데이터 업데이트 시 수동 생성

스냅샷 비교:
├─ 버전 간 비교: 스냅샷 간 차이 분석
├─ 변경 사항 추적: 작가 추가/삭제, 점수 변경
└─ 시계열 분석: 시간에 따른 구조 변화 추적
```

---

## 3. 백엔드 API 계층 (FastAPI)

### 3.1 API 설계

```
Base URL: https://artdrive1208-api-xxx.run.app/v1
(초기: Cloud Run 자동 생성 도메인)
(향후: https://api.argo.art/v1 - 커스텀 도메인 추가 예정)

인증: JWT Token (Authorization: Bearer <token>)
응답 형식: JSON-LD (Schema.org 표준)
오류 처리: HTTP Status Code + JSON 에러 메시지
```

### 3.2 API 엔드포인트

#### 3.2.1 작가 관련 API

```
GET /api/artists
  설명: 모든 작가 조회 (페이지네이션)
  쿼리 파라미터:
    - page: INT (기본값: 1)
    - limit: INT (기본값: 20, 최대: 100)
    - segment_id: STRING (필터)
    - career_stage: ENUM (필터)
    - min_score: FLOAT (필터)
  응답:
    200: { artists: Artist[], total: INT, page: INT }
    400: { error: "Invalid parameter" }

GET /api/artists/{artist_id}
  설명: 특정 작가 상세 정보 + 모든 관계
  응답:
    200: {
      artist: Artist (상세),
      affiliated_institutions: Institution[],
      collaborators: Artist[],
      exhibitions: Exhibition[],
      artworks: Artwork[],
      cluster: Cluster
    }
    404: { error: "Artist not found" }

GET /api/artists/{artist_id}/network
  설명: 작가의 1홉/2홉 네트워크 그래프
  쿼리 파라미터:
    - depth: INT (1 또는 2)
  응답:
    200: {
      nodes: [{ id, name, score, type }],
      edges: [{ source, target, strength, type }]
    }

POST /api/artists/search
  설명: 전문 검색 (이름, 기관, 세그먼트 등)
  요청 본문:
    { query: STRING, filters: {...} }
  응답:
    200: { results: Artist[], count: INT }

GET /api/artists/{artist_id}/market
  설명: 작가의 시장 정보 (거래 이력, 가격 추이)
  응답:
    200: {
      transactions: Transaction[],
      price_trend: { year: [price_avg] },
      market_percentile: FLOAT
    }
```

#### 3.2.2 기관 관련 API

```
GET /api/institutions
  설명: 모든 기관 조회
  쿼리 파라미터:
    - type: ENUM (필터)
    - city: STRING (필터)
  응답:
    200: { institutions: Institution[], total: INT }

GET /api/institutions/{inst_id}
  설명: 기관 상세 정보
  응답:
    200: {
      institution: Institution,
      affiliated_artists: Artist[],
      organized_exhibitions: Exhibition[],
      member_clusters: Cluster[]
    }

GET /api/institutions/{inst_id}/benchmarking
  설명: 기관 벤치마킹 (동종 기관과 비교)
  응답:
    200: {
      self: Institution,
      peers: Institution[],
      metrics: {
        prestige_rank: INT,
        exhibition_frequency: INT,
        artist_diversity: FLOAT
      }
    }
```

#### 3.2.3 갤럭시 & 분석 API

```
GET /api/galaxy-snapshot
  설명: 현재 갤럭시 스냅샷 (통계, 구조 메트릭)
  응답:
    200: GalaxySnapshot

GET /api/clusters
  설명: 모든 군집 조회
  응답:
    200: { clusters: Cluster[], total: INT }

GET /api/clusters/{cluster_id}
  설명: 군집 상세 정보
  응답:
    200: {
      cluster: Cluster,
      members: Artist[],
      neighboring_clusters: Cluster[]
    }

POST /api/analysis/centrality
  설명: 중심성 계산 (Degree, Betweenness, Eigenvector)
  요청 본문:
    { measure: ENUM ["degree", "betweenness", "eigenvector"] }
  응답:
    200: [
      { artist_id: STRING, name: STRING, score: FLOAT, rank: INT }
    ]

POST /api/analysis/community-detection
  설명: Louvain 커뮤니티 탐지
  응답:
    200: {
      clusters: Cluster[],
      modularity: FLOAT,
      algorithm_version: STRING
    }

GET /api/anomalies
  설명: 이상치 탐지 (거래 가격)
  쿼리 파라미터:
    - segment_id: STRING (필터)
    - confidence: FLOAT (기본값: 0.8)
  응답:
    200: [
      {
        transaction_id: STRING,
        artist_id: STRING,
        anomaly_score: FLOAT,
        hypothesis: [{ text: STRING, confidence: FLOAT }]
      }
    ]

GET /api/search
  설명: 통합 검색 (작가, 기관, 전시)
  쿼리 파라미터:
    - q: STRING
    - type: ENUM ["artist", "institution", "exhibition", "all"]
  응답:
    200: { results: [] (mixed type) }
```

### 3.3 응답 스키마 (JSON-LD) - 구조주의 확장

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
    "addressCountry": "KR"
  },

  "jobTitle": "Professor",

  "argo:scores": {
    "argo:inst_score": 82,
    "argo:acad_score": 68,
    "argo:media_score": 75,
    "argo:network_score": 71,
    "argo:composite_score": 74.15,
    "argo:composite_confidence": 0.92
  },

  "argo:structuralist_analysis": {
    "dominant_capital": "institutional",
    "capital_composition": {
      "institutional_ratio": 0.28,
      "academic_ratio": 0.23,
      "media_ratio": 0.25,
      "network_ratio": 0.24
    },
    "structural_position": {
      "field_quadrant": "Q1_established",
      "position_stability": 0.85,
      "mobility_potential": 0.15
    }
  },

  "argo:methodology": {
    "version": "v1.0_structuralist",
    "weights": {
      "institutional": 0.30,
      "academic": 0.20,
      "media": 0.25,
      "network": 0.25
    },
    "theoretical_basis": "Bourdieu_Field_Theory",
    "references": [
      "Bourdieu, P. (1984). Distinction: A Social Critique of the Judgement of Taste",
      "Bourdieu, P. (1993). The Field of Cultural Production",
      "Fraiberger, S. et al. (2018). Quantifying reputation and success in art. Science"
    ]
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
  }
}
```

### 3.4 API 버전 관리 전략 (신규)

#### 3.4.1 버전 관리 원칙

**버전 형식:**

```
URL 기반 버전 관리:
├─ Base URL: https://artdrive1208-api-xxx.run.app/v1 (초기)
├─ 향후 커스텀 도메인: https://api.argo.art/v1
├─ 버전 형식: v{Major}.{Minor}
└─ 예: /v1/artists, /v2/artists

현재 버전: v1.0 (초기 릴리스)
```

**버전 변경 규칙:**

```
Major 버전 (v1 → v2):
├─ 호환되지 않는 변경 (Breaking Changes)
├─ 예: 필드 삭제, 필드 타입 변경, 엔드포인트 삭제
└─ 마이그레이션 가이드 제공 필수

Minor 버전 (v1.0 → v1.1):
├─ 호환되는 추가 (Non-Breaking Changes)
├─ 예: 새 필드 추가, 새 엔드포인트 추가
└─ 기존 클라이언트 영향 없음

Patch 버전 (v1.0.0 → v1.0.1):
├─ 버그 수정 (내부 변경)
└─ API 응답 형식 변경 없음
```

#### 3.4.2 하위 호환성 보장

**하위 호환성 체크리스트:**

```
✅ 호환되는 변경:
├─ 새 필드 추가 (기존 클라이언트는 무시 가능)
├─ 새 엔드포인트 추가
├─ 선택적 파라미터 추가
├─ 응답에 새 필드 추가
└─ 에러 메시지 개선

❌ 호환되지 않는 변경:
├─ 필드 삭제
├─ 필드 타입 변경 (예: STRING → INT)
├─ 필수 파라미터 추가
├─ 엔드포인트 삭제
└─ HTTP 메서드 변경
```

**하위 호환성 보장 전략:**

```
1. 필드 Deprecation 프로세스:
   ├─ Deprecation 공지: 3개월 전 알림
   ├─ Deprecation 기간: 6개월간 유지
   ├─ 응답에 deprecation_warning 필드 추가
   └─ 문서에 대체 필드 안내

2. 엔드포인트 Deprecation 프로세스:
   ├─ Deprecation 공지: 6개월 전 알림
   ├─ Deprecation 기간: 12개월간 유지
   ├─ HTTP 410 Gone 응답 (Deprecation 기간 후)
   └─ 문서에 대체 엔드포인트 안내

3. 버전 공존 전략:
   ├─ 최신 버전: v2 (신규 개발 권장)
   ├─ 이전 버전: v1 (기존 클라이언트 지원)
   └─ 지원 기간: 최신 버전 출시 후 12개월
```

#### 3.4.3 버전 관리 프로세스

**버전 출시 프로세스:**

```
Step 1: 변경 제안 (API Change Proposal)
├─ 변경 사유 문서화
├─ 영향도 분석 (기존 클라이언트)
├─ 마이그레이션 가이드 작성
└─ 팀 리뷰 및 승인

Step 2: 개발 환경 테스트
├─ 새 버전 API 구현
├─ 기존 버전과 공존 테스트
├─ 하위 호환성 검증
└─ 마이그레이션 가이드 검증

Step 3: 스테이징 환경 배포
├─ 스테이징에 새 버전 배포
├─ 클라이언트 테스트
├─ 성능 테스트
└─ 문서 업데이트

Step 4: 프로덕션 배포
├─ 새 버전 배포 (기존 버전 유지)
├─ 점진적 트래픽 전환 (10% → 50% → 100%)
├─ 모니터링 강화
└─ 사용자 공지

Step 5: 이전 버전 Deprecation
├─ Deprecation 공지 (6개월 전)
├─ 사용자 마이그레이션 지원
├─ Deprecation 기간 유지 (12개월)
└─ 최종 제거
```

**버전 문서화:**

```
API 문서 구조:
├─ /docs/v1/: v1 API 문서 (현재 버전)
├─ /docs/v2/: v2 API 문서 (신규 버전)
├─ /docs/migration/: 마이그레이션 가이드
└─ /docs/changelog/: 변경 이력

변경 이력 형식:
├─ 날짜: 2025-12-08
├─ 버전: v1.1.0
├─ 변경 유형: Minor (호환되는 추가)
├─ 변경 내용: structuralist_analysis 필드 추가
└─ 영향도: 낮음 (기존 클라이언트 영향 없음)
```

---

## 4. 프론트엔드 계층 (React + Three.js)

### 4.1 컴포넌트 구조

```
src/
├─ components/
│  ├─ Galaxy3D.tsx (메인 Three.js 씬, 350줄)
│  ├─ LeftPanel.tsx (필터 & 통계, 200줄)
│  ├─ RightPanel.tsx (선택정보, 250줄)
│  ├─ Controls.tsx (키보드/마우스 제어, 150줄)
│  ├─ InfoOverlay.tsx (FPS, 카메라 정보, 100줄)
│  └─ Layout.tsx (전체 3패널 레이아웃, 80줄)
│
├─ hooks/
│  ├─ useGalaxy.ts (갤럭시 상태관리, 200줄)
│  ├─ useSelection.ts (선택 항목 상태, 100줄)
│  ├─ useFilter.ts (필터 상태, 150줄)
│  └─ useAPI.ts (API 호출, 200줄)
│
├─ utils/
│  ├─ colorMapping.ts (RGB 색상 매핑, 50줄)
│  ├─ coordinateTransform.ts (정규화, 100줄)
│  ├─ raycastSelection.ts (클릭 충돌감지, 80줄)
│  └─ apiClient.ts (API 클라이언트, 150줄)
│
├─ types/
│  └─ argo.ts (TypeScript 타입정의, 300줄)
│
├─ pages/
│  ├─ Home.tsx (갤럭시 홈화면)
│  ├─ Analysis.tsx (분석 대시보드)
│  ├─ Galaxy.tsx (군집 탐색)
│  ├─ Anomalies.tsx (이상치 분석)
│  ├─ Methodology.tsx (방법론)
│  ├─ Compare.tsx (비교 분석)
│  └─ Profile.tsx (사용자 프로필)
│
├─ styles/
│  ├─ globals.css (전역 스타일)
│  ├─ three-colors.css (3D 색상 팔레트)
│  └─ panels.css (패널 레이아웃)
│
├─ App.tsx (메인 라우터)
└─ main.tsx (진입점)
```

### 4.2 핵심 렌더링 로직

```typescript
// Galaxy3D.tsx (Three.js 렌더링)

const createParticleSystem = (artists: Artist[]) => {
  // 1. 기하구조 생성
  const geometry = new THREE.BufferGeometry();
  
  // 2. 위치 배열 (x, y, z 좌표)
  const positions = new Float32Array(artists.length * 3);
  artists.forEach((artist, i) => {
    positions[i*3] = artist.coordinates_3d.x;
    positions[i*3+1] = artist.coordinates_3d.y;
    positions[i*3+2] = artist.coordinates_3d.z;
  });
  geometry.setAttribute('position', 
    new THREE.BufferAttribute(positions, 3));
  
  // 3. 색상 배열 (R=inst, G=acad, B=media)
  const colors = new Uint8Array(artists.length * 3);
  artists.forEach((artist, i) => {
    colors[i*3] = artist.scores.inst_score;
    colors[i*3+1] = artist.scores.acad_score;
    colors[i*3+2] = artist.scores.media_score;
  });
  geometry.setAttribute('color',
    new THREE.BufferAttribute(colors, 3, true));
  
  // 4. 크기 배열 (반경 = 10 + network_score/5)
  const sizes = new Float32Array(artists.length);
  artists.forEach((artist, i) => {
    sizes[i] = 10 + (artist.scores.network_score / 5);
  });
  geometry.setAttribute('size',
    new THREE.BufferAttribute(sizes, 1));
  
  // 5. InstancedMesh로 렌더링 (성능 최적화)
  const material = new THREE.PointsMaterial({
    size: 5,
    sizeAttenuation: true,
    vertexColors: true,
    emissive: 0x000000
  });
  
  const points = new THREE.Points(geometry, material);
  return points;
};

// 렌더링 루프
const animate = () => {
  requestAnimationFrame(animate);
  
  // 카메라 제어
  controls.update();
  
  // 렌더링
  renderer.render(scene, camera);
};
```

### 4.3 상태 관리 (React Hooks)

```typescript
// useGalaxy.ts

const useGalaxy = () => {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [selectedArtist, setSelectedArtist] = useState<Artist | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null);
  const [filters, setFilters] = useState({
    segment_id: null,
    career_stage: null,
    region: null,
    min_score: 0,
    max_score: 100
  });
  
  // API 호출
  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('/api/artists', {
        params: filters
      });
      const data = await response.json();
      setArtists(data.artists);
    };
    
    fetchData();
  }, [filters]);
  
  return {
    artists,
    clusters,
    selectedArtist,
    setSelectedArtist,
    filters,
    setFilters
  };
};
```

---

## 5. 배포 아키텍처

### 5.1 인프라 구성

```
┌─────────────────────────────────────────────┐
│   Firebase Hosting (프론트엔드)              │
│   • React + Vite 빌드                        │
│   • Cloud CDN 자동 포함                      │
│   • 자동 HTTPS                               │
│   • 리전: 글로벌 엣지 네트워크              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Cloud Run (백엔드 API)                    │
│   • FastAPI + Python 3.10                   │
│   • 서버리스 자동 스케일링                    │
│   • 사용량 기반 과금                         │
│   • 리전: asia-northeast3 (서울)            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Cloud Memorystore (Redis 캐싱)             │
│   • API 응답 캐싱                            │
│   • TTL 관리                                 │
│   • 리전: asia-northeast3 (서울)            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Neo4j Aura (데이터베이스)                  │
│   • 외부 서비스 (GCP 외부)                   │
│   • 연결만 관리                              │
│   • 99.9% SLA 보장                           │
│   • 자동 백업                                │
└─────────────────────────────────────────────┘
```

### 5.2 배포 파이프라인

```
GitHub Push
    ↓
GitHub Actions (CI/CD) 또는 Cloud Build
├─ 테스트 실행 (Jest, Pytest)
├─ 빌드 (Vite, Python packaging)
├─ 린트 (ESLint, Pylint)
└─ 배포
    ├─ Firebase Hosting (프론트엔드)
    └─ Cloud Run (백엔드)
    ↓
Production 환경
├─ 프론트엔드: artdrive1208.web.app (Firebase Hosting)
│  └─ 향후: argo.art (커스텀 도메인)
├─ 백엔드: artdrive1208-api-xxx.run.app (Cloud Run)
│  └─ 향후: api.argo.art (커스텀 도메인)
└─ 데이터베이스: Neo4j Aura (AuraDB)
```

---

## 6. 성능 사양 & SLA

### 6.1 성능 목표

```
응답 시간:
├─ API 응답: < 200ms (90th percentile)
├─ 갤럭시 로딩: < 3초
├─ 검색: < 500ms
├─ 이상치 탐지: < 2초
└─ 3D 렌더링: 60 FPS

확장성:
├─ 동시 사용자: 100명 (Year 1)
├─ 월간활성사용자: 1,000명 (Year 1)
├─ 데이터 크기: 50MB (100명 + 1,200거래)
└─ 정확도: 신뢰도 점수 > 0.85

캐시 전략 (강화):
├─ Cloud CDN: 정적 자산 (JS, CSS, 이미지) - Firebase Hosting 자동 포함
├─ Cloud Memorystore (Redis 호환): API 응답 (TTL: 1시간)
│  ├─ 일반 API 응답: TTL 1시간
│  ├─ 구조주의 분석 결과: TTL 24시간 (변경 빈도 낮음)
│  ├─ 갤럭시 스냅샷: TTL 1주일 (주 1회 업데이트)
│  └─ 구조적 등가성 결과: TTL 24시간 (배치 처리 결과)
├─ 브라우저: 갤럭시 데이터 (IndexedDB)
│  ├─ 갤럭시 좌표 데이터: 영구 저장
│  ├─ 필터 설정: 세션 저장
│  └─ 북마크: 영구 저장
└─ Neo4j: 쿼리 결과 (Query Cache)
   ├─ 자주 사용되는 쿼리: 자동 캐싱
   ├─ 구조주의 분석 쿼리: 명시적 캐싱
   └─ 캐시 무효화: 데이터 업데이트 시
```

### 6.3 성능 모니터링 메트릭 및 임계값 (신규)

#### 6.3.1 애플리케이션 메트릭

**API 성능 메트릭:**

| 메트릭 | 측정 방식 | 목표값 | Warning | Critical | 알림 채널 |
|--------|----------|--------|---------|----------|----------|
| **응답시간 (p50)** | Prometheus | < 100ms | > 150ms | > 300ms | Slack |
| **응답시간 (p90)** | Prometheus | < 200ms | > 300ms | > 500ms | Slack, PagerDuty |
| **응답시간 (p99)** | Prometheus | < 500ms | > 800ms | > 1s | PagerDuty |
| **에러율** | Prometheus | < 0.1% | > 1% | > 5% | PagerDuty |
| **처리량 (RPS)** | Prometheus | > 100 | < 80 | < 50 | Slack |

**프론트엔드 성능 메트릭:**

| 메트릭 | 측정 방식 | 목표값 | Warning | Critical | 알림 채널 |
|--------|----------|--------|---------|----------|----------|
| **갤럭시 로딩 시간** | Custom timer | < 3초 | > 4초 | > 5초 | Slack |
| **3D 렌더링 FPS** | Chrome DevTools | 60 FPS | < 55 FPS | < 30 FPS | Slack |
| **메모리 사용량** | Chrome DevTools | < 150MB | > 200MB | > 300MB | Slack |
| **번들 크기** | Webpack | < 500KB | > 600KB | > 800KB | Slack |

**데이터베이스 성능 메트릭:**

| 메트릭 | 측정 방식 | 목표값 | Warning | Critical | 알림 채널 |
|--------|----------|--------|---------|----------|----------|
| **쿼리 응답시간** | Neo4j 내장 | < 200ms | > 500ms | > 1s | Slack |
| **느린 쿼리 수** | Neo4j 로그 | < 5/일 | > 10/일 | > 20/일 | Slack |
| **연결 풀 사용률** | Neo4j 모니터링 | < 70% | > 85% | > 95% | PagerDuty |
| **메모리 사용량** | Neo4j 모니터링 | < 80% | > 90% | > 95% | PagerDuty |

#### 6.3.2 비즈니스 메트릭

**데이터 품질 메트릭:**

| 메트릭 | 측정 방식 | 목표값 | Warning | Critical | 알림 채널 |
|--------|----------|--------|---------|----------|----------|
| **평균 신뢰도** | 주기적 계산 | ≥ 0.85 | < 0.88 | < 0.85 | Email, Slack |
| **검증 통과율** | 파이프라인 로그 | > 95% | < 97% | < 95% | Email |
| **결측치율** | 데이터 분석 | < 5% | > 7% | > 10% | Email |
| **데이터 최신성** | 타임스탬프 | < 24시간 | > 48시간 | > 72시간 | Slack |

**사용자 경험 메트릭:**

| 메트릭 | 측정 방식 | 목표값 | Warning | Critical | 알림 채널 |
|--------|----------|--------|---------|----------|----------|
| **일일 활성 사용자** | Google Analytics | > 50 | < 40 | < 30 | Slack |
| **사용자 이탈률** | Google Analytics | < 30% | > 40% | > 50% | Slack |
| **평균 세션 시간** | Google Analytics | > 5분 | < 3분 | < 2분 | Slack |
| **페이지 로드 실패율** | Sentry | < 1% | > 2% | > 5% | PagerDuty |

#### 6.3.3 모니터링 대시보드 구성

**Grafana 대시보드:**

```
대시보드 1: API 성능
├─ 응답시간 (p50, p90, p99)
├─ 에러율
├─ 처리량 (RPS)
├─ 엔드포인트별 성능
└─ 상위 10개 느린 쿼리

대시보드 2: 프론트엔드 성능
├─ 갤럭시 로딩 시간
├─ 3D 렌더링 FPS
├─ 메모리 사용량
├─ 에러 발생률
└─ 사용자 행동 분석

대시보드 3: 데이터베이스 성능
├─ 쿼리 응답시간
├─ 연결 풀 사용률
├─ 메모리 사용량
├─ 느린 쿼리 추적
└─ 인덱스 사용률

대시보드 4: 비즈니스 메트릭
├─ 데이터 신뢰도 추이
├─ 일일 활성 사용자
├─ API 사용량
├─ 에러 통계
└─ 사용자 이탈률
```

### 6.2 모니터링 & 로깅

```
프론트엔드 모니터링:
├─ Sentry (에러 추적)
├─ Google Analytics (사용자 행동)
├─ Lighthouse (성능 점수)
└─ Custom 메트릭 (갤럭시 FPS, 로딩 시간)

백엔드 모니터링:
├─ Prometheus (메트릭 수집)
├─ Grafana (시각화)
├─ ELK Stack (로그 분석)
└─ DataDog (APM)

데이터베이스 모니터링:
├─ Neo4j 내장 모니터링
├─ 쿼리 성능 분석
├─ 메모리 사용량
└─ 백업 상태
```

---

## 7. 동기화 매트릭스

### 7.1 BRD ↔ PRD ↔ TSD 연계

| BRD (비즈니스) | PRD (제품) | TSD (기술) |
|---|---|---|
| **Year 1 목표: MAU 1,000명** | 홈화면 갤럭시 시각화 | Galaxy3D.tsx + 60 FPS 렌더링 |
| **수익: 정부 계약 3억** | API 공개, 데이터 다운로드 | `/api/artists`, `/api/galaxy-snapshot` |
| **논문 5편 발표** | 방법론 페이지, 데이터 투명성 | JSON-LD 응답, Cypher 쿼리 공개 |
| **기관 구독 5곳** | 프리미엄 분석 대시보드 | `/api/analysis/*` 엔드포인트 |
| **데이터 신뢰도 0.85** | 데이터 출처 표시 | metadata.confidence_score, verified flag |
| **Year 2: 기관 25곳** | 고급 필터, 비교 분석 | `/api/compare`, 복합 쿼리 최적화 |
| **Year 3: 글로벌 진출** | 국제 미술 데이터 | 다국어 지원, 통화 변환 (USD, EUR) |

### 7.2 데이터 흐름 검증

```
BRD 요구사항 → PRD 기능 → TSD 구현
├─ "투명성 증진" → "모든 계산 로직 공개" → "Cypher 쿼리 공개"
├─ "학술 신뢰도" → "논문 인용 기능" → JSON-LD 인용 메타데이터
├─ "시장 이상치" → "이상치 탐지 기능" → POST /api/anomalies
├─ "정책 근거" → "정부 계약용 리포트" → GalaxySnapshot + analytics
└─ "사용자 참여" → "무료 갤럭시" → Three.js 렌더링 + 필터
```

---

## 8. 마이그레이션 & 업그레이드 경로

### 8.1 Year 1 → Year 2

```
데이터 확장:
100명 → 500명 (스키마 불변)

기능 추가:
├─ Artist: 시장 가격 히스토리 추가
├─ Institution: 국제 협력 정보
├─ Cluster: 머신러닝 예측 모델
└─ Transaction: 장기 거래 추이 분석

성능 최적화:
├─ Neo4j 클러스터 (replica)
├─ API 캐싱 전략 개선
└─ Three.js LOD (Level of Detail)
```

### 8.2 Year 2 → Year 3

```
국제화:
├─ 다국어 지원 (일본어, 중국어)
├─ 통화 변환 (KRW ↔ USD ↔ EUR)
└─ 국제 미술계 데이터 통합

새 기능:
├─ 머신러닝 추천 시스템
├─ 시계열 예측 (LSTM)
├─ 모바일 네이티브 앱 (React Native)
└─ API v2 (GraphQL 옵션)
```

---

## 9. 보안 & 규정 준수

### 9.1 데이터 보안

```
전송 보안:
├─ HTTPS/TLS 1.3 (모든 통신)
├─ JWT 토큰 (인증)
└─ Rate Limiting (API 남용 방지)

저장 보안:
├─ Neo4j 암호화 (AES-256)
├─ 감시 액세스 로깅
└─ 정기 백업 (24시간마다)

개인정보 보호:
├─ 작가명 공개 (공개 정보)
├─ 연락처 비공개 (필요시 요청)
├─ GDPR 규정 준수 (EU 사용자)
└─ 동의 기반 데이터 사용
```

### 9.2 학술 윤리

```
데이터 인용 원칙:
├─ 모든 데이터 출처 명시
├─ 정규화 과정 투명화
└─ 분석 방법론 공개

결과 검증:
├─ 동료 검증 (학술지 게재)
├─ 재현성 보장 (코드/데이터 공개)
└─ 한계점 명시 (신뢰도 점수)
```

### 9.3 재해 복구 계획 (DRP) (신규)

#### 9.3.1 재해 시나리오 및 대응

**시나리오 1: Neo4j 데이터베이스 손실**

```
심각도: Critical
영향: 전체 서비스 중단, 데이터 손실
복구 목표 시간 (RTO): 4시간
복구 목표 시점 (RPO): 24시간 전

대응 절차:
1. 즉시 대응 (0-30분)
   ├─ Neo4j Aura 자동 백업 확인
   ├─ 최신 백업 스냅샷 식별
   └─ 복구 팀 소집 (DevOps + Backend)

2. 복구 실행 (30분-2시간)
   ├─ Neo4j Aura 새 인스턴스 생성
   ├─ 최신 백업에서 데이터 복원
   ├─ 스키마 재생성 (제약조건, 인덱스)
   └─ 연결 테스트

3. 검증 (2-3시간)
   ├─ 데이터 무결성 검증 (샘플 쿼리)
   ├─ API 엔드포인트 테스트
   └─ 성능 테스트

4. 서비스 재개 (3-4시간)
   ├─ 트래픽 점진적 복구 (10% → 50% → 100%)
   ├─ 모니터링 강화
   └─ 사용자 공지

백업 정책:
├─ 자동 백업: Neo4j Aura 일일 백업 (매일 02:00 UTC)
├─ 수동 백업: 주간 전체 백업 (매주 일요일)
├─ 백업 보관: 30일간 보관
└─ 백업 검증: 주 1회 복원 테스트
```

**시나리오 2: 백엔드 API 서버 장애**

```
심각도: High
영향: API 서비스 중단, 프론트엔드 기능 제한
복구 목표 시간 (RTO): 1시간
복구 목표 시점 (RPO): 실시간 (무손실)

대응 절차:
1. 즉시 대응 (0-10분)
   ├─ 자동 스케일링 확인
   ├─ Health check 실패 확인
   └─ 로그 분석 (에러 원인 파악)

2. 복구 실행 (10-30분)
   ├─ 새 인스턴스 자동 생성 (Cloud Run)
   ├─ 환경 변수 복원 (Secret Manager 또는 환경 변수)
   ├─ 의존성 확인 (Neo4j 연결)
   └─ Health check 통과 확인

3. 검증 (30-45분)
   ├─ API 엔드포인트 테스트
   ├─ 부하 테스트 (트래픽 점진적 증가)
   └─ 모니터링 확인

4. 서비스 재개 (45-60분)
   ├─ 트래픽 라우팅 복구
   ├─ 모니터링 강화
   └─ 사용자 공지 (필요시)

폴백 전략:
├─ Circuit Breaker: Neo4j 실패 시 캐시 반환
├─ Cloud CDN 캐싱: 정적 자산은 영향 없음 (Firebase Hosting 자동 포함)
└─ 읽기 전용 모드: 쓰기 기능 일시 중단 가능
```

**시나리오 3: 데이터 손상 (부분적)**

```
심각도: Medium
영향: 일부 데이터 부정확, 신뢰도 하락
복구 목표 시간 (RTO): 24시간
복구 목표 시점 (RPO): 손상 발견 시점

대응 절차:
1. 손상 범위 확인 (0-2시간)
   ├─ 데이터 무결성 검사 스크립트 실행
   ├─ 손상된 레코드 식별
   └─ 손상 원인 분석

2. 데이터 복구 (2-12시간)
   ├─ 백업에서 손상된 레코드 복원
   ├─ 데이터 검증 파이프라인 재실행
   └─ 신뢰도 점수 재계산

3. 검증 (12-20시간)
   ├─ 복구된 데이터 검증
   ├─ 신뢰도 점수 확인 (목표: ≥ 0.85)
   └─ API 테스트

4. 서비스 재개 (20-24시간)
   ├─ 점진적 데이터 업데이트
   ├─ 모니터링 강화
   └─ 사용자 공지 (필요시)
```

#### 9.3.2 백업 정책

**Neo4j 데이터베이스:**

```
백업 유형:
├─ 자동 백업: Neo4j Aura 일일 백업 (매일 02:00 UTC)
├─ 수동 백업: 주간 전체 백업 (매주 일요일)
└─ 이벤트 백업: 주요 데이터 업데이트 전

백업 보관:
├─ 일일 백업: 7일간 보관
├─ 주간 백업: 30일간 보관
└─ 월간 백업: 90일간 보관

백업 검증:
├─ 자동 검증: 백업 생성 후 즉시 검증
├─ 수동 검증: 주 1회 복원 테스트
└─ 검증 항목: 데이터 무결성, 스키마 일치성
```

**애플리케이션 코드:**

```
백업 유형:
├─ Git 저장소: 모든 코드 버전 관리
├─ Docker 이미지: 프로덕션 이미지 태그 보관
└─ 환경 변수: 암호화된 저장소에 보관

백업 보관:
├─ Git: 무기한 보관
├─ Docker 이미지: 최근 10개 버전
└─ 환경 변수: 암호화된 백업 (월 1회)
```

#### 9.3.3 복구 테스트 계획

```
테스트 주기:
├─ 월간 테스트: 백업 복원 테스트 (매월 첫째 주)
├─ 분기별 테스트: 전체 DRP 시뮬레이션 (분기별)
└─ 연간 테스트: 재해 시나리오 전체 테스트 (연 1회)

테스트 항목:
├─ 백업 복원 시간 측정
├─ 데이터 무결성 검증
├─ 서비스 재개 시간 측정
└─ RTO/RPO 목표 달성 여부

테스트 결과 문서화:
├─ 테스트 일시 및 참여자
├─ 발견된 문제점
├─ 개선 사항
└─ 다음 테스트 계획
```

---

## 10. 타임라인 & 마일스톤

### Phase 1: 파일럿 & 검증 (Month 1–3)

```
M1:
├─ Neo4j Aura 인스턴스 생성
├─ 100명 데이터 수집 & 정규화
├─ 스키마 배포
└─ 점수 계산 알고리즘 구현

M2:
├─ FastAPI 백엔드 개발 (기본 API)
├─ Galaxy3D 컴포넌트 개발 (렌더링)
├─ 필터 & UI 구현
└─ 초기 논문 작성 시작

M3:
├─ MVP 배포 (베타)
├─ 초기 사용자 100명 모집
├─ 논문 1편 제출
└─ 정부 기관 미팅
```

### Phase 2: 기본 상용화 (Month 4–6)

```
M4:
├─ 분석 대시보드 완성
├─ 이상치 탐지 기능
├─ API 공개 (베타)
└─ 기관 구독 계약 2–3곳

M5:
├─ 논문 발표 3–4편
├─ 정부 계약 체결 (3억 원)
├─ 기관 구독 5곳 확보
└─ MAU 1,000명 달성

M6:
├─ 성능 최적화 (캐싱, 인덱싱)
├─ 보안 감사 완료
├─ Year 2 계획 수립
└─ 기존 사용자 만족도 조사
```

---

## 결론

**TSD는 BRD, PRD와의 완벽한 동기화를 보장한다.**

```
BRD 비즈니스 목표
  ↓ 달성 수단: 제품 기능 (PRD)
    ↓ 구현 수단: 기술 아키텍처 (TSD)
      ↓ 검증: KPI 달성
```

모든 결정과 설계는 다음 원칙을 따른다:

1. **투명성**: 모든 계산 로직 공개 (Cypher, 방법론)
2. **학술성**: 동료 검증 가능, 논문 인용 가능
3. **확장성**: 100명 → 500명 → 2,000명 (스키마 불변)
4. **수익성**: Year 1 적자, Year 2–3 흑자 (4가지 수익 흐름)
5. **사회적 영향**: 미술계 투명성 + 공정성 증진

---

**Next Step**: 
1. ✅ TSD 승인 (기술팀)
2. ✅ BRD 승인 (경영진)
3. ✅ PRD 승인 (제품팀)
4. ⏳ Antigravity에서 Neo4j 초기화
5. ⏳ Cursor에서 개발 시작

---

**End of TSD Document**

**Version Control**:
- v1.0 (2025-12-08): 초안
- v2.0 (2025-12-08): BRD+PRD 완벽 동기화
- v2.1 (2025-12-08): GCP 인프라 구성으로 전면 업데이트
- v2.2 (2025-12-08): 프론트엔드 구현 상태 반영
- v3.0 (예정): 최종 승인 버전

---

## 구현 상태 (Implementation Status)

**Last Updated**: 2025-12-08

### 프론트엔드 계층
- ✅ React 18 + TypeScript + Vite 설정 완료
- ✅ Three.js r181 + React Three Fiber 통합 완료
- ✅ 기본 컴포넌트 구조 완성
  - GalaxyScene.tsx
  - ArtistParticles.tsx (InstancedMesh)
  - GalaxyControls.tsx
  - LeftPanel.tsx, RightPanel.tsx
- ✅ 상태 관리 구조 완성 (useGalaxy, AppContext)
- ✅ 프로젝트 구조 정리 완료 (쉐이더 관련 파일 제거)

### 백엔드 계층
- ⏳ FastAPI 구조 설계 예정
- ⏳ Neo4j Aura Cloud 연동 예정

### 데이터베이스 계층
- ⏳ Neo4j 초기화 예정
- ✅ 데이터 스키마 정의 완료 (types/argo.ts)
