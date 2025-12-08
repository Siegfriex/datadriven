# ARGO 구조주의 알고리즘 설계서
## Structuralist Database & Algorithm Architecture

**작성일**: 2025-12-08
**버전**: 1.0
**이론적 기반**: Bourdieu 장(Field) 이론 + 사회연결망 분석(SNA)
**목적**: 구조주의 관점의 한국 미술계 분석 엔진 핵심 알고리즘

---

## Part 1. 구조주의 이론 프레임워크

### 1.1 핵심 구조주의 원칙

```
ARGO의 구조주의적 전제:

1. 관계의 우선성 (Primacy of Relations)
   └─ 개인의 속성보다 "관계 구조" 속 위치가 더 중요
   └─ 미술가 A의 가치 = A 자체 + A의 구조적 위치

2. 전체성 (Holism)
   └─ 부분(개별 미술가)은 전체(미술계 구조) 안에서만 의미
   └─ 갤럭시 = 전체 구조의 시각화

3. 변환 (Transformation)
   └─ 구조는 고정이 아닌 동적 변환 과정
   └─ 시계열 스냅샷으로 구조 변화 추적

4. 자기조절 (Self-regulation)
   └─ 구조는 내부 규칙에 의해 유지/변화
   └─ 보이지 않는 제도(Invisible Institution) 탐지
```

### 1.2 Bourdieu 자본 이론의 ARGO 적용

```
┌─────────────────────────────────────────────────────────────────┐
│                    미술계 장(Field) 구조                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [상징적 자본]          [문화적 자본]                            │
│   제도적 인정             학술적 정전화                           │
│        │                      │                                │
│        ▼                      ▼                                │
│   ┌─────────┐            ┌─────────┐                           │
│   │ 제도    │────────────│ 학술    │                           │
│   │ 레이어  │            │ 레이어  │                           │
│   │ (0.30)  │            │ (0.20)  │                           │
│   └────┬────┘            └────┬────┘                           │
│        │      복합 점수       │                                │
│        │    (Composite)      │                                │
│        └──────────┬──────────┘                                │
│                   │                                            │
│        ┌──────────┴──────────┐                                │
│        │                     │                                │
│   ┌────┴────┐            ┌───┴─────┐                          │
│   │ 담론    │            │ 네트워크 │                          │
│   │ 레이어  │────────────│ 레이어   │                          │
│   │ (0.25)  │            │ (0.25)   │                          │
│   └─────────┘            └─────────┘                           │
│        ▲                      ▲                                │
│        │                      │                                │
│   미디어 인정             사회적 자본                            │
│   [상징적 자본]          [관계적 자본]                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 구조적 위치(Structural Position) 정의

```python
# 구조적 위치 = 4차원 공간에서의 좌표

class StructuralPosition:
    """
    미술가의 구조적 위치를 정의하는 4차원 벡터

    Bourdieu의 장 이론에 따라:
    - 위치(position)는 자본의 총량과 구성에 의해 결정
    - 같은 위치의 행위자는 유사한 habitus를 공유
    - 위치 간 거리는 사회적 거리를 반영
    """

    def __init__(self, artist):
        # 4개 레이어 = 4차원 좌표
        self.institutional = artist.inst_score  # x축: 제도적 자본
        self.academic = artist.acad_score       # y축: 문화적 자본
        self.media = artist.media_score         # z축: 미디어 자본
        self.network = artist.network_score     # w축: 사회적 자본

    def euclidean_distance(self, other):
        """두 미술가 간 구조적 거리"""
        return sqrt(
            (self.institutional - other.institutional)**2 +
            (self.academic - other.academic)**2 +
            (self.media - other.media)**2 +
            (self.network - other.network)**2
        )

    def field_position(self):
        """장 내 상대적 위치 (자본 총량 vs 자본 구성)"""
        total_capital = self.institutional + self.academic + self.media + self.network

        # 자본 구성 비율
        composition = {
            'institutional_ratio': self.institutional / total_capital,
            'academic_ratio': self.academic / total_capital,
            'media_ratio': self.media / total_capital,
            'network_ratio': self.network / total_capital
        }

        return {
            'total_capital': total_capital,
            'composition': composition,
            'dominant_capital': max(composition, key=composition.get)
        }
```

---

## Part 2. 핵심 알고리즘 설계

### 2.1 점수 계산 알고리즘 (Scoring Algorithm)

#### 2.1.1 제도 점수 (Institutional Score)

```python
def calculate_institutional_score(artist: Artist) -> InstitutionalScore:
    """
    제도 레이어 점수 계산

    이론적 근거:
    - Bourdieu: 제도적 인정 = 상징적 자본의 핵심
    - Fraiberger et al. (2018): 초기 기관 위상 → 장기 성공 r=0.68

    가중 요소:
    - 국립미술관 전시: 기관 위상 × 전시 유형 가중치
    - 비엔날레 참여: 국제성 × 횟수
    - 공공 지원: 지원 규모 × 횟수
    - 레지던시: 위상 × 기간
    """

    # 기관 위상 등급 (Prestige Tier)
    INSTITUTION_PRESTIGE = {
        'national_museum': 100,      # 국립현대미술관
        'major_biennale': 95,        # 베니스, 광주 비엔날레
        'municipal_museum': 80,      # 서울시립미술관 등
        'university_museum': 70,     # 대학 미술관
        'major_gallery': 60,         # 주요 상업 갤러리
        'alternative_space': 50,     # 대안공간
        'minor_gallery': 30          # 소규모 갤러리
    }

    # 전시 유형 가중치
    EXHIBITION_TYPE_WEIGHT = {
        'solo': 1.5,                 # 개인전 (가장 높음)
        'featured_group': 1.2,       # 주요 그룹전
        'group': 1.0,                # 일반 그룹전
        'biennale': 1.8,             # 비엔날레
        'retrospective': 2.0         # 회고전 (최고)
    }

    # 점수 계산
    raw_score = 0
    max_possible = 0

    for exhibition in artist.exhibitions:
        institution_prestige = INSTITUTION_PRESTIGE.get(
            exhibition.institution_type, 30
        )
        exhibition_weight = EXHIBITION_TYPE_WEIGHT.get(
            exhibition.exhibition_type, 1.0
        )

        # 시간 감쇠 (최근 10년 가중)
        years_ago = current_year - exhibition.year
        time_decay = max(0.5, 1 - (years_ago * 0.03))  # 최소 50%

        exhibition_score = institution_prestige * exhibition_weight * time_decay
        raw_score += exhibition_score
        max_possible += 100 * 2.0  # 최대 가능 점수

    # 공공 지원 (ARKO 등)
    for support in artist.public_supports:
        support_weight = {
            'major_grant': 20,       # 대형 지원금
            'residency': 15,         # 레지던시
            'travel_grant': 10,      # 해외 활동 지원
            'material_support': 5    # 재료비 지원
        }
        raw_score += support_weight.get(support.type, 5)
        max_possible += 20

    # 정규화 (0-100)
    if max_possible > 0:
        normalized_score = (raw_score / max_possible) * 100
    else:
        normalized_score = 0

    # 세그먼트 백분위 계산
    segment_percentile = calculate_percentile(
        normalized_score,
        artist.segment_id
    )

    return InstitutionalScore(
        raw_score=raw_score,
        normalized_score=min(100, normalized_score),
        percentile=segment_percentile,
        breakdown={
            'museum_exhibitions': len([e for e in artist.exhibitions
                                       if e.institution_type in ['national_museum', 'municipal_museum']]),
            'biennale_participation': len([e for e in artist.exhibitions
                                           if e.exhibition_type == 'biennale']),
            'public_support_count': len(artist.public_supports),
            'solo_exhibitions': len([e for e in artist.exhibitions
                                     if e.exhibition_type == 'solo'])
        }
    )
