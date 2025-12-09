# ARGO Neo4j 구현 작업 지시서 (MVP 기준)
## id 통일 + GDS/구조주의 v1

**Version**: 1.0.0
**Date**: 2025-12-09
**Status**: Implementation Ready
**Target**: Antigravity (Gemini 3 Pro)

---

## 1. 목표

현재 **Artist 단독 노드 상태**인 Neo4j 그래프를, **관계·인덱스·GDS 분석이 돌아가는 최소 그래프**로 확장한다.

**구체적 목표:**
1. 4개 핵심 노드 타입 완성 (Artist, Institution, Exhibition, Cluster)
2. 4개 핵심 관계 타입 구현 (COLLABORATED_WITH, AFFILIATED_WITH, PARTICIPATED_IN, BELONGS_TO)
3. GDS 네트워크 분석 실제 구현 (degree, betweenness, eigenvector, Louvain)
4. 구조주의 분석 v1 완성 (capital_composition, dominant_capital, field_quadrant, coordinates_3d)

---

## 2. 환경

### 2.1 기술 스택

| 구분 | 기술 | 버전/상세 |
|-----|------|----------|
| Database | Neo4j Aura | AuraDB Professional (GDS 포함) |
| Backend | FastAPI + Python | 3.10+ |
| GDS | Neo4j Graph Data Science | 2.x (Aura 내장, Serverless) |
| ID 체계 | **`id` 통일** | 모든 노드의 primary key는 `id` |

### 2.1.1 Neo4j Aura 인스턴스 정보

**인스턴스 사양:**
- **ID**: be57a318
- **Connection URI**: `neo4j+s://be57a318.databases.neo4j.io`
- **Query API URL**: `https://be57a318.databases.neo4j.io/db/{databaseName}/query/v2`
- **Version**: 2025.10
- **Region**: Google Cloud / Iowa, USA (us-central1)
- **Type**: AuraDB Professional
- **Graph Analytics**: Serverless

**리소스 제한:**
- **Memory**: 1GB
- **CPU**: 1
- **Storage**: 2GB

**연결 설정 권장사항:**
- 최대 연결 풀 크기: 10 (메모리 제약 고려)
- 연결 타임아웃: 30초
- 연결 획득 타임아웃: 2분
- 암호화: 필수 (`encrypted=True`)
- 인증서 신뢰: `TRUST_SYSTEM_CA_SIGNED_CERTIFICATES`

### 2.2 주요 파일 구조

```
argo-backend/
├── app/
│   ├── database.py                    # Neo4j 연결
│   ├── services/
│   │   ├── neo4j_service.py           # 쿼리 실행
│   │   ├── artist_service.py          # Artist 비즈니스 로직
│   │   └── analysis_service.py        # 분석 서비스 (GDS 연동)
│   ├── uploaders/
│   │   └── neo4j_uploader.py          # 노드 업로드 (확장 필요)
│   ├── collectors/                    # 9개 데이터 수집기
│   └── routers/                       # API 라우터
├── neo4j/                             # 신규 생성 필요
│   ├── init_schema.cypher             # 제약조건/인덱스
│   ├── gds_projections.cypher         # GDS 그래프 프로젝션
│   └── queries/                       # 쿼리 템플릿
└── data_collection_pipeline.py        # 통합 파이프라인
```

### 2.3 가용 데이터 소스 요약

| 데이터 소스 | 데이터량 | 활용 목적 | 신뢰도 |
|------------|---------|----------|--------|
| ARKO 작가 목록 | 505명 | Artist 노드 생성 | 0.95 |
| ARKO 미술작품 | 24,762개 | inst_score (작품 수) | 0.95 |
| ARKO 예술단체 | 94개 | Institution 노드 | 0.95 |
| KCI 논문 정보 | ~10,000개 | acad_score (논문 수) | 0.85 |
| KCI 인용 정보 | ~1.4M명 | acad_score (인용 수, H-index) | 0.90 |
| 청주공예비엔날레 | 수천 개 | inst_score (비엔날레 참여) | 0.90 |
| MMCA 레지던시 | 수백 개 | inst_score (레지던시 참여) | 0.92 |
| MMCA 소장작품 | 수천 개 | inst_score (소장작품 수) | 0.95 |