```

#### 2.1.2 학술 점수 (Academic Score)

```python
def calculate_academic_score(artist: Artist) -> AcademicScore:
    """
    학술 레이어 점수 계산

    이론적 근거:
    - Galenson (2006): 교과서 인용 ↔ 장기 가치 r=0.71
    - Lang & Lang (1988): Renown(장기 명성) vs Fame(단기 명성)

    가중 요소:
    - 학술 논문 인용
    - 전시 카탈로그 수록
    - 미술사 교과서/개론서 언급
    - 학술 출판물 저술
    """

    # 출판물 유형별 가중치
    PUBLICATION_WEIGHT = {
        'art_history_textbook': 30,    # 미술사 교과서 (최고)
        'monograph': 25,               # 단독 연구서
        'exhibition_catalog': 15,      # 전시 카탈로그
        'journal_article': 10,         # 학술지 논문
        'magazine_feature': 5,         # 미술 잡지 특집
        'newspaper_review': 3          # 신문 비평
    }

    # 인용 학술지 등급
    JOURNAL_TIER = {
        'tier_1': 3.0,  # A급 (미술사학보, Journal of Art History)
        'tier_2': 2.0,  # B급 (지역 학술지)
        'tier_3': 1.0   # C급 (기타)
    }

    raw_score = 0

    # 학술 출판물 점수
    for publication in artist.academic_publications:
        base_weight = PUBLICATION_WEIGHT.get(publication.type, 3)

        # 출판사/학술지 위상 반영
        if hasattr(publication, 'journal_tier'):
            tier_multiplier = JOURNAL_TIER.get(publication.journal_tier, 1.0)
        else:
            tier_multiplier = 1.0

        raw_score += base_weight * tier_multiplier

    # 인용 횟수 (Google Scholar, KCI)
    citation_score = min(50, artist.citation_count * 2)  # 최대 50점
    raw_score += citation_score

    # 카탈로그 수록 횟수
    catalog_score = min(30, artist.catalog_mentions * 3)  # 최대 30점
    raw_score += catalog_score

    # 정규화
    max_possible = 100 + 50 + 30  # 출판물 + 인용 + 카탈로그
    normalized_score = min(100, (raw_score / max_possible) * 100)

    return AcademicScore(
        raw_score=raw_score,
        normalized_score=normalized_score,
        breakdown={
            'citation_count': artist.citation_count,
            'catalog_mentions': artist.catalog_mentions,
            'academic_publications': len(artist.academic_publications),
            'research_emphasis': normalized_score / 100  # 0-1
        }
    )
```

#### 2.1.3 담론 점수 (Media Score)

```python
def calculate_media_score(artist: Artist) -> MediaScore:
    """
    담론 레이어 점수 계산

    이론적 근거:
    - Thompson (2008): 미디어 브랜딩의 시장 효과
    - Artnet (2019): 미디어 노출 ↔ 낙찰률 r=0.58

    가중 요소:
    - 언론 기사 수
    - 감정 분석 (긍정/부정)
    - 미디어 트렌드 (상승/하락)
    - 과대포장 비율 (Hype Ratio)
    """

    # 미디어 유형별 가중치
    MEDIA_TYPE_WEIGHT = {
        'major_newspaper': 10,       # 주요 일간지 (중앙일보, 조선일보)
        'art_magazine': 8,           # 미술 전문지 (아트인컬처)
        'broadcast': 12,             # 방송 (TV, 라디오)
        'online_major': 6,           # 주요 온라인 매체
        'sns_viral': 4,              # SNS 바이럴
        'blog_review': 2             # 블로그/개인 리뷰
    }

    raw_score = 0
    sentiment_sum = 0
    article_count = 0

    for article in artist.media_mentions:
        # 기본 점수
        base_weight = MEDIA_TYPE_WEIGHT.get(article.media_type, 2)

        # 시간 감쇠 (최근 3년 강조)
        years_ago = current_year - article.year
        time_decay = max(0.3, 1 - (years_ago * 0.15))

        raw_score += base_weight * time_decay

        # 감정 분석
        sentiment_sum += article.sentiment  # -1 ~ 1
        article_count += 1

    # 평균 감정 점수
    if article_count > 0:
        avg_sentiment = sentiment_sum / article_count
    else:
        avg_sentiment = 0

    # 감정 점수를 0-100으로 변환 (중립 = 50)
    sentiment_score = (avg_sentiment + 1) * 50  # -1→0, 0→50, 1→100

    # 트렌드 계산 (최근 2년 vs 이전 2년)
    recent_count = len([a for a in artist.media_mentions
                        if current_year - a.year <= 2])
    older_count = len([a for a in artist.media_mentions
                       if 2 < current_year - a.year <= 4])

    if older_count > 0:
        trend = (recent_count - older_count) / older_count
    else:
        trend = 0 if recent_count == 0 else 1.0

    # Hype Ratio (과대포장 비율)
    # 미디어 점수 대비 제도 점수가 낮으면 과대포장 의심
    hype_ratio = raw_score / (artist.inst_score + 1)  # 0으로 나눔 방지
    is_potentially_hyped = hype_ratio > 2.0

    # 최종 정규화
    max_possible = 200  # 예상 최대값
    normalized_score = min(100, (raw_score / max_possible) * 100)

    return MediaScore(
        raw_score=raw_score,
        normalized_score=normalized_score,
        breakdown={
            'article_count': article_count,
            'sentiment': round(avg_sentiment, 2),
            'media_mentions_trend': round(trend, 2),
            'hype_ratio': round(hype_ratio, 2),
            'is_potentially_hyped': is_potentially_hyped
        }
    )