**파생 가능한 관계:**
- Artist → Artwork: 작가명 매칭 (53.5% 성공률)
- Artist → Paper: 저자명 매칭
- Artist → Biennale/Residency/Collection: 이름 매칭
- Artist ↔ Artist (공동저자): KCI 공동저자 필드
- Artist ↔ Artist (공동전시): 전시 참여자 매칭 (MMCA 추가 수집 필요)

---

## 3. 1단계: MVP Neo4j 설계 정리

### 3.1 필수 노드 라벨 (MVP)

#### 3.1.1 `:Artist` (핵심)

```cypher
(:Artist {
  // === Primary Key ===
  id: STRING,                          // "arko_0001" (UNIQUE)

  // === 기본 정보 ===
  name: STRING,                        // 한글 이름 (검색용)
  name_ko: STRING,                     // 한글 이름 (표시용)
  name_en: STRING,                     // 영문 이름
  segment_id: STRING,                  // "painting_KR", "sculpture_KR" 등
  career_stage: STRING,                // "early", "mid", "late"
  genre: STRING,                       // "회화", "조각", "공예" 등

  // === 4개 레이어 점수 (0-100) ===
  inst_score: FLOAT,                   // 제도 점수
  acad_score: FLOAT,                   // 학술 점수
  media_score: FLOAT,                  // 담론 점수 (MVP에서는 기본값)
  network_score: FLOAT,                // 네트워크 점수 (GDS 계산)
  composite_score: FLOAT,              // 가중 복합 점수
  composite_confidence: FLOAT,         // 신뢰도 (0-1)

  // === 구조주의 분석 필드 ===
  dominant_capital: STRING,            // "institutional"/"academic"/"media"/"network"
  capital_composition: MAP,            // {inst: 0.3, acad: 0.2, media: 0.25, network: 0.25}
  field_quadrant: STRING,              // "Q1_established", "Q2_academic_elite", "Q3_media_star", "Q4_emerging"

  // === 3D 좌표 ===
  coord_x: FLOAT,                      // inst_score 기반
  coord_y: FLOAT,                      // acad_score 기반
  coord_z: FLOAT,                      // media_score 기반
  coord_radius: FLOAT,                 // network_score 기반

  // === GDS 중심성 (런타임 계산) ===
  degree_centrality: FLOAT,            // GDS 계산
  betweenness_centrality: FLOAT,       // GDS 계산
  eigenvector_centrality: FLOAT,       // GDS 계산
  community_id: INTEGER,               // Louvain 커뮤니티 ID

  // === 메타데이터 ===
  data_sources: [STRING],              // ["ARKO", "KCI", "MMCA_COLLECTION"]
  collected_at: DATETIME,
  updated_at: DATETIME,
  verified: BOOLEAN
})
```

#### 3.1.2 `:Institution` (핵심)

```cypher
(:Institution {
  // === Primary Key ===
  id: STRING,                          // "inst_0001" (UNIQUE)

  // === 기본 정보 ===
  name: STRING,                        // 기관명
  name_en: STRING,                     // 영문명
  type: STRING,                        // "museum", "gallery", "university", "foundation", "arts_group"

  // === 위치 정보 ===
  region: STRING,                      // "서울", "부산" 등
  address: STRING,                     // 상세 주소

  // === 기관 지표 ===
  prestige_score: FLOAT,               // 기관 위상 점수 (0-100)
  artist_count: INTEGER,               // 소속 작가 수

  // === 메타데이터 ===
  data_source: STRING,                 // "ARKO", "MMCA"
  url: STRING,
  representative: STRING,              // 대표자
  collected_at: DATETIME
})
```

#### 3.1.3 `:Exhibition` (핵심)

```cypher
(:Exhibition {
  // === Primary Key ===
  id: STRING,                          // "exh_0001" (UNIQUE)

  // === 기본 정보 ===
  title: STRING,                       // 전시명
  type: STRING,                        // "solo", "group", "biennale", "triennial"

  // === 일시/장소 ===
  year: INTEGER,                       // 개최 연도
  start_date: DATE,
  end_date: DATE,
  venue: STRING,                       // 개최 장소

  // === 전시 지표 ===
  participant_count: INTEGER,          // 참여 작가 수
  significance: STRING,                // "local", "national", "international"

  // === 메타데이터 ===
  data_source: STRING,
  collected_at: DATETIME
})
```

#### 3.1.4 `:Cluster` (핵심)

```cypher
(:Cluster {
  // === Primary Key ===
  id: STRING,                          // "cluster_001" (UNIQUE)

  // === 기본 정보 ===
  name: STRING,                        // 클러스터명 (자동 생성)
  type: STRING,                        // "louvain", "genre", "generation"

  // === 클러스터 지표 ===
  size: INTEGER,                       // 멤버 수
  avg_composite_score: FLOAT,          // 평균 복합 점수
  dominant_genre: STRING,              // 주요 장르

  // === 3D 좌표 (중심점) ===
  center_x: FLOAT,
  center_y: FLOAT,
  center_z: FLOAT,

  // === 메타데이터 ===
  algorithm_version: STRING,
  created_at: DATETIME
})
```

### 3.2 Phase 2로 미루는 노드 (스키마만 정의)

#### 3.2.1 `:Artwork` (Phase 2)

```cypher
(:Artwork {
  id: STRING,                          // "work_0001"
  title: STRING,
  artist_id: STRING,                   // FK to Artist
  year: INTEGER,
  medium: STRING,                      // "oil on canvas", "bronze"
  classification: STRING,              // "조각", "회화"
  location: STRING,                    // 설치 위치
  data_source: STRING
})
```

#### 3.2.2 `:Transaction` (Phase 2)

```cypher
(:Transaction {
  id: STRING,                          // "trans_0001"
  artwork_id: STRING,
  price: FLOAT,
  currency: STRING,
  date: DATE,
  auction_house: STRING,
  data_source: STRING
})
```

### 3.3 필수 관계 라벨 (MVP)

#### 3.3.1 `[:COLLABORATED_WITH]` (Artist ↔ Artist)

**생성 기준:**
1. KCI 논문 공동저자 관계
2. 같은 전시 참여 (Exhibition을 통해 추론)
3. 같은 기관 소속 (Institution을 통해 추론)

```cypher
(:Artist)-[:COLLABORATED_WITH {
  strength: FLOAT,                     // 0.0 - 1.0 (관계 강도)
  collaboration_count: INTEGER,        // 협업 횟수
  collaboration_type: STRING,          // "co_author", "co_exhibition", "same_institution"
  years: [INTEGER],                    // 협업 연도 리스트
  last_collaboration: INTEGER          // 마지막 협업 연도
}]->(:Artist)
```

**초기 생성 전략:**
```
1. KCI 공동저자 → strength 0.8, type "co_author"
2. 같은 Exhibition 참여 → strength 0.5, type "co_exhibition"
3. 같은 Institution 소속 → strength 0.3, type "same_institution"
```

#### 3.3.2 `[:AFFILIATED_WITH]` (Artist → Institution)

**생성 기준:**
1. ARKO 예술단체 대표자 매칭
2. KCI 논문 발행기관 매칭
3. MMCA 레지던시 참여

```cypher
(:Artist)-[:AFFILIATED_WITH {
  role: STRING,                        // "member", "professor", "director", "alumni"
  start_year: INTEGER,
  end_year: INTEGER,                   // null = 현재 소속
  is_current: BOOLEAN
}]->(:Institution)
```

#### 3.3.3 `[:PARTICIPATED_IN]` (Artist → Exhibition)

**생성 기준:**
1. 비엔날레 참여 (청주공예비엔날레)
2. 전시 참여 (MMCA 추가 수집 시)

```cypher
(:Artist)-[:PARTICIPATED_IN {
  role: STRING,                        // "artist", "curator"
  artworks_count: INTEGER,             // 출품 작품 수
  award: STRING                        // 수상 정보 (있으면)
}]->(:Exhibition)
```

#### 3.3.4 `[:BELONGS_TO]` (Artist → Cluster)

**생성 기준:**
1. Louvain 커뮤니티 탐지 결과

```cypher
(:Artist)-[:BELONGS_TO {
  membership_strength: FLOAT,          // 0.0 - 1.0
  distance_to_center: FLOAT            // 클러스터 중심까지 거리
}]->(:Cluster)
```

### 3.4 Phase 2로 미루는 관계