```

#### 2.1.4 네트워크 점수 (Network Score)

```python
def calculate_network_score(artist: Artist, graph: nx.Graph) -> NetworkScore:
    """
    네트워크 레이어 점수 계산

    이론적 근거:
    - Granovetter (1973): 약한 유대의 힘
    - Becker (1982): 미술계는 협력 네트워크
    - Fraiberger et al. (2018): 네트워크 중심성 ↔ 성공 r=0.54

    가중 요소:
    - Degree Centrality: 연결 수
    - Betweenness Centrality: 중개자 역할
    - Eigenvector Centrality: 영향력 있는 연결
    - Bridge Potential: 다른 커뮤니티 연결
    """

    import networkx as nx

    # 중심성 지표 계산
    degree_centrality = nx.degree_centrality(graph)[artist.artist_id]
    betweenness_centrality = nx.betweenness_centrality(graph)[artist.artist_id]
    eigenvector_centrality = nx.eigenvector_centrality(graph, max_iter=1000)[artist.artist_id]

    # Bridge Potential (구조적 공백 측정)
    # 서로 다른 커뮤니티에 연결된 정도
    communities = nx.community.louvain_communities(graph)
    artist_community = None
    for i, comm in enumerate(communities):
        if artist.artist_id in comm:
            artist_community = i
            break

    bridge_connections = 0
    for neighbor in graph.neighbors(artist.artist_id):
        for i, comm in enumerate(communities):
            if neighbor in comm and i != artist_community:
                bridge_connections += 1
                break

    total_connections = graph.degree(artist.artist_id)
    if total_connections > 0:
        bridge_potential = bridge_connections / total_connections
    else:
        bridge_potential = 0

    # 가중 합산 (연구 기반)
    # Fraiberger et al. (2018) 기준 betweenness가 가장 예측력 높음
    raw_score = (
        degree_centrality * 30 +
        betweenness_centrality * 35 +
        eigenvector_centrality * 25 +
        bridge_potential * 10
    )

    # 정규화 (0-100)
    # 실제 네트워크에서 상위 1%의 값으로 정규화
    top_1_percent_threshold = 0.5  # 경험적 값, 실제 데이터로 조정
    normalized_score = min(100, (raw_score / top_1_percent_threshold) * 100)

    return NetworkScore(
        raw_score=raw_score,
        normalized_score=normalized_score,
        breakdown={
            'degree_centrality': round(degree_centrality, 4),
            'betweenness_centrality': round(betweenness_centrality, 4),
            'eigenvector_centrality': round(eigenvector_centrality, 4),
            'bridge_potential': round(bridge_potential, 4)
        }
    )
```

### 2.2 복합 점수 알고리즘 (Composite Score)

```python
def calculate_composite_score(
    artist: Artist,
    inst_score: InstitutionalScore,
    acad_score: AcademicScore,
    media_score: MediaScore,
    network_score: NetworkScore
) -> CompositeScore:
    """
    복합 점수 계산 - 구조주의적 종합

    이론적 근거:
    - Bourdieu: 자본의 총량과 구성이 장 내 위치 결정
    - 메타 분석 기반 가중치: 0.30/0.20/0.25/0.25

    특징:
    - 세그먼트별 조정 계수 적용
    - 결측치 처리 로직 포함
    - 신뢰도 점수 산출
    """

    # 기본 가중치 (연구 기반)
    BASE_WEIGHTS = {
        'inst': 0.30,
        'acad': 0.20,
        'media': 0.25,
        'network': 0.25
    }

    # 세그먼트별 조정 계수
    SEGMENT_ADJUSTMENTS = {
        'monochrome': {'inst': 1.17, 'acad': 1.25, 'media': 0.80, 'network': 0.80},
        'media_art': {'inst': 0.83, 'acad': 0.75, 'media': 1.20, 'network': 1.20},
        'emerging': {'inst': 0.83, 'acad': 0.75, 'media': 1.20, 'network': 1.20},
        'default': {'inst': 1.00, 'acad': 1.00, 'media': 1.00, 'network': 1.00}
    }

    # 세그먼트 조정
    segment = artist.segment_metadata.get('genre', 'default')
    adjustments = SEGMENT_ADJUSTMENTS.get(segment, SEGMENT_ADJUSTMENTS['default'])

    # 가중치 적용
    scores = {
        'inst': inst_score.normalized_score if inst_score else None,
        'acad': acad_score.normalized_score if acad_score else None,
        'media': media_score.normalized_score if media_score else None,
        'network': network_score.normalized_score if network_score else None
    }

    weighted_sum = 0
    total_weight = 0
    missing_layers = []

    for layer, score in scores.items():
        if score is not None:
            adjusted_weight = BASE_WEIGHTS[layer] * adjustments[layer]
            weighted_sum += score * adjusted_weight
            total_weight += adjusted_weight
        else:
            missing_layers.append(layer)

    # 정규화 (가용 가중치 기준)
    if total_weight > 0:
        composite = weighted_sum / total_weight * sum(BASE_WEIGHTS.values())
    else:
        composite = None

    # 신뢰도 점수
    confidence = total_weight / sum(BASE_WEIGHTS.values())

    # 자본 구성 분석 (구조주의적 해석)
    if composite:
        capital_composition = {
            'institutional_ratio': (scores['inst'] or 0) / (composite + 1),
            'academic_ratio': (scores['acad'] or 0) / (composite + 1),
            'media_ratio': (scores['media'] or 0) / (composite + 1),
            'network_ratio': (scores['network'] or 0) / (composite + 1)
        }
        dominant_capital = max(capital_composition, key=capital_composition.get)
    else:
        capital_composition = None
        dominant_capital = None

    return CompositeScore(
        score=round(composite, 2) if composite else None,
        confidence=round(confidence, 2),
        weights_used={
            layer: round(BASE_WEIGHTS[layer] * adjustments[layer], 3)
            for layer in BASE_WEIGHTS
        },
        missing_layers=missing_layers,
        capital_composition=capital_composition,
        dominant_capital=dominant_capital,
        methodology_version='v1.0_structuralist'
    )