| 관계 | 설명 | Phase 2 이유 |
|-----|------|-------------|
| `[:CREATED]` | Artist → Artwork | Artwork 노드 필요 |
| `[:DISPLAYED_IN]` | Artwork → Exhibition | Artwork 노드 필요 |
| `[:SOLD_IN]` | Artwork → Transaction | 경매 데이터 필요 |
| `[:ADJACENT_TO]` | Cluster ↔ Cluster | 고급 분석 |
| `[:DOMINATES]` | Institution → Cluster | 고급 분석 |

---

## 4. 2단계: 파일/컴포넌트 단위 구현 플랜

### 4.1 신규 생성 파일

#### 4.1.1 `neo4j/init_schema.cypher`

**목적:** 제약조건 및 인덱스 생성

```cypher
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
FOR (a:Artist) ON EACH [a.name, a.name_ko, a.name_en];

CREATE FULLTEXT INDEX institution_name_search IF NOT EXISTS
FOR (i:Institution) ON EACH [i.name, i.name_en];

CREATE FULLTEXT INDEX exhibition_title_search IF NOT EXISTS
FOR (e:Exhibition) ON EACH [e.title];
```

#### 4.1.2 `neo4j/gds_projections.cypher`

**목적:** GDS 그래프 프로젝션 및 알고리즘 실행

```cypher
// ========================================
// GDS Graph Projections & Algorithms
// ========================================

// === 1. 협업 네트워크 프로젝션 ===
CALL gds.graph.project(
  'artist-collaboration-graph',
  'Artist',
  {
    COLLABORATED_WITH: {
      type: 'COLLABORATED_WITH',
      orientation: 'UNDIRECTED',
      properties: ['strength']
    }
  },
  {
    nodeProperties: ['composite_score', 'inst_score', 'acad_score']
  }
);

// === 2. Degree Centrality ===
CALL gds.degree.write(
  'artist-collaboration-graph',
  {
    writeProperty: 'degree_centrality',
    relationshipWeightProperty: 'strength'
  }
);

// === 3. Betweenness Centrality ===
CALL gds.betweenness.write(
  'artist-collaboration-graph',
  {
    writeProperty: 'betweenness_centrality'
  }
);

// === 4. Eigenvector Centrality ===
CALL gds.eigenvector.write(
  'artist-collaboration-graph',
  {
    writeProperty: 'eigenvector_centrality',
    maxIterations: 100
  }
);

// === 5. Louvain Community Detection ===
CALL gds.louvain.write(
  'artist-collaboration-graph',
  {
    writeProperty: 'community_id',
    relationshipWeightProperty: 'strength'
  }
);

// === 6. 그래프 프로젝션 삭제 (정리용) ===
// CALL gds.graph.drop('artist-collaboration-graph');
```

#### 4.1.3 `neo4j/queries/structuralist_analysis.cypher`

**목적:** 구조주의 분석 필드 계산

```cypher
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

// === 4. 3D Coordinates 계산 ===
MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
SET a.coord_x = round((a.inst_score - 50) * 0.6, 2),
    a.coord_y = round((a.acad_score - 50) * 0.6, 2),
    a.coord_z = round((a.media_score - 50) * 0.6, 2),
    a.coord_radius = round(10.0 + (a.network_score / 5.0), 2)
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
```

### 4.2 기존 파일 수정

#### 4.2.1 `app/uploaders/neo4j_uploader.py`

**수정 사항:**
1. `upload_artist()` 미세 조정 (id 통일 확인, datetime 처리)
2. 신규 메서드 추가:
   - `upload_institutions(institutions: List[Dict]) -> Dict`
   - `upload_exhibitions(exhibitions: List[Dict]) -> Dict`
   - `upload_clusters(clusters: List[Dict]) -> Dict`
   - `create_collaboration_relationships(artists: List[Dict], papers: List[Dict]) -> Dict`
   - `create_affiliation_relationships(artists: List[Dict], institutions: List[Dict]) -> Dict`
   - `create_participation_relationships(artists: List[Dict], exhibitions: List[Dict]) -> Dict`
   - `create_belongs_to_relationships() -> Dict` (GDS 실행 후)

**핵심 코드 구조:**

```python
class Neo4jUploader:
    # 기존
    def upload_artist(self, artist_data: Dict) -> bool: ...
    def upload_artists(self, artists: List[Dict]) -> Dict: ...

    # 신규 추가
    def upload_institution(self, inst_data: Dict) -> bool:
        """단일 Institution 노드 업로드"""
        query = """
        MERGE (i:Institution {id: $id})
        SET i.name = $name,
            i.name_en = $name_en,
            i.type = $type,
            i.region = $region,
            i.prestige_score = $prestige_score,
            i.data_source = $data_source,
            i.url = $url,
            i.representative = $representative,
            i.collected_at = datetime()
        RETURN i
        """
        # ... 구현

    def upload_exhibition(self, exh_data: Dict) -> bool:
        """단일 Exhibition 노드 업로드"""
        query = """
        MERGE (e:Exhibition {id: $id})
        SET e.title = $title,
            e.type = $type,
            e.year = $year,
            e.venue = $venue,
            e.participant_count = $participant_count,
            e.data_source = $data_source,
            e.collected_at = datetime()
        RETURN e
        """
        # ... 구현

    def create_collaboration_from_coauthors(self, papers: List[Dict]) -> Dict:
        """KCI 공동저자 관계에서 COLLABORATED_WITH 생성"""
        query = """
        UNWIND $pairs AS pair
        MATCH (a1:Artist {name: pair.author1})
        MATCH (a2:Artist {name: pair.author2})
        WHERE a1.id < a2.id  // 중복 방지
        MERGE (a1)-[r:COLLABORATED_WITH]->(a2)
        ON CREATE SET r.strength = 0.8,
                      r.collaboration_type = 'co_author',
                      r.collaboration_count = 1
        ON MATCH SET r.collaboration_count = r.collaboration_count + 1
        RETURN count(r) AS created
        """
        # ... 구현

    def create_affiliation_from_institutions(self, artists: List[Dict], institutions: List[Dict]) -> Dict:
        """작가-기관 AFFILIATED_WITH 생성"""
        # 대표자 이름 매칭 또는 KCI 발행기관 매칭
        # ... 구현

    def sync_clusters_from_gds(self) -> Dict:
        """GDS Louvain 결과로 Cluster 노드 및 BELONGS_TO 관계 생성"""
        # 1. community_id 별 통계 계산
        # 2. Cluster 노드 생성
        # 3. BELONGS_TO 관계 생성
        # ... 구현
```

#### 4.2.2 `app/services/analysis_service.py`

**수정 사항:**
1. Fake 구현을 실제 GDS 호출로 교체
2. 구조주의 분석 쿼리 추가

```python
class AnalysisService:
    async def run_gds_centrality(self) -> Dict:
        """GDS 중심성 분석 실행 (degree, betweenness, eigenvector)"""
        # 1. 그래프 프로젝션 존재 확인
        # 2. 없으면 생성
        # 3. centrality 알고리즘 실행
        # 4. 결과를 노드에 write
        # ... 구현

    async def run_louvain_community(self) -> Dict:
        """Louvain 커뮤니티 탐지 실행"""
        # 1. 그래프 프로젝션 확인/생성
        # 2. Louvain 실행
        # 3. community_id를 노드에 write
        # 4. Cluster 노드 생성 호출
        # ... 구현

    async def calculate_structuralist_fields(self) -> Dict:
        """구조주의 분석 필드 계산 (capital_composition, dominant_capital, field_quadrant)"""
        # neo4j/queries/structuralist_analysis.cypher 쿼리 실행
        # ... 구현

    async def get_centrality(self, limit: int = 10) -> List[Dict]:
        """기존 메서드: 실제 centrality 속성 반환으로 수정"""
        query = """
        MATCH (a:Artist)
        WHERE a.degree_centrality IS NOT NULL
        RETURN a.id AS id, a.name AS name,
               a.degree_centrality AS degree,
               a.betweenness_centrality AS betweenness,
               a.eigenvector_centrality AS eigenvector
        ORDER BY a.eigenvector_centrality DESC
        LIMIT $limit
        """
        # ... 구현
```

#### 4.2.3 `app/services/artist_service.py`

**수정 사항:**
1. `_map_to_artist()`: 구조주의 필드 매핑 보완
2. 관계 조회 쿼리 개선