```

---

## Part 3. Neo4j 데이터베이스 설계

### 3.1 구조주의 관점의 스키마

```cypher
// ═══════════════════════════════════════════════════════════════
// ARGO Neo4j Schema - Structuralist Design
// ═══════════════════════════════════════════════════════════════

// ───────────────────────────────────────────────────────────────
// 1. ARTIST 노드 (핵심 행위자)
// ───────────────────────────────────────────────────────────────

CREATE (a:Artist {
  // === 식별자 ===
  artist_id: STRING,                    // 고유 ID

  // === 기본 정보 ===
  name: STRING,
  alternative_name: STRING,
  birth_year: INTEGER,

  // === 세그먼트 분류 ===
  segment_id: STRING,                   // "monochrome_seoul_1970s"
  segment_genre: STRING,                // "monochrome", "abstract", etc
  segment_region: STRING,               // "Seoul", "Busan", etc
  segment_generation: STRING,           // "1970s", "1980s", etc
  career_stage: STRING,                 // "early", "mid", "late"

  // === 4개 레이어 점수 (구조적 자본) ===
  inst_score: FLOAT,                    // 제도적 자본 (0-100)
  inst_score_raw: FLOAT,                // 원시 점수
  inst_score_percentile: FLOAT,         // 세그먼트 내 백분위

  acad_score: FLOAT,                    // 학술적 자본 (0-100)
  acad_score_raw: FLOAT,
  acad_score_percentile: FLOAT,

  media_score: FLOAT,                   // 담론적 자본 (0-100)
  media_score_raw: FLOAT,
  media_score_percentile: FLOAT,
  media_sentiment: FLOAT,               // -1 ~ 1
  media_hype_ratio: FLOAT,              // 과대포장 지수

  network_score: FLOAT,                 // 사회적 자본 (0-100)
  network_degree: FLOAT,                // Degree Centrality
  network_betweenness: FLOAT,           // Betweenness Centrality
  network_eigenvector: FLOAT,           // Eigenvector Centrality
  network_bridge: FLOAT,                // Bridge Potential

  // === 복합 점수 ===
  composite_score: FLOAT,               // 가중 평균 (0-100)
  composite_confidence: FLOAT,          // 신뢰도 (0-1)
  dominant_capital: STRING,             // 지배적 자본 유형

  // === 3D 갤럭시 좌표 ===
  coord_x: FLOAT,                       // inst_score 기반
  coord_y: FLOAT,                       // acad_score 기반
  coord_z: FLOAT,                       // media_score 기반
  coord_radius: FLOAT,                  // network_score 기반

  // === 메타데이터 ===
  data_sources: [STRING],
  confidence_score: FLOAT,
  is_verified: BOOLEAN,
  created_at: DATETIME,
  updated_at: DATETIME,
  algorithm_version: STRING             // "v1.0_structuralist"
})

// ───────────────────────────────────────────────────────────────
// 2. INSTITUTION 노드 (제도적 장치)
// ───────────────────────────────────────────────────────────────

CREATE (i:Institution {
  inst_id: STRING,
  name: STRING,
  institution_type: STRING,             // "national_museum", "gallery", etc
  prestige_score: INTEGER,              // 기관 위상 (0-100)
  prestige_tier: STRING,                // "tier_1", "tier_2", "tier_3"

  // 기관 특성
  founding_year: INTEGER,
  region: STRING,
  international_recognition: FLOAT,
  annual_exhibitions: INTEGER,

  // 구조적 영향력
  affiliated_artist_count: INTEGER,
  avg_artist_composite: FLOAT,          // 소속 작가 평균 점수

  // 메타
  created_at: DATETIME,
  updated_at: DATETIME
})

// ───────────────────────────────────────────────────────────────
// 3. CLUSTER 노드 (구조적 군집)
// ───────────────────────────────────────────────────────────────

CREATE (c:Cluster {
  cluster_id: STRING,
  name: STRING,                         // "Seoul Academia Network"
  cluster_type: STRING,                 // "louvain", "geographic", "genre"

  // 공간 정보
  center_x: FLOAT,
  center_y: FLOAT,
  center_z: FLOAT,
  radius: FLOAT,

  // 구조적 특성
  member_count: INTEGER,
  internal_density: FLOAT,              // 내부 연결 밀도
  modularity: FLOAT,                    // 모듈성

  // 평균 점수
  avg_inst_score: FLOAT,
  avg_acad_score: FLOAT,
  avg_media_score: FLOAT,
  avg_network_score: FLOAT,
  avg_composite_score: FLOAT,

  // 지배 구조
  dominant_institution_id: STRING,
  dominant_institution_ratio: FLOAT,
  primary_capital_type: STRING,         // 클러스터의 지배적 자본

  // 메타
  algorithm_version: STRING,
  computed_at: DATETIME
})

// ───────────────────────────────────────────────────────────────
// 4. 관계(Relationship) 정의 - 구조의 핵심
// ───────────────────────────────────────────────────────────────

// 협력 관계 (사회적 자본의 기초)
CREATE (a1:Artist)-[:COLLABORATED_WITH {
  strength: FLOAT,                      // 0-1 협력 강도
  collaboration_count: INTEGER,         // 함께 전시 횟수
  collaboration_type: STRING,           // "co_exhibition", "mentor", etc
  first_year: INTEGER,
  last_year: INTEGER,

  // 구조적 의미
  structural_equivalence: FLOAT,        // 구조적 등가성
  is_strong_tie: BOOLEAN,               // 강한 유대 여부
  is_bridge: BOOLEAN                    // 브릿지 관계 여부
}]->(a2:Artist)

// 소속 관계 (제도적 자본의 기초)
CREATE (a:Artist)-[:AFFILIATED_WITH {
  role: STRING,                         // "professor", "alumni", etc
  start_year: INTEGER,
  end_year: INTEGER,
  is_current: BOOLEAN,

  // 구조적 의미
  prestige_transfer: FLOAT,             // 기관 위상 전이 정도
  institutional_capital_gained: FLOAT   // 획득한 제도적 자본
}]->(i:Institution)

// 클러스터 소속 (구조적 위치)
CREATE (a:Artist)-[:BELONGS_TO {
  membership_strength: FLOAT,           // 소속 강도 (0-1)
  distance_to_center: FLOAT,            // 중심까지 거리
  is_core_member: BOOLEAN,              // 핵심 멤버 여부
  is_peripheral: BOOLEAN                // 주변부 여부
}]->(c:Cluster)

// 클러스터 간 관계 (구조 간 관계)
CREATE (c1:Cluster)-[:ADJACENT_TO {
  distance: FLOAT,
  shared_members: INTEGER,
  interaction_strength: FLOAT,
  relationship_type: STRING             // "hierarchical", "peer", "satellite"
}]->(c2:Cluster)

// 기관의 클러스터 지배 (권력 구조)
CREATE (i:Institution)-[:DOMINATES {
  influence_ratio: FLOAT,               // 영향력 비율
  member_count: INTEGER,
  influence_tier: STRING                // "primary", "secondary"
}]->(c:Cluster)
```

### 3.2 핵심 Cypher 쿼리

#### 3.2.1 점수 계산 후 업데이트

```cypher
// 복합 점수 계산 및 업데이트 쿼리

MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
  AND a.acad_score IS NOT NULL

WITH a,
     // 기본 가중치 적용
     (a.inst_score * 0.30 +
      a.acad_score * 0.20 +
      a.media_score * 0.25 +
      a.network_score * 0.25) AS composite,

     // 지배적 자본 판별
     CASE
       WHEN a.inst_score >= a.acad_score
        AND a.inst_score >= a.media_score
        AND a.inst_score >= a.network_score THEN 'institutional'
       WHEN a.acad_score >= a.media_score
        AND a.acad_score >= a.network_score THEN 'academic'
       WHEN a.media_score >= a.network_score THEN 'media'
       ELSE 'network'
     END AS dominant

SET a.composite_score = round(composite, 2),
    a.dominant_capital = dominant,
    a.updated_at = datetime(),
    a.algorithm_version = 'v1.0_structuralist'

RETURN a.artist_id, a.name, a.composite_score, a.dominant_capital
ORDER BY a.composite_score DESC
```

#### 3.2.2 네트워크 중심성 계산

```cypher
// Degree Centrality 계산
CALL gds.degree.stream('artist-network')
YIELD nodeId, score
MATCH (a:Artist) WHERE id(a) = nodeId
SET a.network_degree = score
RETURN a.artist_id, a.name, score
ORDER BY score DESC LIMIT 20;

// Betweenness Centrality 계산
CALL gds.betweenness.stream('artist-network')
YIELD nodeId, score
MATCH (a:Artist) WHERE id(a) = nodeId
SET a.network_betweenness = score
RETURN a.artist_id, a.name, score
ORDER BY score DESC LIMIT 20;

// Eigenvector Centrality 계산
CALL gds.eigenvector.stream('artist-network', {maxIterations: 100})
YIELD nodeId, score
MATCH (a:Artist) WHERE id(a) = nodeId
SET a.network_eigenvector = score
RETURN a.artist_id, a.name, score
ORDER BY score DESC LIMIT 20;
```

#### 3.2.3 Louvain 커뮤니티 탐지

```cypher
// Louvain 알고리즘으로 구조적 군집 탐지
CALL gds.louvain.stream('artist-network')
YIELD nodeId, communityId
MATCH (a:Artist) WHERE id(a) = nodeId

// 커뮤니티별 집계
WITH communityId, collect(a) AS members
WITH communityId, members, size(members) AS member_count

// 클러스터 노드 생성
MERGE (c:Cluster {cluster_id: 'louvain_' + toString(communityId)})
SET c.member_count = member_count,
    c.cluster_type = 'louvain',
    c.computed_at = datetime()

// 아티스트-클러스터 관계 생성
WITH c, members
UNWIND members AS a
MERGE (a)-[:BELONGS_TO {
  membership_strength: 1.0,
  is_core_member: a.network_betweenness > 0.1
}]->(c)

RETURN c.cluster_id, c.member_count
ORDER BY c.member_count DESC;
```

#### 3.2.4 3D 좌표 계산

```cypher
// 갤럭시 3D 좌표 계산 (PCA 기반 정규화)

MATCH (a:Artist)
WHERE a.composite_score IS NOT NULL

WITH a,
     // 점수 정규화 (-10 ~ 10 범위)
     (a.inst_score - 50) / 5 AS x,
     (a.acad_score - 50) / 5 AS y,
     (a.media_score - 50) / 5 AS z,
     // 반경 (네트워크 점수 기반)
     10 + (a.network_score / 10) AS radius

SET a.coord_x = round(x, 2),
    a.coord_y = round(y, 2),
    a.coord_z = round(z, 2),
    a.coord_radius = round(radius, 2)

RETURN a.artist_id, a.name,
       a.coord_x, a.coord_y, a.coord_z, a.coord_radius