```python
def _map_to_artist(self, data: dict) -> Artist:
    # ... 기존 코드

    # 구조주의 분석 필드 매핑 보완
    structuralist_analysis = StructuralistAnalysis(
        dominant_capital=node.get('dominant_capital', 'institutional'),
        capital_composition=node.get('capital_composition', {}),
        structural_position={
            'field_quadrant': node.get('field_quadrant', 'Q4_emerging'),
            'community_id': node.get('community_id'),
        },
        algorithm_version='v1.0.0',
        weights_applied={'inst': 0.30, 'acad': 0.20, 'media': 0.25, 'network': 0.25},
        theoretical_basis='Bourdieu Field Theory + Meta-Analysis'
    )
    # ...
```

### 4.3 파일별 TODO 요약

| 파일 | 작업 유형 | TODO |
|-----|---------|------|
| `neo4j/init_schema.cypher` | 신규 | 제약조건 6개 + 인덱스 8개 + Fulltext 3개 |
| `neo4j/gds_projections.cypher` | 신규 | 그래프 프로젝션 + centrality 4종 |
| `neo4j/queries/structuralist_analysis.cypher` | 신규 | 구조주의 필드 계산 쿼리 5개 |
| `app/uploaders/neo4j_uploader.py` | 확장 | Institution/Exhibition 업로더 + 관계 생성 메서드 5개 |
| `app/services/analysis_service.py` | 리팩터 | GDS 실제 구현 + 구조주의 분석 |
| `app/services/artist_service.py` | 수정 | 구조주의 필드 매핑 보완 |
| `data_collection_pipeline.py` | 확장 | Institution/Exhibition 업로드 단계 추가, 관계 생성 단계 추가 |

---

## 5. 3단계: Phase별 실행 순서

### Phase 1: 스키마/무결성 기반 정비 (Day 1)

**목표:** Neo4j 인덱스/제약조건 설정, 기존 데이터 정합성 확보

**작업:**
1. `neo4j/init_schema.cypher` 생성 및 실행
2. 기존 Artist 노드의 `id` 필드 확인/보정
3. 검증: `SHOW CONSTRAINTS`, `SHOW INDEXES`

**완료 후 가능한 질문:**
- "인덱스가 적용된 상태에서 작가 검색 속도가 개선되었나?"
- "중복 ID가 있는 작가가 있나?"

```cypher
// 검증 쿼리
SHOW CONSTRAINTS;
SHOW INDEXES;
MATCH (a:Artist) RETURN count(a) AS total_artists;
MATCH (a:Artist) WHERE a.id IS NULL RETURN count(a) AS missing_id;
```

---

### Phase 2: Institution/Exhibition 노드 + 관계 생성 (Day 2)

**목표:** 핵심 엔터티 확장, 기본 관계 구조 완성

**작업:**
1. `neo4j_uploader.py`에 `upload_institution()`, `upload_exhibition()` 추가
2. ARKO 예술단체 데이터 → Institution 노드 업로드
3. 비엔날레 데이터 → Exhibition 노드 업로드
4. 관계 생성 메서드 구현:
   - `create_collaboration_from_coauthors()` (KCI 공동저자)
   - `create_affiliation_from_institutions()` (작가-기관)
   - `create_participation_from_exhibitions()` (작가-전시)
5. `data_collection_pipeline.py` 확장

**완료 후 가능한 질문:**
- "한 작가가 어떤 기관과 전시에 연결되어 있나?"
- "가장 많은 작가가 참여한 전시는?"
- "KCI 공동저자 관계가 몇 개 생성되었나?"

```cypher
// 검증 쿼리
MATCH (i:Institution) RETURN count(i) AS total_institutions;
MATCH (e:Exhibition) RETURN count(e) AS total_exhibitions;
MATCH ()-[r:COLLABORATED_WITH]->() RETURN count(r) AS collab_count;
MATCH ()-[r:AFFILIATED_WITH]->() RETURN count(r) AS affil_count;
MATCH ()-[r:PARTICIPATED_IN]->() RETURN count(r) AS parti_count;

// 관계 샘플 확인
MATCH (a:Artist)-[r:COLLABORATED_WITH]->(b:Artist)
RETURN a.name, r.collaboration_type, r.strength, b.name
LIMIT 10;
```

---

### Phase 3: GDS 네트워크 분석 (Day 3)

**목표:** 실제 중심성 계산, 커뮤니티 탐지, Cluster 노드 생성