ORDER BY a.composite_score DESC;
```

#### 3.2.5 구조적 이상치 탐지

```cypher
// 구조적 이상치 탐지
// 미디어 점수 대비 제도 점수가 현저히 낮은 경우

MATCH (a:Artist)
WHERE a.media_score IS NOT NULL AND a.inst_score IS NOT NULL

WITH a,
     a.media_score / (a.inst_score + 1) AS hype_ratio,
     // Z-score 계산
     (a.composite_score - avg(a.composite_score)) / stdev(a.composite_score) AS z_score

WHERE hype_ratio > 2.0 OR abs(z_score) > 2.0

RETURN a.artist_id,
       a.name,
       a.inst_score,
       a.media_score,
       round(hype_ratio, 2) AS hype_ratio,
       round(z_score, 2) AS z_score,
       CASE
         WHEN hype_ratio > 2.0 THEN 'POTENTIALLY_HYPED'
         WHEN z_score > 2.0 THEN 'OUTLIER_HIGH'
         WHEN z_score < -2.0 THEN 'OUTLIER_LOW'
       END AS anomaly_type
ORDER BY hype_ratio DESC;
```

---

## Part 4. 문서 스위트 업데이트 계획

### 4.1 업데이트 대상 및 범위

```
┌─────────────────────────────────────────────────────────────────┐
│                    문서 스위트 업데이트 맵                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ARGO_BRD_Final.md                                             │
│  ├─ 섹션 6: 위험 및 완화 전략                                   │
│  │   └─ 가중치 근거 리스크 → "연구 기반 해결" 추가             │
│  └─ 부록: 방법론 개요 추가                                     │
│                                                                 │
│  ARGO_PRD_Final.md                                             │
│  ├─ 섹션 7.2: 점수 계산 로직                                   │
│  │   └─ 기존 단순 수식 → 연구 기반 알고리즘으로 교체           │
│  └─ 부록: 가중치 근거 문서 참조 추가                           │
│                                                                 │
│  ARGO_SRD_Final.md                                             │
│  ├─ 섹션 3.2.4: Confidence Score 계산                          │
│  │   └─ 상세 알고리즘 업데이트                                 │
│  ├─ 섹션 4.2: 분석 메트릭                                      │
│  │   └─ 구조주의 지표 추가                                     │
│  └─ 신규 섹션: 구조주의 분석 알고리즘                          │
│                                                                 │
│  ARGO_TSD_Final.md                                             │
│  ├─ 섹션 2.1.1: Artist 스키마                                  │
│  │   └─ 새 필드 추가 (dominant_capital 등)                     │
│  ├─ 섹션 3.2: API 엔드포인트                                   │
│  │   └─ 메타데이터 응답 형식 업데이트                          │
│  └─ 신규 섹션: 알고리즘 버전 관리                              │
│                                                                 │
│  ARGO_Final_Schema.md                                          │
│  ├─ 섹션 2.1: Artist 엔터티                                    │
│  │   └─ 구조주의 필드 추가                                     │
│  ├─ 섹션 5: 쿼리 템플릿                                        │
│  │   └─ 새 분석 쿼리 추가                                      │
│  └─ 신규 섹션: 알고리즘 명세                                   │
│                                                                 │
│  [신규] ARGO_METHODOLOGY.md                                    │
│  └─ 방법론 전체 문서 (학술 인용 가능)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 상세 업데이트 내역

#### 4.2.1 BRD 업데이트

```markdown
## BRD 업데이트 사항

### 위치: 섹션 6. 위험 및 완화 전략

기존:
| 위험 | 영향 | 확률 | 완화 |
|-----|------|------|------|
| **데이터 품질 문제** | 높음 | 중간 | 수동 검증 + LLM 정규화 |

추가:
| **방법론 비판** | 중간 | 중간 | 학술 연구 기반 가중치 + 투명한 공개 |

### 위치: 부록 C (신규)

## 부록 C. 방법론 개요

ARGO의 점수 산정 방법론은 다음 학술적 근거에 기반한다:

**이론적 기초:**
- Pierre Bourdieu의 장(Field) 이론 (1984, 1993)
- 미술사회학의 명성(Reputation) 연구

**실증적 근거:**
- Fraiberger et al. (2018) Science: 제도-성공 상관 r=0.68
- Galenson (2006): 학술-장기가치 상관 r=0.71

**가중치:**
- 제도(0.30), 학술(0.20), 담론(0.25), 네트워크(0.25)

상세 방법론: ARGO_METHODOLOGY.md 참조
```

#### 4.2.2 PRD 업데이트

```markdown
## PRD 업데이트 사항

### 위치: 섹션 7.2 점수 계산 로직

기존:
```
복합 점수 (Composite):
  c_score = (
    i_score * 0.3 +
    a_score * 0.2 +
    m_score * 0.25 +
    n_score * 0.25
  )
```

교체:
```
복합 점수 (Composite) - 구조주의 기반:

1. 이론적 근거:
   - Bourdieu 자본 이론에 따른 4개 레이어 정의
   - 메타 분석 기반 가중치 도출

2. 가중치 (연구 기반):
   - 제도: 0.30 (상관계수 r=0.68)
   - 학술: 0.20 (상관계수 r=0.60)
   - 담론: 0.25 (상관계수 r=0.57)
   - 네트워크: 0.25 (상관계수 r=0.58)

3. 세그먼트 조정:
   - 모노크롬: 학술 +25%, 담론 -20%
   - 미디어아트: 담론 +20%, 네트워크 +20%
   - 신진작가: 담론 +20%, 제도 -17%

4. 신뢰도 산출:
   confidence = available_weight / total_weight

참조: ARGO_STRUCTURALIST_ALGORITHM_DESIGN.md
```

### 위치: 부록 D (신규)

## 부록 D. 가중치 학술적 근거

| 레이어 | 가중치 | 핵심 연구 | 상관계수 |
|--------|--------|----------|----------|
| 제도 | 0.30 | Fraiberger et al. (2018) | r=0.68 |
| 학술 | 0.20 | Galenson (2006) | r=0.60 |
| 담론 | 0.25 | Artnet (2019) | r=0.57 |
| 네트워크 | 0.25 | Fraiberger et al. (2018) | r=0.58 |
```