**작업:**
1. `neo4j/gds_projections.cypher` 생성
2. `analysis_service.py`에 GDS 호출 메서드 구현:
   - `run_gds_centrality()` → degree, betweenness, eigenvector
   - `run_louvain_community()` → community_id
3. `neo4j_uploader.py`에 `sync_clusters_from_gds()` 구현
4. Cluster 노드 자동 생성 + BELONGS_TO 관계 생성

**완료 후 가능한 질문:**
- "허브/브리지 작가는 누구인가? (eigenvector/betweenness 기준)"
- "몇 개의 커뮤니티가 탐지되었고, 각 커뮤니티의 크기는?"
- "가장 큰 커뮤니티의 특성(평균 점수, 주요 장르)은?"

```cypher
// 검증 쿼리
// 중심성 상위 작가
MATCH (a:Artist)
WHERE a.eigenvector_centrality IS NOT NULL
RETURN a.name, a.degree_centrality, a.betweenness_centrality, a.eigenvector_centrality
ORDER BY a.eigenvector_centrality DESC
LIMIT 10;

// 커뮤니티 통계
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
RETURN a.community_id, count(a) AS size, avg(a.composite_score) AS avg_score
ORDER BY size DESC;

// Cluster 노드 확인
MATCH (c:Cluster) RETURN c.id, c.name, c.size ORDER BY c.size DESC;

// BELONGS_TO 관계 확인
MATCH (a:Artist)-[r:BELONGS_TO]->(c:Cluster)
RETURN c.id, count(a) AS members
ORDER BY members DESC;
```

---

### Phase 4: 구조주의 분석 완성 (Day 4)

**목표:** capital_composition, dominant_capital, field_quadrant, coordinates_3d 계산

**작업:**
1. `neo4j/queries/structuralist_analysis.cypher` 생성
2. `analysis_service.py`에 `calculate_structuralist_fields()` 구현
3. network_score를 GDS 중심성 기반으로 업데이트
4. 3D 좌표 계산 및 저장

**완료 후 가능한 질문:**
- "각 field_quadrant에 몇 명의 작가가 속하나?"
- "Q1_established 작가들의 평균 점수는?"
- "dominant_capital이 'academic'인 작가는 누구인가?"
- "3D 좌표가 계산된 작가 수는?"

```cypher
// 검증 쿼리
// 구조주의 필드 확인
MATCH (a:Artist)
WHERE a.capital_composition IS NOT NULL
RETURN a.name, a.dominant_capital, a.field_quadrant, a.capital_composition
LIMIT 10;

// Field Quadrant 분포
MATCH (a:Artist)
WHERE a.field_quadrant IS NOT NULL
RETURN a.field_quadrant, count(a) AS count, avg(a.composite_score) AS avg_score
ORDER BY count DESC;

// 3D 좌표 확인
MATCH (a:Artist)
WHERE a.coord_x IS NOT NULL
RETURN a.name, a.coord_x, a.coord_y, a.coord_z, a.coord_radius
LIMIT 10;

// Network Score 업데이트 확인
MATCH (a:Artist)
WHERE a.network_score <> 50  // 기본값이 아닌 경우
RETURN a.name, a.network_score, a.degree_centrality
ORDER BY a.network_score DESC
LIMIT 10;
```

---

### Phase 5: 통합 검증 및 정리 (Day 5)

**목표:** 전체 파이프라인 검증, 문서 동기화, API 연동 확인

**작업:**
1. 전체 파이프라인 End-to-End 테스트
2. API 라우터에서 새 필드 노출 확인
3. 스키마 문서(`ARGO_Final_Schema.md`) 업데이트 (id 통일 반영)
4. TSD 문서 업데이트
5. 성능 테스트 (100명 기준 쿼리 시간)

**검증 체크리스트:**

```cypher
// 전체 통계
MATCH (a:Artist) RETURN count(a) AS artists;
MATCH (i:Institution) RETURN count(i) AS institutions;
MATCH (e:Exhibition) RETURN count(e) AS exhibitions;
MATCH (c:Cluster) RETURN count(c) AS clusters;

// 관계 통계
MATCH ()-[r:COLLABORATED_WITH]->() RETURN count(r) AS collabs;
MATCH ()-[r:AFFILIATED_WITH]->() RETURN count(r) AS affiliations;
MATCH ()-[r:PARTICIPATED_IN]->() RETURN count(r) AS participations;
MATCH ()-[r:BELONGS_TO]->() RETURN count(r) AS belongs_to;

// 구조주의 필드 커버리지
MATCH (a:Artist) WHERE a.dominant_capital IS NOT NULL RETURN count(a) AS with_dominant;
MATCH (a:Artist) WHERE a.field_quadrant IS NOT NULL RETURN count(a) AS with_quadrant;
MATCH (a:Artist) WHERE a.coord_x IS NOT NULL RETURN count(a) AS with_coords;

// GDS 필드 커버리지
MATCH (a:Artist) WHERE a.community_id IS NOT NULL RETURN count(a) AS with_community;
MATCH (a:Artist) WHERE a.eigenvector_centrality IS NOT NULL RETURN count(a) AS with_centrality;
```

---

## 6. 검증 방법 요약

### 6.1 Phase별 검증 쿼리

| Phase | 검증 항목 | 쿼리 |
|-------|---------|------|
| 1 | 제약조건 | `SHOW CONSTRAINTS` |
| 1 | 인덱스 | `SHOW INDEXES` |
| 2 | Institution 노드 | `MATCH (i:Institution) RETURN count(i)` |
| 2 | 관계 생성 | `MATCH ()-[r]->() RETURN type(r), count(r)` |
| 3 | 중심성 계산 | `MATCH (a:Artist) WHERE a.eigenvector_centrality IS NOT NULL RETURN count(a)` |
| 3 | 커뮤니티 | `MATCH (a:Artist) RETURN a.community_id, count(a) ORDER BY count(a) DESC` |
| 4 | 구조주의 필드 | `MATCH (a:Artist) WHERE a.field_quadrant IS NOT NULL RETURN a.field_quadrant, count(a)` |
| 5 | 전체 통계 | 위 체크리스트 참조 |

### 6.2 API 검증

```bash
# Artist 상세 조회 (구조주의 필드 포함)
curl http://localhost:8000/v1/api/artists/arko_0001

# 중심성 분석 결과
curl -X POST http://localhost:8000/v1/api/analysis/centrality?limit=10

# 커뮤니티 탐지 결과
curl -X POST http://localhost:8000/v1/api/analysis/community-detection

# Field Quadrant 분포
curl http://localhost:8000/v1/api/analysis/field-quadrants

# Galaxy Snapshot (3D 좌표 포함)
curl http://localhost:8000/v1/api/galaxy-snapshot?limit=100
```

---

## 7. 주의사항

### 7.1 GDS 관련

1. **Neo4j Aura에서 GDS 지원 확인** 필요 (Enterprise 플랜)
2. GDS 미지원 시 대안:
   - apoc.path 프로시저 사용
   - Python networkx로 계산 후 결과 업로드
3. **그래프 프로젝션 메모리** 관리:
   - 프로젝션 후 반드시 `gds.graph.drop()` 호출
   - 또는 메모리 설정 확인

### 7.2 데이터 품질

1. **이름 매칭 정확도**: 동명이인 문제로 관계가 잘못 생성될 수 있음
   - Phase 2 이후 ID 기반 매칭으로 전환 필요
2. **관계 강도(strength)**: 초기값은 휴리스틱, 향후 데이터 기반 조정

### 7.3 성능

1. **배치 처리**: 관계 생성 시 UNWIND 사용
2. **인덱스**: 매칭에 사용되는 필드 반드시 인덱스
3. **트랜잭션 크기**: 1000개 단위 커밋 권장

---

## 8. 문서 참조

| 문서 | 역할 |
|-----|------|
| `ARGO_Final_Schema.md` | Neo4j 스키마 정의 (업데이트 필요) |
| `ARGO_DATA_SOURCE_APIS.md` | 데이터 소스 API 명세 |
| `ARGO_METHODOLOGY.md` | 구조주의 분석 이론 |
| `ARGO_STRUCTURALIST_ALGORITHM_DESIGN.md` | 알고리즘 설계 |

---

**Document Version**: 1.0.0
**Created**: 2025-12-09
**Author**: Claude (Senior Graph Engineer)
**Target**: Antigravity (Gemini 3 Pro)