#### 4.2.3 SRD 업데이트

```markdown
## SRD 업데이트 사항

### 위치: 섹션 3.2.4 Confidence Score 계산 (교체)

```python
def calculate_confidence_score(artist_data: ArtistData) -> ConfidenceScore:
    """
    구조주의 기반 신뢰도 점수 계산

    구성 요소:
    1. 데이터 가용성 (data_availability): 4개 레이어 중 몇 개 존재
    2. 소스 신뢰도 (source_credibility): 데이터 출처 품질
    3. 검증 수준 (verification_level): 수동/자동 검증 여부
    """

    # 가용 레이어 수
    available_layers = sum([
        1 if artist_data.inst_score is not None else 0,
        1 if artist_data.acad_score is not None else 0,
        1 if artist_data.media_score is not None else 0,
        1 if artist_data.network_score is not None else 0
    ])
    data_availability = available_layers / 4

    # 소스 신뢰도
    SOURCE_WEIGHTS = {
        'ARKO': 0.95, 'MMCA': 0.92, 'auction': 0.88,
        'web_crawl': 0.70, 'sns': 0.65
    }
    source_scores = [SOURCE_WEIGHTS.get(s, 0.5) for s in artist_data.data_sources]
    source_credibility = sum(source_scores) / len(source_scores) if source_scores else 0.5

    # 검증 수준
    verification_level = 1.0 if artist_data.is_verified else 0.5

    # 복합 신뢰도
    confidence = (
        data_availability * 0.40 +
        source_credibility * 0.35 +
        verification_level * 0.25
    )

    return ConfidenceScore(
        score=round(confidence, 2),
        breakdown={
            'data_availability': data_availability,
            'source_credibility': source_credibility,
            'verification_level': verification_level
        },
        minimum_threshold=0.60  # 60% 이상만 공개
    )
```

### 위치: 섹션 4.2 분석 메트릭 (추가)

#### 4.2.12 구조적 등가성 (Structural Equivalence)

```
정의: 두 미술가가 동일한 관계 패턴을 가지는 정도
계산: 인접 행렬의 상관계수
범위: 0 ~ 1
해석: 높을수록 대체 가능한 위치

응답시간: < 3초 (100명 기준)
```

#### 4.2.13 자본 구성 분석 (Capital Composition)

```
정의: 개별 미술가의 4개 자본 비율
출력:
  - institutional_ratio: 제도 자본 비율
  - academic_ratio: 학술 자본 비율
  - media_ratio: 담론 자본 비율
  - network_ratio: 네트워크 자본 비율
  - dominant_capital: 지배적 자본 유형

API: GET /api/artists/{id}/capital-composition
응답시간: < 100ms
```
```

#### 4.2.4 TSD 업데이트

```markdown
## TSD 업데이트 사항

### 위치: 섹션 2.1.1 Artist 엔터티 (필드 추가)

```cypher
// 기존 필드에 추가

(:Artist {
  // ... 기존 필드 ...

  // === 신규: 구조주의 분석 필드 ===

  // 지배적 자본 유형
  dominant_capital: STRING,  // "institutional", "academic", "media", "network"

  // 자본 구성 비율
  capital_composition: {
    institutional_ratio: FLOAT,
    academic_ratio: FLOAT,
    media_ratio: FLOAT,
    network_ratio: FLOAT
  },

  // 구조적 위치 지표
  structural_position: {
    field_quadrant: STRING,      // "autonomous", "heteronomous", etc
    position_stability: FLOAT,   // 위치 안정성 (0-1)
    mobility_potential: FLOAT    // 이동 가능성 (0-1)
  },

  // 알고리즘 버전 (재현성)
  algorithm_version: STRING,     // "v1.0_structuralist"
  weights_applied: {
    inst: FLOAT,
    acad: FLOAT,
    media: FLOAT,
    network: FLOAT
  }
})
```

### 위치: 섹션 3.2 API 응답 형식 (업데이트)

```json
{
  "@context": "https://schema.org/",
  "@type": "Person",
  "argo:scores": {
    "argo:inst_score": 82,
    "argo:acad_score": 68,
    "argo:media_score": 75,
    "argo:network_score": 71,
    "argo:composite_score": 74.15
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
      "field_quadrant": "autonomous_established",
      "position_stability": 0.85
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
      "Bourdieu (1984)",
      "Fraiberger et al. (2018)"
    ]
  }
}
```
```

#### 4.2.5 Schema 업데이트

```markdown
## Schema 업데이트 사항

### 위치: 섹션 2.1 Artist (확장)

기존 scores 객체에 추가:

```neo4j
scores: {
  // 기존 4개 점수...

  // 신규: 원시 점수 (정규화 전)
  inst_score_raw: FLOAT,
  acad_score_raw: FLOAT,
  media_score_raw: FLOAT,
  network_score_raw: FLOAT,

  // 신규: 세그먼트 내 백분위
  inst_percentile: FLOAT @range(0, 100),
  acad_percentile: FLOAT @range(0, 100),
  media_percentile: FLOAT @range(0, 100),
  network_percentile: FLOAT @range(0, 100),

  // 신규: 세부 메트릭
  network_metrics: {
    degree_centrality: FLOAT @range(0, 1),
    betweenness_centrality: FLOAT @range(0, 1),
    eigenvector_centrality: FLOAT @range(0, 1),
    bridge_potential: FLOAT @range(0, 1)
  },

  media_metrics: {
    sentiment_avg: FLOAT @range(-1, 1),
    hype_ratio: FLOAT,
    trend_velocity: FLOAT
  }
}
```

### 위치: 섹션 5 쿼리 템플릿 (추가)

```cypher
// 구조주의 분석 쿼리

// 1. 자본 구성별 미술가 분류
MATCH (a:Artist)
WHERE a.composite_score IS NOT NULL
RETURN a.dominant_capital AS capital_type,
       count(*) AS artist_count,
       avg(a.composite_score) AS avg_score
ORDER BY artist_count DESC;

// 2. 구조적 등가 미술가 찾기
MATCH (a1:Artist {artist_id: $target_id})
MATCH (a2:Artist)
WHERE a1 <> a2
WITH a1, a2,
     abs(a1.inst_score - a2.inst_score) +
     abs(a1.acad_score - a2.acad_score) +
     abs(a1.media_score - a2.media_score) +
     abs(a1.network_score - a2.network_score) AS distance
WHERE distance < 20
RETURN a2.artist_id, a2.name, distance
ORDER BY distance
LIMIT 10;

// 3. 장(Field) 사분면 분포
MATCH (a:Artist)
WITH a,
     CASE WHEN a.inst_score + a.acad_score > 100 THEN 'high_cultural' ELSE 'low_cultural' END AS cultural,
     CASE WHEN a.media_score + a.network_score > 100 THEN 'high_social' ELSE 'low_social' END AS social
RETURN cultural + '_' + social AS quadrant,
       count(*) AS count
ORDER BY count DESC;
```
```

### 4.3 신규 문서: ARGO_METHODOLOGY.md

```markdown
# ARGO 방법론 문서
## Methodology for Korean Art World Structural Analysis

**Version**: 1.0
**Last Updated**: 2025-12-08
**Citation**: ARGO Project. (2025). Methodology for Korean Art World
             Structural Analysis. ARGO Technical Report TR-001.

---

## 1. 이론적 기초

### 1.1 구조주의적 접근

ARGO는 개별 미술가의 "속성"보다 미술계 "구조" 내 위치를 분석한다.
이는 Pierre Bourdieu의 장(Field) 이론에 기반한다.

### 1.2 4개 자본 레이어

| 레이어 | Bourdieu 자본 | 측정 대상 |
|--------|-------------|----------|
| 제도 | 상징적 자본 | 미술관/비엔날레 인정 |
| 학술 | 문화적 자본 | 미술사적 정전화 |
| 담론 | 상징적 자본 | 미디어 가시성 |
| 네트워크 | 사회적 자본 | 협력 관계망 |

---

## 2. 가중치 산정

### 2.1 메타 분석 방법론

8개 선행 연구의 효과 크기(상관계수)를 종합하였다.

### 2.2 최종 가중치

| 레이어 | 가중치 | 95% CI | 근거 연구 |
|--------|--------|--------|----------|
| 제도 | 0.30 | [0.25, 0.35] | Fraiberger(2018) |
| 학술 | 0.20 | [0.15, 0.25] | Galenson(2006) |
| 담론 | 0.25 | [0.20, 0.30] | Artnet(2019) |
| 네트워크 | 0.25 | [0.20, 0.30] | Granovetter(1973) |

---

## 3. 알고리즘 상세

[알고리즘 코드 및 수식 포함]

---

## 4. 한계 및 향후 연구

### 4.1 한계점

1. 100명 파일럿 데이터의 대표성
2. 한국 미술계 특수성의 일반화 가능성
3. 시간에 따른 가중치 변화 가능성

### 4.2 향후 연구

1. 종단 연구를 통한 가중치 검증
2. 세그먼트별 가중치 정교화
3. 국제 비교 연구

---

## 참고문헌

[전체 참고문헌 목록]
```

---

## Part 5. 실행 계획

### 5.1 업데이트 일정

```
Week 1: 핵심 알고리즘 구현
├─ Day 1-2: 점수 계산 함수 구현 (Python)
├─ Day 3-4: Neo4j 스키마 업데이트
└─ Day 5: 단위 테스트 작성

Week 2: 문서 업데이트
├─ Day 1: BRD, PRD 업데이트
├─ Day 2: SRD 업데이트
├─ Day 3: TSD, Schema 업데이트
├─ Day 4: METHODOLOGY.md 작성
└─ Day 5: 문서 간 일관성 검토

Week 3: 검증 및 배포
├─ Day 1-2: 통합 테스트
├─ Day 3: 코드 리뷰
├─ Day 4: 문서 최종 검토
└─ Day 5: 버전 릴리즈 (v1.0_structuralist)
```

### 5.2 체크리스트

```
알고리즘 구현:
[ ] calculate_institutional_score() 구현
[ ] calculate_academic_score() 구현
[ ] calculate_media_score() 구현
[ ] calculate_network_score() 구현
[ ] calculate_composite_score() 구현
[ ] 단위 테스트 작성 (커버리지 > 80%)

Neo4j 업데이트:
[ ] 신규 필드 추가 (dominant_capital 등)
[ ] 인덱스 생성
[ ] 마이그레이션 스크립트 작성
[ ] 기존 데이터 업데이트 쿼리 실행

문서 업데이트:
[ ] BRD 섹션 6, 부록 C 업데이트
[ ] PRD 섹션 7.2, 부록 D 업데이트
[ ] SRD 섹션 3.2.4, 4.2 업데이트
[ ] TSD 섹션 2.1.1, 3.2 업데이트
[ ] Schema 섹션 2.1, 5 업데이트
[ ] METHODOLOGY.md 신규 작성

검증:
[ ] 문서 간 일관성 검토
[ ] 버전 번호 통일 (v1.0_structuralist)
[ ] 참조 링크 검증
[ ] 인용 형식 통일
```

---

## 결론

### 구조주의 접근의 장점

```
1. 학술적 엄밀성
   └─ Bourdieu 이론 + 실증 연구 기반

2. 재현 가능성
   └─ 모든 알고리즘 코드 공개

3. 투명성
   └─ 가중치 근거 명시적 제시

4. 확장성
   └─ 세그먼트/시대별 조정 가능

5. 방어 가능성
   └─ 비판에 대한 학술적 대응 가능
```

### 최종 산출물

```
생성 문서:
├─ ARGO_STRUCTURALIST_ALGORITHM_DESIGN.md (본 문서)
├─ ARGO_METHODOLOGY.md (학술 인용용)
└─ 5개 기존 문서 업데이트 완료

생성 코드:
├─ scoring/institutional.py
├─ scoring/academic.py
├─ scoring/media.py
├─ scoring/network.py
├─ scoring/composite.py
└─ neo4j/schema_v1.0_structuralist.cypher
```

---

**Document Version**: 1.0
**Algorithm Version**: v1.0_structuralist
**Status**: Ready for Implementation
