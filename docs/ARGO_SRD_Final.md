# ARGO: 한국 미술계 구조 분석 엔진
## Software Requirement Specification (SRD)
### 상세 기술 요구사항 명세서

**Version**: 1.0  
**Last Updated**: 2025-12-08  
**Status**: Development Ready  
**Target Audience**: Engineering Team, QA, Architects

---

## Executive Summary

**SRD는 BRD(비즈니스) + PRD(제품) + TSD(기술)의 구체적 구현 명세다.**

이 문서는 다음을 정의한다:
- ✅ **5가지 핵심 기능**의 상세 기술 명세
- ✅ **20+ API 엔드포인트**의 완벽한 명세
- ✅ **기능별 KPI & 성능 목표**
- ✅ **테스트 기준 & 인수인계 체크리스트**
- ✅ **배포 마일스톤 & 우선순위**

개발팀은 이 SRD를 기반으로 **Cursor, Antigravity, Google AI Studio에서 바로 코드 생성 가능**하다.

---

## 1. 핵심 기능 정의

### 1.1 5가지 핵심 기능 분류

| # | 기능명 | 담당팀 | 우선순위 | Phase | 목표 KPI |
|---|--------|--------|---------|-------|---------|
| **F1** | 3D 갤럭시 시각화 | Frontend | P0 | 1 | 60 FPS, 3초 로딩 |
| **F2** | 미술가 데이터 관리 | Backend | P0 | 1 | 100명 + 신뢰도 0.85 |
| **F3** | 분석 대시보드 | Frontend + Backend | P1 | 2 | 10+ 분석 메트릭 |
| **F4** | 이상치 탐지 | Backend + ML | P1 | 2 | 정확도 80%, 응답시간 2초 |
| **F5** | 공개 API & 데이터 | Backend | P1 | 2 | 20+ 엔드포인트, 월 500만 요청 |

---

## 2. Feature 1: 3D 갤럭시 시각화 (F1)

### 2.1 기능 개요

**목적**: 한국 미술계의 복잡한 구조를 **3D 입자 시스템**으로 시각화하여 사용자가 직관적으로 권력 구조를 파악할 수 있게 함.

**사용자 경험**:
1. 홈화면 로드 → 3D 갤럭시 자동 렌더링
2. 마우스 드래그: 카메라 회전
3. 스크롤: 줌 인/아웃
4. 클릭: 미술가 선택 → 우측 패널에 정보 표시
5. 필터 선택: 갤럭시 동적 업데이트

### 2.2 기술 명세

#### 2.2.1 렌더링 엔진

```
라이브러리: Three.js r128+
조건: 
  - WebGL 2.0 지원 필수
  - 최소 메모리: 512MB
  - GPU: NVIDIA, AMD, Intel 호환

캔버스 크기:
  - 데스크톱: 60% 화면 너비
  - 태블릿: 70% 화면 너비
  - 모바일: 90% 화면 너비

렌더링 목표:
  - 프레임 레이트: 60 FPS (desktop), 30 FPS (mobile)
  - 응답성: 16ms 이내 (60 FPS)
  - 줌 범위: 0.5x ~ 10x
```

#### 2.2.2 입자 시스템 (Particle System)

```typescript
// 구성 요소
입자 수: 100명 (Phase 1) ~ 2,000명 (Phase 3)
입자 타입: Points (성능 최적화)

속성별 인코딩:
  - 위치 (x, y, z): 3D 좌표
    x축: inst_score (제도 레이어) [-10 ~ 10]
    y축: acad_score (학술 레이어) [-10 ~ 10]
    z축: media_score (담론 레이어) [-10 ~ 10]
  
  - 색상 (R, G, B): 4개 점수 시각화
    R: inst_score (0~100 → 0~255)
    G: acad_score (0~100 → 0~255)
    B: media_score (0~100 → 0~255)
    (Alpha: 0.8 기본값, 선택시 1.0)
  
  - 크기 (radius): network_score 반영
    base_radius: 5px
    final_size: base_radius + (network_score / 100) * 15px
    범위: 5px ~ 20px
  
  - Emissive (발광): composite_score
    0~50: 어두움 (검은색 발광)
    50~70: 중간 (회색 발광)
    70~100: 밝음 (흰색 발광)

성능 최적화:
  - InstancedMesh 사용 (GPU 메모리 효율)
  - LOD (Level of Detail) 구현
    거리 > 50 units: 점 크기 감소
    거리 > 100 units: 색상 단순화
  - 뷰 프러스텀 컬링 (화면 밖 객체 제외)
  - 오클루전 컬링 (가려진 객체 제외)
```

#### 2.2.3 카메라 제어 (Camera Controls)

```
제어 방식:
  - Trackball Camera (직관적 회전)
  - 마우스 드래그: 좌회전 (수평), 상하회전 (수직)
  - 스크롤: 줌 (마우스 위치 중심)
  - 더블클릭: 선택된 입자로 자동 포커싱
  - 우클릭: 카메라 리셋

키보드 단축키:
  - R: 카메라 리셋
  - H: 홈 위치로 이동
  - F: 선택된 입자 포커싱
  - Esc: 선택 해제

애니메이션:
  - 카메라 이동: 0.5초 (easing: ease-in-out)
  - 줌 애니메이션: 0.3초
  - 입자 하이라이트: 0.2초 (opacity 전환)
```

#### 2.2.4 상호작용 (Interaction)

```
클릭 탐지:
  - Raycaster 사용 (Three.js 내장)
  - 마우스 위치 → 3D 좌표 변환
  - 클릭 가능 반경: 입자 크기의 2배
  - 겹침: 카메라에 가장 가까운 입자 선택

선택 시각화:
  - 선택 입자: 색상 증폭 (saturate 150%)
  - 선택 입자 주변: 연결선 표시
    - 협력자: 파란색 선 (strength ≥ 0.3)
    - 소속 기관: 초록색 선
    - 전시 참여: 황색 선
  - 연결선 애니메이션: 0.3초 fade-in

마우스 오버 (Hover):
  - 호버 입자: 아우라 표시 (0.2초)
  - 입자명 Tooltip 표시 (200ms 딜레이)
  - Tooltip 위치: 마우스 우상향 20px
  - Tooltip 자동 사라짐: 3초 후
```

#### 2.2.5 필터 동적 업데이트

```
필터 적용 시나리오:
1. 사용자 필터 선택 (좌패널)
2. React state 업데이트
3. API 호출 (/api/artists?filters=...)
4. 응답 받으면 갤럭시 업데이트
   - 숨김 입자: opacity → 0 (0.5초)
   - 표시 입자: opacity → 0.8 (0.5초)
   - 카메라: 새 데이터 범위에 맞춰 자동 조정

필터 유형:
  - segment_id: 장르/지역/세대별
  - career_stage: 경력 단계 (early/mid/late)
  - region: 지역 (Seoul, Busan, etc)
  - min_score, max_score: 점수 범위
  - institution_id: 특정 기관만
  - exhibition_id: 특정 전시 참여자만

성능:
  - 필터 적용: 200ms 이내
  - 갤럭시 업데이트: 0.5초
  - 총 응답시간: 700ms 이내
```

### 2.3 성능 목표 (KPI)

| 지표 | 목표값 | 측정 방식 | Phase 1 | Phase 2 | Phase 3 |
|-----|--------|---------|---------|---------|---------|
| **Frame Rate** | 60 FPS (desktop) | Chrome DevTools | 60 | 60 | 55+ |
| **Initial Load** | < 3초 | Lighthouse | 3.0초 | 2.5초 | 2.0초 |
| **Filter Response** | < 700ms | Custom timer | 600ms | 400ms | 300ms |
| **Interaction Latency** | < 50ms | Input lag | 40ms | 30ms | 20ms |
| **Memory Usage** | < 150MB | Chrome DevTools | 120MB | 140MB | 150MB |
| **Supported Particles** | 100명 | Data size | 100 | 500 | 2,000 |
| **Browser Support** | Chrome, Firefox, Safari (latest 2 versions) | CanIUse | ✅ | ✅ | ✅ |

### 2.4 테스트 기준

```
단위 테스트 (Unit Tests):
  - colorMapping 함수 (R/G/B 계산) → 오류율 0%
  - coordinateTransform (정규화) → 오류율 0%
  - raycastSelection (충돌감지) → 정확도 99%

통합 테스트 (Integration Tests):
  - 갤럭시 로드 → 입자 렌더링 검증
  - 필터 적용 → 입자 수 감소 검증
  - 클릭 이벤트 → 우측 패널 업데이트 검증
  - 카메라 제어 → 마우스 이벤트 응답 검증

E2E 테스트 (End-to-End Tests):
  - 홈화면 로드 → 갤럭시 렌더링 완료
  - 필터 선택 → 갤럭시 업데이트 완료
  - 미술가 선택 → 상세정보 표시
  - API 연결 확인 → 데이터 동기화

성능 테스트 (Performance Tests):
  - 100명 데이터: 60 FPS 유지 (99th percentile)
  - 500명 데이터: 50 FPS 이상
  - 메모리 누수: < 5MB/분

호환성 테스트 (Compatibility Tests):
  - Chrome 최신 2 버전
  - Firefox 최신 2 버전
  - Safari 최신 2 버전
  - Edge 최신 버전
  - 데스크톱/태블릿 해상도
```

### 2.5 인수인계 체크리스트

```
[ ] 갤럭시 렌더링 60 FPS 유지 (desktop)
[ ] 초기 로드 3초 이내
[ ] 마우스 제어 응답성 50ms 이내
[ ] 필터 적용 700ms 이내
[ ] 클릭 탐지 정확도 99%
[ ] 메모리 누수 없음 (1시간 연속 사용)
[ ] 모든 브라우저에서 렌더링 일치
[ ] 모바일 버전 30 FPS 이상
[ ] 접근성: 키보드 네비게이션 가능
[ ] 마크다운 문서: 렌더링 로직 완벽 설명
```

---

## 3. Feature 2: 미술가 데이터 관리 (F2)

### 3.1 기능 개요

**목적**: 100명의 미술가 데이터를 Neo4j에 체계적으로 저장하고, 신뢰도 0.85 이상으로 검증된 데이터만 공개.

### 3.2 데이터 수집 & 정규화

#### 3.2.1 데이터 소스 (Primary & Secondary)

```
Primary Sources (1차):
  - ARKO (예술경영지원센터) API
    엔드포인트: https://www.arko.or.kr/api/artists
    빈도: 주 1회 자동 동기화
    신뢰도: 0.95
  
  - 국립현대미술관 데이터
    방식: 웹 크롤링 (robots.txt 준수)
    빈도: 월 1회
    신뢰도: 0.92
  
  - 미술 경매사 (Artsy, LiveArt)
    방식: API (유료) 또는 수동 입력
    빈도: 거래 시마다 (실시간)
    신뢰도: 0.88

Secondary Sources (2차):
  - 개인 웹사이트
    수집: URL 저장 + 메타데이터 추출
    신뢰도: 0.70
  
  - 소셜 미디어 (Instagram)
    수집: 해시태그 기반 검색
    신뢰도: 0.65
  
  - 언론 기사 (아트인사이트, 중앙일보)
    수집: 자동 크롤링 (저작권 준수)
    신뢰도: 0.80
```

#### 3.2.2 데이터 정규화 프로세스

```
Step 1: 데이터 수집 (Collection)
  - 여러 소스에서 병렬 수집
  - 중복 제거 (artist_id 기반)
  - 인코딩 표준화 (UTF-8)
  시간: < 30분

Step 2: 데이터 검증 (Validation)
  - 필수 필드 확인 (name, birth_year 등)
  - 형식 검증 (email, URL 형식)
  - 논리 검증 (birth_year < current_year)
  - 통과율 목표: > 95%
  시간: < 1시간

Step 3: 데이터 정규화 (Normalization)
  - 이름 표준화: Hangul + 영문 병기
    예: "이상훈" → { ko: "이상훈", en: "Sang-Hoon Lee" }
  - 주소 정규화: 도/시/구 표준화
  - 가격 정규화: KRW → USD 환율 적용
  - 날짜 정규화: YYYY-MM-DD 형식
  - 도구: Python + Pandas + fuzzywuzzy
  시간: < 2시간

Step 4: 점수 계산 (Scoring)
  - 제도 점수 (inst_score): ARKO 데이터 기반
    계산식: (museum_count * 20) + (biennale_count * 30) + (support_count * 10)
    범위: 0~100
  
  - 학술 점수 (acad_score): KCI 논문 인용 + 도록 언급
    계산식: (citation_count * 2) + (catalog_count * 5)
    범위: 0~100
  
  - 담론 점수 (media_score): 언론 기사 수 + 감정 분석
    계산식: (article_count * 1) + (sentiment_score * 20)
    범위: 0~100 (음수값은 0으로 절사)
  
  - 네트워크 점수 (network_score): 협력자 수 + 중심성 지수
    계산식: (collaborators * 5) + (centrality * 40)
    범위: 0~100
  
  - 복합 점수 (composite_score): 가중 평균
    계산식: inst*0.3 + acad*0.2 + media*0.25 + network*0.25
    범위: 0~100
  
  - 신뢰도 점수 (confidence_score):
    계산식: (source_credibility * 0.4) + (data_completeness * 0.3) + (verification_level * 0.3)
    범위: 0~1
  시간: < 3시간

Step 5: 검증 (Verification)
  - 상위 20명 수동 검증 (큐레이터)
  - 무작위 50명 샘플 검증 (통계)
  - 이상치 탐지 (신뢰도 < 0.7인 데이터)
  - 통과율 목표: > 0.85
  시간: < 2시간

Step 6: Neo4j 업로드 (Upload)
  - Cypher 스크립트 실행
  - 트랜잭션 롤백 가능성 확보
  - 백업 생성 (업로드 전)
  - 업로드 로그 기록
  시간: < 30분

총 소요 시간: < 9시간 (월 1회)
자동화율: 85% (Step 1~4)
수동 작업: 15% (Step 5)
```

#### 3.2.3 Confidence Score 계산 (상세) - 구조주의 기반

```python
def calculate_confidence_score(artist_data: ArtistData) -> ConfidenceScore:
    """
    구조주의 기반 신뢰도 점수 계산

    이론적 근거:
    - Bourdieu 장 이론에 따른 4개 레이어 구조 분석
    - 메타 분석 기반 데이터 품질 평가

    구성 요소:
    1. 데이터 가용성 (data_availability): 4개 레이어 중 몇 개 존재
    2. 소스 신뢰도 (source_credibility): 데이터 출처 품질
    3. 검증 수준 (verification_level): 수동/자동 검증 여부
    """

    # 가용 레이어 수 (구조주의 4개 자본)
    available_layers = sum([
        1 if artist_data.inst_score is not None else 0,
        1 if artist_data.acad_score is not None else 0,
        1 if artist_data.media_score is not None else 0,
        1 if artist_data.network_score is not None else 0
    ])
    data_availability = available_layers / 4

    # 소스 신뢰도 (기관별 가중치)
    SOURCE_WEIGHTS = {
        'ARKO': 0.95,           # 예술경영지원센터
        'MMCA': 0.92,           # 국립현대미술관
        'auction': 0.88,        # 경매사 데이터
        'KCI': 0.85,            # 한국학술지인용색인
        'web_crawl': 0.70,      # 웹 크롤링
        'sns': 0.65             # SNS 데이터
    }
    source_scores = [SOURCE_WEIGHTS.get(s, 0.5) for s in artist_data.data_sources]
    source_credibility = sum(source_scores) / len(source_scores) if source_scores else 0.5

    # 검증 수준
    verification_level = 1.0 if artist_data.is_verified else 0.5

    # 복합 신뢰도 (가중 합산)
    confidence = (
        data_availability * 0.40 +      # 데이터 가용성 40%
        source_credibility * 0.35 +     # 소스 신뢰도 35%
        verification_level * 0.25       # 검증 수준 25%
    )

    return ConfidenceScore(
        score=round(confidence, 2),
        breakdown={
            'data_availability': data_availability,
            'source_credibility': source_credibility,
            'verification_level': verification_level,
            'available_layers': available_layers,
            'missing_layers': [
                layer for layer in ['inst', 'acad', 'media', 'network']
                if getattr(artist_data, f'{layer}_score') is None
            ]
        },
        minimum_threshold=0.60,         # 60% 이상만 공개
        methodology_version='v1.0_structuralist'
    )

# 예시:
# ARKO + MMCA 데이터 (4레이어 완전) + 검증됨
# → confidence = 1.0*0.4 + 0.935*0.35 + 1.0*0.25 = 0.977 ✅

# 웹 크롤링 데이터 (2레이어만) + 미검증
# → confidence = 0.5*0.4 + 0.70*0.35 + 0.5*0.25 = 0.57 ❌ (임계값 미달)
```

#### 3.2.4 데이터 스키마 (Neo4j)

```cypher
// Artist 노드 생성 쿼리

CREATE (a:Artist {
  artist_id: "artist_001",
  name: "이상훈",
  alternativeName: "Sang-Hoon Lee",
  birth_year: 1975,
  url: "https://example.com/artist",
  segment_id: "monochrome_seoul_1970s",
  career_stage: "mid",
  
  // 점수
  scores: {
    inst_score: 82,
    acad_score: 68,
    media_score: 75,
    network_score: 71,
    composite_score: 74
  },
  
  // 3D 좌표
  coordinates_3d: {
    x: 2.34,
    y: -1.23,
    z: 0.67,
    radius: 15,
    computed_at: "2025-12-08T18:30:00Z"
  },
  
  // 메타데이터
  metadata: {
    created_at: "2025-12-08T18:30:00Z",
    updated_at: "2025-12-08T18:30:00Z",
    data_source: ["ARKO", "KCI"],
    confidence_score: 0.88,
    verified: true,
    verified_by: "curator_001",
    verified_at: "2025-12-08T19:00:00Z"
  }
})
```

#### 3.2.5 데이터 검증 파이프라인 상세 명세 (신규)

**목적**: 데이터 품질을 자동으로 검증하고 이상치를 사전에 차단하는 파이프라인 구축

**파이프라인 단계:**

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: 데이터 수집 (Collection)                       │
│   ├─ 소스별 병렬 수집 (ARKO, MMCA, KCI, 웹 크롤링)     │
│   ├─ 중복 제거 (artist_id 기반 해시 테이블)            │
│   ├─ 인코딩 표준화 (UTF-8 강제)                        │
│   └─ 수집 로그 기록 (소스별 성공/실패 통계)            │
│   시간: < 30분                                          │
│   품질 게이트: 수집 성공률 > 90%                        │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: 데이터 검증 (Validation) - 구조주의 기반        │
│                                                         │
│ 2.1 필수 필드 검증:                                     │
│   - name: 필수, 비어있으면 거부                         │
│   - birth_year: 필수, 범위 [1900, 현재연도]             │
│   - artist_id: 필수, 고유성 검증                        │
│                                                         │
│ 2.2 형식 검증:                                          │
│   - email: RFC 5322 준수                                │
│   - URL: http/https 프로토콜 필수                       │
│   - 날짜: YYYY-MM-DD 형식 강제                          │
│                                                         │
│ 2.3 논리 검증:                                          │
│   - birth_year < current_year                           │
│   - 전시 시작일 < 종료일                                │
│   - 가격 > 0 (거래 데이터)                              │
│                                                         │
│ 2.4 구조주의 레이어 검증:                               │
│   - 4개 자본 레이어 중 최소 2개 존재해야 함             │
│   - 각 점수 범위: 0 ≤ score ≤ 100                       │
│   - composite_score = 가중합 검증 (오차 < 0.01)         │
│                                                         │
│ 2.5 신뢰도 임계값 검증:                                 │
│   - confidence_score ≥ 0.60 (최소 공개 기준)           │
│   - confidence_score ≥ 0.85 (Year 1 목표)              │
│                                                         │
│ 통과율 목표: > 95%                                      │
│ 실패 데이터: 자동 격리 (quarantine) → 수동 검토        │
│ 시간: < 1시간                                           │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: 데이터 정규화 (Normalization)                  │
│   ├─ 이름 표준화: Hangul + 영문 병기                    │
│   ├─ 주소 정규화: 도/시/구 표준화                       │
│   ├─ 가격 정규화: KRW → USD 환율 적용                   │
│   ├─ 날짜 정규화: YYYY-MM-DD 형식                      │
│   └─ 도구: Python + Pandas + fuzzywuzzy                │
│   시간: < 2시간                                          │
│   품질 게이트: 정규화 성공률 > 98%                      │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: 점수 계산 및 구조주의 분석 (Scoring)             │
│                                                         │
│ 4.1 4개 레이어 점수 계산:                               │
│   - inst_score: 제도 레이어 (0-100)                     │
│   - acad_score: 학술 레이어 (0-100)                     │
│   - media_score: 담론 레이어 (0-100)                    │
│   - network_score: 네트워크 레이어 (0-100)              │
│                                                         │
│ 4.2 복합 점수 계산 (가중 평균):                         │
│   composite_score = (inst*0.30 + acad*0.20 +            │
│                      media*0.25 + network*0.25)         │
│                                                         │
│ 4.3 구조주의 분석 계산:                                 │
│   - 자본 구성 비율 (capital_composition)                 │
│   - 지배적 자본 유형 (dominant_capital)                 │
│   - 장 분면 분류 (field_quadrant)                       │
│   - 구조적 등가성 (structural_equivalence)              │
│                                                         │
│ 4.4 신뢰도 점수 계산 (구조주의 기반):                   │
│   confidence_score = (data_availability * 0.40 +         │
│                       source_credibility * 0.35 +       │
│                       verification_level * 0.25)         │
│                                                         │
│ 시간: < 3시간                                            │
│ 품질 게이트: 계산 오류율 < 0.1%                         │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: 품질 검증 (Quality Assurance)                  │
│                                                         │
│ 5.1 자동 검증:                                           │
│   - 상위 20명 작가: 자동 플래그 (수동 검증 필요)         │
│   - 무작위 50명 샘플: 통계적 검증                       │
│   - 이상치 탐지: 신뢰도 < 0.7인 데이터                  │
│   - 점수 일관성 검증: 재계산 시 동일 결과               │
│                                                         │
│ 5.2 수동 검증 (큐레이터):                               │
│   - 상위 20명 작가: 큐레이터 검토                        │
│   - 이상치 데이터: 전문가 판단                          │
│   - 검증 통과율 목표: > 0.85                            │
│                                                         │
│ 5.3 품질 게이트:                                         │
│   - 전체 데이터 신뢰도 평균 ≥ 0.85                      │
│   - 신뢰도 < 0.60인 데이터 비율 < 5%                    │
│   - 필수 필드 채움률 > 95%                              │
│                                                         │
│ 통과율 목표: > 0.85                                      │
│ 시간: < 2시간                                            │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Step 6: Neo4j 업로드 (Upload)                          │
│   ├─ 트랜잭션 롤백 가능성 확보                          │
│   ├─ 백업 생성 (업로드 전)                              │
│   ├─ 배치 업로드 (100개씩)                              │
│   ├─ 업로드 로그 기록                                   │
│   └─ 업로드 후 검증 (쿼리 테스트)                       │
│   시간: < 30분                                           │
│   품질 게이트: 업로드 성공률 100%                       │
└─────────────────────────────────────────────────────────┘
```

**품질 게이트 정의:**

| 게이트 | 임계값 | 실패 시 조치 |
|--------|--------|------------|
| **수집 성공률** | > 90% | 재시도 또는 수동 수집 |
| **검증 통과율** | > 95% | 실패 데이터 격리 및 수동 검토 |
| **정규화 성공률** | > 98% | 정규화 규칙 개선 |
| **계산 오류율** | < 0.1% | 알고리즘 버그 수정 |
| **전체 신뢰도 평균** | ≥ 0.85 | 데이터 소스 추가 또는 검증 강화 |
| **업로드 성공률** | 100% | 롤백 및 재시도 |

**자동화 수준:**

- Step 1-4: 85% 자동화 (Python 스크립트)
- Step 5: 70% 자동화 (30% 수동 검증)
- Step 6: 100% 자동화 (Neo4j 배치 업로드)

**이상치 데이터 처리 절차:**

1. **자동 격리**: 신뢰도 < 0.60인 데이터는 자동으로 quarantine 테이블로 이동
2. **알림**: 이상치 발견 시 큐레이터에게 자동 알림
3. **수동 검토**: 큐레이터가 이상치 데이터 검토 후 승인/거부 결정
4. **재처리**: 승인된 데이터는 정규화 파이프라인 재진입

### 3.3 성능 목표 (KPI)

| 지표 | 목표값 | Phase 1 | Phase 2 | Phase 3 |
|-----|--------|---------|---------|---------|
| **데이터 정확도** | > 0.85 신뢰도 | 0.85 | 0.88 | 0.90 |
| **수집 주기** | 월 1회 | ✅ | ✅ | ✅ |
| **정규화 시간** | < 9시간 | 8시간 | 6시간 | 4시간 |
| **검증 통과율** | > 95% | 95% | 97% | 98% |
| **데이터 커버리지** | 100명 | 100 | 500 | 2,000 |
| **결측치율** | < 5% | 4% | 3% | 2% |
| **중복 제거율** | 99% | 99% | 99.5% | 99.5% |
| **품질 게이트 통과율** | 100% | 100% | 100% | 100% |

### 3.4 테스트 기준

```
단위 테스트:
  [ ] confidenceScore 계산 함수 → 오류율 0%
  [ ] nameNormalization 함수 → 정확도 99%
  [ ] addressNormalization 함수 → 정확도 95%
  [ ] scoringAlgorithm 함수 → 재현성 100%

통합 테스트:
  [ ] 100명 데이터 정규화 완료
  [ ] 신뢰도 0.85 이상 데이터만 필터링
  [ ] Neo4j 업로드 성공 (0 에러)
  [ ] 트랜잭션 롤백 가능 (장애 시)

데이터 품질 테스트:
  [ ] 필수 필드 채움률 > 95%
  [ ] 이상치 탐지 정확도 > 90%
  [ ] 중복 제거 정확도 > 99%
  [ ] 점수 계산 일관성 (재계산 시 동일한 결과)
```

### 3.5 인수인계 체크리스트

```
[ ] 100명 미술가 데이터 수집 완료
[ ] 데이터 정규화 완료 (이름, 주소, 가격 등)
[ ] 신뢰도 점수 계산 완료 (confidence_score > 0.85)
[ ] Neo4j 데이터베이스 초기화 완료
[ ] 관계(relationship) 설정 완료
[ ] 인덱스 생성 완료 (성능 최적화)
[ ] 백업 생성 완료
[ ] 점수 검증 완료 (수동 샘플 검증)
[ ] 문서화 완료 (데이터 출처, 계산식 공개)
[ ] QA 테스트 통과
```

---

## 4. Feature 3: 분석 대시보드 (F3)

### 4.1 기능 개요

**목적**: 사용자가 미술계 구조를 **10가지 이상의 분석 메트릭**으로 심층 이해할 수 있도록 함.

### 4.2 분석 메트릭 (10+)

#### 4.2.1 중심성 분석 (Centrality Analysis)

```
Degree Centrality (차수 중심성):
  정의: 각 작가가 얼마나 많은 다른 작가와 연결되어 있는가
  계산: 협력자 수 / (전체 작가 수 - 1)
  범위: 0 ~ 1
  목표: top 10 작가 식별
  응답시간: < 1초
  
Betweenness Centrality (매개 중심성):
  정의: 각 작가가 다른 작가들 사이의 경로에 얼마나 자주 등장하는가
  계산: 작가를 경유하는 최단경로 수 / 전체 최단경로 수
  범위: 0 ~ 1
  목표: 영향력 있는 중개자 식별
  응답시간: < 3초 (Floyd-Warshall 알고리즘)
  
Eigenvector Centrality (고유벡터 중심성):
  정의: 영향력 있는 작가와 연결된 작가의 영향력
  계산: 인접 행렬의 고유벡터
  범위: 0 ~ 1
  목표: 권력 있는 네트워크 식별
  응답시간: < 2초 (power iteration)

Closeness Centrality (근접 중심성):
  정의: 각 작가가 다른 모든 작가에게 얼마나 가까운가
  계산: (n-1) / 모든 최단경로 합
  범위: 0 ~ 1
  목표: 네트워크 허브 식별
  응답시간: < 2초
```

**API 엔드포인트**:
```
POST /api/analysis/centrality
  요청:
    {
      "measure": "degree" | "betweenness" | "eigenvector" | "closeness",
      "limit": 20,
      "segment_id": "optional"
    }
  응답:
    {
      "measure": "degree",
      "results": [
        {
          "rank": 1,
          "artist_id": "artist_001",
          "name": "이상훈",
          "score": 0.92,
          "interpretation": "매우 높은 협력 네트워크"
        },
        ...
      ],
      "computation_time_ms": 450
    }
```

#### 4.2.2 커뮤니티 탐지 (Community Detection)

```
Louvain Algorithm:
  정의: 그래프의 자연스러운 커뮤니티(군집) 자동 탐지
  계산: 모듈성(modularity) 최대화
  결과: 7~12개 커뮤니티 (일반적)
  범위: modularity = 0 ~ 1
  목표: 자연스러운 미술 그룹 식별
  응답시간: < 5초 (100명 데이터)
  
출력:
  - 각 커뮤니티의 작가 목록
  - 커뮤니티별 특성 (주요 기관, 장르, 지역)
  - 커뮤니티 간 연결성 (edge_between_communities)
  - 커뮤니티 크기 및 응집력
```

**API 엔드포인트**:
```
POST /api/analysis/community-detection
  요청: {}
  응답:
    {
      "algorithm": "Louvain v1.0",
      "modularity": 0.62,
      "num_communities": 9,
      "communities": [
        {
          "id": "cluster_001",
          "size": 15,
          "cohesion": 0.78,
          "name": "흑백화-서울 1970년대",
          "members": ["artist_001", "artist_002", ...],
          "dominant_institution": "서울대 미술대",
          "primary_genre": "monochrome_painting"
        },
        ...
      ],
      "computation_time_ms": 2340
    }
```

#### 4.2.3 네트워크 밀도 (Network Density)

```
정의: 전체 가능한 연결 중 실제 연결의 비율
계산: 실제 연결 수 / (n * (n-1) / 2)
범위: 0 ~ 1
  0: 완전히 단절된 네트워크
  1: 완벽히 연결된 네트워크
  
목표 해석:
  < 0.2: 느슨한 네트워크 (다양한 하위 커뮤니티)
  0.2~0.4: 중간 밀도 (자연스러운 구조)
  > 0.4: 높은 밀도 (강력한 상호작용)

응답시간: < 100ms
```

#### 4.2.4 군집 계수 (Clustering Coefficient)

```
정의: 각 작가의 협력자들이 서로 얼마나 연결되어 있는가
계산: 실제 삼각형 수 / 가능한 삼각형 수
범위: 0 ~ 1

해석:
  높음 (> 0.6): 닫힌 그룹 (트라이앵글 많음)
  낮음 (< 0.3): 열린 네트워크 (새로운 연결 용이)

응답시간: < 200ms
```

#### 4.2.5 경로 길이 분포 (Path Length Distribution)

```
정의: 네트워크에서 두 작가 사이의 평균 거리
계산: 모든 쌍의 최단경로 합 / (n * (n-1) / 2)
범위: 1 ~ n

해석:
  Short (< 3): 긴밀하게 연결된 네트워크
  Medium (3~5): 중간 정도 연결
  Long (> 5): 느슨하게 연결된 네트워크

목표: < 3.5 (한국 미술계 특성상)

응답시간: < 2초
```

#### 4.2.6 이상치 점수 분포 (Outlier Score Distribution)

```
정의: 각 작가가 얼마나 "이상한" 패턴을 보이는가
계산: Z-score 기반 이상치 탐지
범위: -3 ~ 3

해석:
  > 2.5: 매우 이상함 (관심 대상)
  1.5~2.5: 약간 이상함
  -1.5~1.5: 정상
  < -1.5: 반대방향 이상 (예: 과소평가됨)

목표: 이상치 < 5% (정상 분포)

응답시간: < 1초
```

#### 4.2.7 기관별 영향력 (Institution Dominance)

```
정의: 각 기관이 미술계 전체에 미치는 영향력
계산: 
  영향력 = (소속_작가_수 * 0.4) + 
           (작가들의_avg_composite_score * 0.3) + 
           (연결된_다른_기관_수 * 0.2) + 
           (전시_개최_횟수 * 0.1)
범위: 0 ~ 100

상위 5 기관 식별
응답시간: < 500ms
```

#### 4.2.8 세대별 분포 (Generational Distribution)

```
정의: 각 세대(출생년대)별 미술가 수 및 영향력
카테고리:
  - 1950s: 고령 (72+)
  - 1960s: 고령 (62-72)
  - 1970s: 중년 (51-62)
  - 1980s: 중년 (41-51)
  - 1990s: 청년 (31-41)
  - 2000s: 신진 (21-31)

분석:
  - 각 세대별 작가 수
  - 세대별 평균 composite_score
  - 세대별 권력 분포 (%)

시각화: 스택 바 차트, 파이 차트
응답시간: < 200ms
```

#### 4.2.9 지역별 분포 (Geographic Distribution)

```
정의: 각 지역(도시)별 미술가 분포
지역:
  - Seoul: 서울
  - Busan: 부산
  - Daegu: 대구
  - Incheon: 인천
  - Daejeon: 대전
  - Gwangju: 광주
  - Ulsan: 울산
  - International: 국제

분석:
  - 각 지역별 작가 수 (%)
  - 지역별 평균 점수
  - 지역 간 네트워크 (크로스 지역 협력)

시각화: 지도 (지역별 색상), 라디얼 차트
응답시간: < 300ms
```

#### 4.2.10 점수 상관관계 (Score Correlation)

```
정의: 4가지 점수(제도, 학술, 담론, 네트워크) 간의 상관관계
계산: Pearson Correlation Coefficient
범위: -1 ~ 1

예상 결과:
  inst_score ↔ acad_score: 중간 양의 상관 (r ≈ 0.6)
  inst_score ↔ media_score: 약한 양의 상관 (r ≈ 0.3)
  network_score ↔ composite_score: 강한 양의 상관 (r ≈ 0.8)

시각화: 히트맵, 산점도
응답시간: < 500ms
```

#### 4.2.11 시간 추이 분석 (Temporal Trend)

```
정의: 시간에 따른 미술계 구조 변화
분석 기간: 2015~2025 (10년)
측정:
  - 연도별 신규 미술가 수
  - 연도별 전시 개최 수
  - 연도별 거래 규모 (KRW)
  - 연도별 네트워크 성장률

목표: 미술시장 성장 트렌드 파악
응답시간: < 800ms
```

#### 4.2.12 구조적 등가성 (Structural Equivalence) - 구조주의 신규

```
정의: 두 미술가가 동일한 관계 패턴을 가지는 정도
이론적 근거: Bourdieu - 같은 구조적 위치는 유사한 habitus 공유
계산: 인접 행렬의 상관계수 (Euclidean Distance)

공식:
  distance = √[(inst₁-inst₂)² + (acad₁-acad₂)² + (media₁-media₂)² + (network₁-network₂)²]
  equivalence = 1 - (distance / max_distance)

범위: 0 ~ 1
해석:
  > 0.8: 높은 등가성 (대체 가능한 위치)
  0.5~0.8: 중간 등가성
  < 0.5: 낮은 등가성 (차별화된 위치)

API: GET /api/artists/{id}/structural-equivalents?limit=10
응답시간: < 3초 (100명 기준)

성능 최적화 전략:
1. 근사 알고리즘 적용 (확장성 고려)
   - 정확한 O(n²) 계산 대신 Locality-Sensitive Hashing (LSH) 사용
   - 100명: 정확 계산 (O(n²) = 10,000 연산, < 3초)
   - 500명: LSH 근사 (O(n log n) = 2,700 연산, < 5초)
   - 2000명: LSH 근사 (O(n log n) = 22,000 연산, < 10초)
   
2. 배치 처리 전략
   - 모든 작가 쌍 계산을 주기적 배치 작업으로 실행 (주 1회)
   - 결과를 Neo4j에 캐시 저장 (structural_equivalents_count 필드)
   - 실시간 요청 시 캐시된 결과 반환 (응답시간 < 100ms)
   
3. 결과 캐싱
   - Redis 캐싱: TTL 24시간
   - Neo4j 필드 캐싱: structural_equivalents_count (영구 저장)
   - 캐시 무효화: 새로운 작가 추가 또는 점수 업데이트 시
```

#### 4.2.13 자본 구성 분석 (Capital Composition) - 구조주의 신규

```
정의: 개별 미술가의 4개 자본 비율 및 지배적 자본 유형
이론적 근거: Bourdieu - 자본 총량 + 자본 구성이 장 내 위치 결정

출력:
  - institutional_ratio: 제도 자본 비율 (0~1)
  - academic_ratio: 학술 자본 비율 (0~1)
  - media_ratio: 담론 자본 비율 (0~1)
  - network_ratio: 네트워크 자본 비율 (0~1)
  - dominant_capital: 지배적 자본 유형
  - capital_total: 자본 총량 (0~400)

해석:
  dominant_capital = "institutional": 제도적 인정 중심 작가
  dominant_capital = "academic": 학술적 정전화 중심 작가
  dominant_capital = "media": 미디어 가시성 중심 작가
  dominant_capital = "network": 사회적 연결 중심 작가

API: GET /api/artists/{id}/capital-composition
응답시간: < 100ms

성능 최적화 전략:
1. 사전 계산 및 저장
   - 점수 계산 시 자본 구성 비율도 함께 계산하여 Neo4j에 저장
   - structuralist_analysis.capital_composition 필드에 영구 저장
   - 실시간 계산 불필요 (이미 저장된 값 반환)
   
2. 인덱스 활용
   - dominant_capital 필드에 인덱스 생성 (필터링 성능 향상)
   - capital_composition 필드에 복합 인덱스 (쿼리 최적화)
   
3. 캐싱 전략
   - Redis 캐싱: TTL 1시간 (점수 업데이트 빈도 낮음)
   - Neo4j 필드 캐싱: 영구 저장 (기본 전략)
```

#### 4.2.14 장(Field) 사분면 분석 - 구조주의 신규

```
정의: Bourdieu의 장 이론에 따른 문화자본 vs 사회자본 2차원 배치
계산:
  cultural_axis = (inst_score + acad_score) / 2
  social_axis = (media_score + network_score) / 2

사분면:
  Q1 (high_cultural + high_social): 완전 확립형
  Q2 (high_cultural + low_social): 학술 엘리트형
  Q3 (low_cultural + high_social): 미디어 스타형
  Q4 (low_cultural + low_social): 신진/주변부형

API: GET /api/analysis/field-quadrants
응답시간: < 500ms

성능 최적화 전략:
1. 사전 계산 및 저장
   - 점수 계산 시 장 분면도 함께 계산하여 Neo4j에 저장
   - structuralist_analysis.structural_position.field_quadrant 필드에 영구 저장
   - 중앙값 계산은 주기적 배치 작업으로 실행 (주 1회)
   
2. 집계 쿼리 최적화
   - 분면별 통계는 Neo4j 집계 쿼리로 계산 (인덱스 활용)
   - GalaxySnapshot에 분면별 통계 캐시 저장
   - 실시간 요청 시 스냅샷 데이터 반환 (응답시간 < 100ms)
   
3. 캐싱 전략
   - Redis 캐싱: TTL 1시간 (분면 분류는 자주 변경되지 않음)
   - Neo4j 필드 캐싱: 영구 저장 (기본 전략)
   - GalaxySnapshot 캐싱: 주 1회 업데이트
```

### 4.3 성능 목표 (KPI)

| 메트릭 | 응답시간 | 정확도 | 캐싱 | 업데이트 주기 |
|--------|---------|--------|------|-------------|
| **Centrality** | < 1초 | 100% | 1시간 | 주 1회 |
| **Community Detection** | < 5초 | 95% | 1시간 | 주 1회 |
| **Network Density** | < 100ms | 100% | 1시간 | 주 1회 |
| **Clustering Coeff** | < 200ms | 100% | 1시간 | 주 1회 |
| **Path Length** | < 2초 | 99% | 1시간 | 주 1회 |
| **Institution Dominance** | < 500ms | 95% | 1시간 | 월 1회 |
| **Generational Dist** | < 200ms | 100% | 1시간 | 월 1회 |
| **Geographic Dist** | < 300ms | 100% | 1시간 | 월 1회 |
| **Score Correlation** | < 500ms | 100% | 1시간 | 주 1회 |
| **Temporal Trend** | < 800ms | 90% | 24시간 | 월 1회 |

### 4.4 UI 컴포넌트 (프론트엔드)

```
분석 대시보드 (Analysis.tsx)

레이아웃:
┌─────────────────────────────────────────┐
│  분석 대시보드 (상단 헤더)              │
├─────────────────────────────────────────┤
│ 메트릭 선택 (탭):                      │
│ [중심성] [커뮤니티] [밀도] [기관] ...  │
├─────────────────────────────────────────┤
│                                        │
│  [메인 차트 영역]                      │
│  (선택된 메트릭의 상세 시각화)         │
│                                        │
│                                        │
├─────────────────────────────────────────┤
│  [세부 통계 (하단)]                   │
│  - Top 10 목록                         │
│  - 수치 요약                          │
└─────────────────────────────────────────┘

차트 라이브러리:
  - D3.js (복잡한 상호작용형 차트)
  - Chart.js (간단한 막대/라인 차트)
  - Plotly (3D 산점도)

상호작용:
  - 마우스 오버: 데이터 값 표시
  - 클릭: 세부 정보 모달
  - 다운로드: CSV/PNG 내보내기
```

### 4.5 테스트 기준

```
단위 테스트:
  [ ] 중심성 계산 (Degree, Betweenness, Eigenvector)
  [ ] 커뮤니티 탐지 (Louvain 결과 검증)
  [ ] 상관관계 계산
  [ ] 분포 분석

통합 테스트:
  [ ] 분석 요청 → 결과 반환 (< 응답시간)
  [ ] 캐시 히트 (응답시간 < 100ms)
  [ ] 캐시 미스 (응답시간 < 목표값)
  [ ] 차트 렌더링 (문제 없음)

성능 테스트:
  [ ] 100명 데이터: 모든 분석 < 목표시간
  [ ] 500명 데이터: 성능 저하 < 20%
  [ ] 동시 요청 10개: 큐잉 정상 작동
```

---

## 5. Feature 4: 이상치 탐지 (F4)

### 5.1 기능 개요

**목적**: 미술 시장의 **비정상적인 가격 거래**를 자동으로 탐지하고, **LLM으로 가설 생성**하여 사용자에게 제시.

### 5.2 이상치 탐지 알고리즘

#### 5.2.1 Isolation Forest 기반 탐지

```
알고리즘: Isolation Forest
라이브러리: scikit-learn
목표: Transaction.market_analysis.anomaly_score 계산

특징 벡터 (Feature Vector):
  1. transaction_price: 거래 가격 (KRW)
  2. artist_composite_score: 작가 종합 점수 (0~100)
  3. market_percentile: 같은 세그먼트의 백분위 (0~100)
  4. days_since_last_sale: 마지막 판매로부터의 일수
  5. price_trend: 최근 3년 가격 추이 (%)
  6. seasonal_factor: 계절 보정값
  7. gallery_prestige: 거래 갤러리 위상 점수

이상치 점수:
  anomaly_score = isolation_path_length 정규화값
  범위: 0 ~ 1 (1에 가까울수록 이상)
  임계값: 0.7 (> 0.7 = 이상치)

결과:
  - anomaly_score > 0.7: 강한 이상치 (매우 이상함)
  - anomaly_score 0.6~0.7: 약한 이상치 (약간 이상함)
  - anomaly_score < 0.6: 정상 (일반적)

응답시간: < 1초 (100명 데이터)
정확도: 80% (전문가 검증 기준)
```

#### 5.2.2 Z-Score 기반 이상치 탐지

```
공식: z_score = (x - mean) / std_dev
범위: -3 ~ 3

이상치 판정:
  |z_score| > 2.5: 매우 이상함 (확률 1.2%)
  |z_score| > 2.0: 이상함 (확률 4.6%)
  |z_score| > 1.5: 약간 이상함 (확률 13.4%)

세그먼트별 계산:
  - 같은 작가 세그먼트 내에서만 z_score 계산
  - 예: "흑백화-서울-1970년대" 세그먼트 내 작가들과만 비교

응답시간: < 500ms
```

#### 5.2.3 시계열 기반 이상치 탐지

```
알고리즘: ARIMA (AutoRegressive Integrated Moving Average)
목표: 작가 개인의 거래 가격 추이에서 이상치 탐지

필요 데이터: 최소 10개 거래 이력
계산:
  1. 과거 거래 가격 시계열
  2. ARIMA 모델 학습 (p,d,q 자동 선택)
  3. 다음 가격 예측
  4. 실제 거래 가격과 예측값 비교
  5. 잔차(residual)가 큰 경우 = 이상치

예시:
  과거 거래: [100M, 120M, 110M, 125M, 130M, ...]
  예측값: 135M
  실제 거래: 200M
  편차: +65M (±50% 이상) = 이상치

응답시간: < 2초 (개인별)
```

### 5.3 LLM 기반 가설 생성

#### 5.3.1 가설 생성 프롬프트

```python
# 이상치 탐지 후 LLM 호출

def generate_anomaly_hypothesis(transaction: Transaction, context: Context) -> List[Hypothesis]:
    """
    이상치 거래를 분석하여 가능한 가설 생성
    """
    
    prompt = f"""
    당신은 한국 미술시장 분석가다.
    
    다음 거래 이상치를 분석하고, 가능한 가설 5개를 생성하라:
    
    거래 정보:
    - 작가: {transaction.artist.name}
    - 작품: {transaction.artwork.title}
    - 거래가: {transaction.price.final_price_with_premium:,.0f} KRW
    - 예상가: {transaction.price.estimate_high:,.0f} KRW (예상 범위 상한)
    - 편차: {((transaction.price.final_price_with_premium - transaction.price.estimate_high) / transaction.price.estimate_high * 100):.1f}%
    - 거래 유형: {transaction.transaction_type}
    - 거래처: {transaction.venue}
    
    작가 배경:
    - 복합 점수: {transaction.artist.scores.composite_score:.1f}/100
    - 제도 점수: {transaction.artist.scores.inst_score:.1f}/100
    - 학술 점수: {transaction.artist.scores.acad_score:.1f}/100
    - 담론 점수: {transaction.artist.scores.media_score:.1f}/100
    - 네트워크 점수: {transaction.artist.scores.network_score:.1f}/100
    - 소속 기관: {', '.join([inst.name for inst in transaction.artist.affiliated_institutions])}
    - 최근 전시: {', '.join([exh.title for exh in transaction.artist.recent_exhibitions[:3]])}
    
    시장 맥락:
    - 같은 세그먼트의 평균 가격: {context.segment_avg_price:,.0f} KRW
    - 같은 세그먼트의 표준편차: {context.segment_std:.1f}%
    - 최근 미술시장 트렌드: {context.market_trend}
    - 거래처 위상: {transaction.venue_prestige}/10
    
    가설 형식:
    각 가설은 다음과 같아야 한다:
    1. 가설 제목 (20자 이내)
    2. 가설 설명 (50자 이내)
    3. 신뢰도 (0~100%)
    4. 근거 (구체적 이유)
    
    예시:
    가설 1: "후원자의 재정 유동성"
    설명: "수집가가 긴급 자금 조달을 위해 고가로 낙찰"
    신뢰도: 45%
    근거: "시장 예상치의 +65%는 일반적인 수준 초과. 경매 열정과 후원자의 목적-구입 패턴"
    
    [JSON 형식 응답]:
    {
      "hypotheses": [
        {
          "title": "...",
          "description": "...",
          "confidence": 45,
          "reasoning": "..."
        },
        ...
      ]
    }
    """
    
    response = llm.generate(prompt, model="claude-3.5-sonnet")
    return json.loads(response)
```

#### 5.3.2 가설 신뢰도 보정

```
LLM 생성 가설에 대해 다음과 같이 신뢰도 보정:

1. 기본 LLM 신뢰도: X%
2. 맥락 기반 보정:
   - 장르별 가격 변동성 고려
   - 거래처 신뢰도 고려 (경매사 vs 갤러리)
   - 작가 세그먼트 내 평균 가격 변동성
3. 최종 신뢰도 = X% × 맥락_계수 (0.5~1.5)

예시:
  LLM이 "후원자 재정 유동성"에 45% 신뢰도 제시
  장르별 변동성 높음 (monochrome painting = 원래 변동성 큼)
  → 맥락_계수 = 0.8
  → 최종 신뢰도 = 45% × 0.8 = 36%
```

### 5.4 성능 목표 (KPI)

| 지표 | 목표값 | 측정 방식 | Phase 1 | Phase 2 |
|-----|--------|---------|---------|---------|
| **탐지 정확도** | 80% | 전문가 검증 | 75% | 85% |
| **이상치 응답시간** | < 2초 | Custom timer | 1.8초 | 1.2초 |
| **이상치 탐지율** | 95% | 회상율 (Recall) | 90% | 98% |
| **거짓양성율** | < 10% | 정밀도 (Precision) | 15% | 8% |
| **가설 생성 시간** | < 3초 | LLM 응답시간 | 2.5초 | 1.5초 |
| **가설 관련성** | > 80% | 사용자 피드백 | 70% | 85% |

### 5.5 API 엔드포인트

```
GET /api/anomalies
  설명: 모든 이상치 거래 조회
  쿼리 파라미터:
    - segment_id: STRING (필터)
    - confidence: FLOAT (0.7 기본값, 임계값)
    - limit: INT (20 기본값)
  응답:
    200: {
      "anomalies": [
        {
          "transaction_id": "trans_001",
          "artist_id": "artist_001",
          "artist_name": "이상훈",
          "artwork_title": "무제 (1990)",
          "price_krw": 250000000,
          "estimate_high_krw": 150000000,
          "deviation_percent": 66.7,
          "anomaly_score": 0.78,
          "anomaly_type": "overvalued",
          "hypotheses": [
            {
              "title": "후원자 재정 유동성",
              "description": "수집가가 긴급 자금 조달을 위해...",
              "confidence": 36,
              "reasoning": "..."
            },
            ...
          ],
          "computation_time_ms": 1250
        },
        ...
      ],
      "total_anomalies": 5
    }

POST /api/anomalies/analyze
  설명: 특정 거래의 이상치 재분석
  요청:
    { "transaction_id": "trans_001" }
  응답:
    200: { anomalies 상세 정보 }
```

### 5.6 테스트 기준

```
단위 테스트:
  [ ] Isolation Forest 학습 및 예측
  [ ] Z-Score 계산
  [ ] ARIMA 모델 학습
  [ ] LLM 가설 생성 (프롬프트 검증)

통합 테스트:
  [ ] 거래 데이터 입력 → 이상치 점수 계산
  [ ] 이상치 점수 → LLM 가설 생성
  [ ] 가설 신뢰도 보정
  [ ] 최종 결과 JSON 응답

정확도 테스트:
  [ ] 50개 샘플 거래에 대해 전문가와 비교
  [ ] 정확도 > 75%
  [ ] 거짓양성 < 15%
  [ ] 거짓음성 < 10%
```

---

## 6. Feature 5: 공개 API & 데이터 (F5)

### 6.7 예외 상황 처리 전략 (신규)

#### 6.7.1 API 에러 처리

**에러 응답 형식 (표준화):**

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 친화적 에러 메시지",
    "details": "상세 기술 정보 (개발자용)",
    "timestamp": "2025-12-08T18:30:00Z",
    "request_id": "req_123456789",
    "documentation": "https://api.argo.art/docs/errors/ERROR_CODE"
  }
}
```

**HTTP 상태 코드 매핑:**

| 상황 | HTTP 코드 | 에러 코드 | 설명 |
|------|----------|----------|------|
| 잘못된 요청 | 400 | `INVALID_PARAMETER` | 필수 파라미터 누락 또는 형식 오류 |
| 인증 실패 | 401 | `UNAUTHORIZED` | API 키 없음 또는 만료 |
| 권한 없음 | 403 | `FORBIDDEN` | 접근 권한 없음 |
| 리소스 없음 | 404 | `NOT_FOUND` | 요청한 리소스 없음 |
| 레이트 제한 | 429 | `RATE_LIMIT_EXCEEDED` | 요청 한도 초과 |
| 서버 오류 | 500 | `INTERNAL_ERROR` | 내부 서버 오류 |
| 서비스 불가 | 503 | `SERVICE_UNAVAILABLE` | 일시적 서비스 중단 |

**예외 케이스별 처리:**

```
1. Neo4j 연결 실패
   ├─ 재시도: 3회 (지수 백오프: 1초, 2초, 4초)
   ├─ Circuit Breaker: 연속 5회 실패 시 30초 차단
   ├─ 폴백: 캐시된 데이터 반환 (TTL: 1시간)
   └─ 알림: DevOps 팀에 즉시 알림

2. 쿼리 타임아웃 (> 5초)
   ├─ 쿼리 취소 및 타임아웃 에러 반환
   ├─ 로그 기록 (쿼리 성능 분석용)
   └─ 사용자에게 "일시적 지연" 메시지 표시

3. 데이터 불일치 감지
   ├─ 자동 감지: 스키마 버전 불일치, 필수 필드 누락
   ├─ 자동 복구: 기본값 적용 또는 캐시 데이터 사용
   └─ 알림: 데이터 팀에 불일치 리포트 전송

4. LLM API 실패 (이상치 가설 생성)
   ├─ 재시도: 2회 (지수 백오프)
   ├─ 폴백: 템플릿 기반 가설 생성 (신뢰도 낮음)
   └─ 로그: LLM 실패 원인 기록

5. 메모리 부족 (대용량 쿼리)
   ├─ 쿼리 분할: 배치 처리로 나눔
   ├─ 페이지네이션 강제: limit 파라미터 필수
   └─ 에러: "요청이 너무 큽니다. 페이지네이션 사용" 반환
```

#### 6.7.2 Circuit Breaker 패턴

**구현 전략:**

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def execute_neo4j_query(query: str, params: dict):
    """
    Neo4j 쿼리 실행 (Circuit Breaker 적용)
    
    - 연속 5회 실패 시 30초간 차단
    - 차단 중에는 캐시된 데이터 반환
    """
    try:
        result = neo4j_driver.execute_query(query, params)
        return result
    except Exception as e:
        logger.error(f"Neo4j query failed: {e}")
        raise
```

**Circuit Breaker 상태:**

- **Closed (정상)**: 모든 요청 통과
- **Open (차단)**: 모든 요청 차단, 캐시 반환
- **Half-Open (테스트)**: 일부 요청 허용하여 복구 테스트

#### 6.7.3 데이터 불일치 감지 및 자동 복구

**불일치 감지 규칙:**

```
1. 스키마 버전 불일치
   - 감지: API 버전과 DB 스키마 버전 비교
   - 복구: 마이그레이션 스크립트 자동 실행

2. 필수 필드 누락
   - 감지: 스키마 정의와 실제 데이터 비교
   - 복구: 기본값 적용 또는 NULL 허용

3. 관계 무결성 위반
   - 감지: 참조된 노드가 존재하지 않음
   - 복구: 고아 관계 제거 또는 경고 로그

4. 점수 계산 불일치
   - 감지: composite_score ≠ 가중합 검증
   - 복구: 자동 재계산 및 업데이트
```

**자동 복구 프로세스:**

```
Step 1: 불일치 감지 (주기적 스캔, 주 1회)
Step 2: 심각도 평가 (Critical/High/Medium/Low)
Step 3: 자동 복구 시도 (Medium 이하)
Step 4: 수동 검토 필요 알림 (Critical/High)
Step 5: 복구 결과 로그 기록
```

---

## 6. Feature 5: 공개 API & 데이터 (F5)

### 6.1 기능 개요

**목적**: 모든 ARGO 데이터를 **공개 API로 제공**하여 학술 신뢰도 증진 및 생태계 구축.

### 6.2 API 설계 원칙

```
1. RESTful 설계
   - 자원 기반 설계 (/api/artists, /api/institutions)
   - HTTP 메서드 준수 (GET, POST, PUT, DELETE)
   - 상태코드 정확 (200, 201, 400, 404, 500)

2. JSON-LD 표준
   - Schema.org 맵핑
   - @context 명시
   - @id 식별자 포함

3. 투명성
   - 모든 데이터 출처 명시
   - 계산 로직 공개 (문서)
   - Cypher 쿼리 공개 (복잡한 분석)

4. 확장성
   - 버전 관리 (v1, v2, ...)
   - GraphQL 옵션 (향후)
   - Webhook 지원 (향후)

5. 보안
   - API 키 인증
   - Rate Limiting (월 500만 요청)
   - CORS 설정
   - 데이터 암호화 (HTTPS)
```

### 6.3 공개 API 엔드포인트 (20+)

#### 6.3.1 작가 API (6개)

```
1. GET /api/artists
   [이미 정의됨]

2. GET /api/artists/{artist_id}
   [이미 정의됨]

3. GET /api/artists/{artist_id}/network
   [이미 정의됨]

4. GET /api/artists/{artist_id}/exhibitions
   설명: 특정 작가가 참여한 전시 목록
   응답:
     200: {
       "exhibitions": [
         {
           "exh_id": "exh_001",
           "title": "한국 추상미술의 맥락",
           "organizer_id": "inst_001",
           "organizer_name": "국립현대미술관",
           "start_date": "2024-03-15",
           "end_date": "2024-06-30",
           "participated_role": "artist",
           "artworks_count": 3
         }
       ]
     }

5. GET /api/artists/{artist_id}/artworks
   설명: 특정 작가의 작품 목록
   응답:
     200: {
       "artworks": [
         {
           "work_id": "work_001",
           "title": "무제 (1990)",
           "creation_year": 1990,
           "medium": "acrylic on canvas",
           "dimensions": { "height_cm": 200, "width_cm": 150 },
           "estimated_value_usd": 45000
         }
       ]
     }

6. GET /api/artists/{artist_id}/market
   설명: 작가의 시장 정보 (거래 이력, 가격 추이)
   응답:
     200: {
       "transactions": [ ... ],
       "price_history": {
         "2022": 35000,
         "2023": 40000,
         "2024": 45000
       },
       "market_percentile": 72,
       "price_trend_percent": 12.5
     }
```

#### 6.3.2 기관 API (4개)

```
7. GET /api/institutions
   [이미 정의됨]

8. GET /api/institutions/{inst_id}
   [이미 정의됨]

9. GET /api/institutions/{inst_id}/affiliated-artists
   설명: 기관 소속 미술가 목록
   응답:
     200: {
       "affiliated_artists": [
         {
           "artist_id": "artist_001",
           "name": "이상훈",
           "role": "professor",
           "tenure_start_year": 2015,
           "tenure_end_year": null,
           "is_current": true
         }
       ]
     }

10. GET /api/institutions/{inst_id}/exhibitions
    설명: 기관이 개최한 전시 목록
    응답:
      200: {
        "exhibitions": [ ... ]
      }
```

#### 6.3.3 전시 API (2개)

```
11. GET /api/exhibitions
    설명: 모든 전시 조회
    쿼리 파라미터:
      - organizer_id: STRING (필터)
      - start_year: INT (필터)
      - end_year: INT (필터)
    응답:
      200: { "exhibitions": [...], "total": INT }

12. GET /api/exhibitions/{exh_id}
    설명: 전시 상세 정보
    응답:
      200: {
        "exhibition": { ... },
        "participating_artists": [ ... ],
        "featured_artworks": [ ... ]
      }
```

#### 6.3.4 거래 API (3개)

```
13. GET /api/transactions
    설명: 모든 거래 조회
    쿼리 파라미터:
      - artist_id: STRING (필터)
      - transaction_type: ENUM (필터)
      - start_date: DATE (필터)
      - end_date: DATE (필터)
    응답:
      200: { "transactions": [...], "total": INT }

14. GET /api/transactions/{trans_id}
    설명: 거래 상세 정보
    응답:
      200: { "transaction": { ... } }

15. GET /api/transactions/price-history/{artist_id}
    설명: 작가의 거래 가격 히스토리
    응답:
      200: {
        "artist_id": "artist_001",
        "price_history": [
          { "date": "2022-05-15", "price_krw": 35000000 },
          { "date": "2023-11-20", "price_krw": 40000000 },
          { "date": "2024-03-10", "price_krw": 45000000 }
        ]
      }
```

#### 6.3.5 분석 API (4개)

```
16. POST /api/analysis/centrality
    [이미 정의됨]

17. POST /api/analysis/community-detection
    [이미 정의됨]

18. GET /api/analysis/correlation
    설명: 4가지 점수 간의 상관관계
    응답:
      200: {
        "correlation_matrix": [
          [1.0, 0.6, 0.3, 0.8],
          [0.6, 1.0, 0.4, 0.5],
          ...
        ],
        "interpretation": {
          "inst_acad": "중간 양의 상관",
          "inst_media": "약한 양의 상관",
          ...
        }
      }

19. POST /api/analysis/compare
    설명: 2명 이상의 작가 비교
    요청:
      {
        "artist_ids": ["artist_001", "artist_002", "artist_003"],
        "metrics": ["composite_score", "inst_score", "network_score"]
      }
    응답:
      200: {
        "comparison": [
          {
            "artist_id": "artist_001",
            "metrics": { "composite_score": 74, "inst_score": 82, ... }
          },
          ...
        ]
      }
```

#### 6.3.6 검색 API (1개)

```
20. GET /api/search
    [이미 정의됨]
```

#### 6.3.7 메타데이터 API (2개)

```
21. GET /api/galaxy-snapshot
    설명: 현재 갤럭시 스냅샷 (통계, 구조 메트릭)
    응답:
      200: {
        "snapshot_id": "snapshot_20251208",
        "snapshot_date": "2025-12-08",
        "galaxy_statistics": {
          "total_artists": 100,
          "total_institutions": 25,
          "total_exhibitions": 180,
          "total_artworks": 450,
          "total_transactions": 1200,
          "total_clusters": 9
        },
        "structure_metrics": {
          "entropy": 0.72,
          "density": 0.18,
          "clustering_coefficient": 0.62,
          "average_path_length": 3.2,
          "diameter": 6
        },
        "computation_time_ms": 1500
      }

22. GET /api/metadata/sources
    설명: 모든 데이터 출처 및 신뢰도
    응답:
      200: {
        "data_sources": [
          {
            "source_id": "source_arko",
            "name": "ARKO",
            "url": "https://arko.or.kr",
            "last_sync": "2025-12-07T18:30:00Z",
            "credibility_score": 0.95,
            "records_count": 2500,
            "coverage": "생존 미술가 전수"
          },
          ...
        ]
      }
```

### 6.4 API 레이트 제한 & 인증

```
API 키 관리:
  - 무료 계층: 월 10,000 요청 (1000/일)
  - 프리미엄 계층: 월 500,000 요청 (16,666/일)
  - 기관 계층: 무제한 (커스텀)

인증 방식:
  - Header: Authorization: Bearer <api_key>
  - 또는 Query: ?api_key=<api_key>

레이트 제한 응답:
  429 Too Many Requests
  {
    "error": "Rate limit exceeded",
    "retry_after_seconds": 3600,
    "limits": {
      "requests_limit": 10000,
      "requests_remaining": 0,
      "reset_time": "2025-12-09T00:00:00Z"
    }
  }
```

### 6.5 성능 목표 (KPI)

| 지표 | 목표값 | Phase 1 | Phase 2 |
|-----|--------|---------|---------|
| **API 응답시간** | < 200ms | 180ms | 150ms |
| **공개 엔드포인트** | 20+ | 15 | 25 |
| **월간 API 요청** | 500만+ | 100만 | 500만 |
| **API 가용성** | 99.9% | 99.5% | 99.95% |
| **데이터 최신성** | < 24시간 | 48시간 | 24시간 |
| **문서 완성도** | 100% | 90% | 100% |

### 6.6 테스트 기준

```
단위 테스트:
  [ ] 모든 엔드포인트 응답 형식 검증
  [ ] JSON-LD 스키마 검증 (Schema.org)
  [ ] 에러 응답 검증 (400, 404, 500)

통합 테스트:
  [ ] 인증 (API 키 검증)
  [ ] 레이트 제한 작동 검증
  [ ] 응답 시간 < 200ms
  [ ] 데이터 일관성 (중복 요청 시 동일 결과)

부하 테스트:
  [ ] 동시 100개 요청 처리
  [ ] 동시 1000개 요청 처리
  [ ] 응답 시간 저하 < 20%
```

---

## 7. 배포 타임라인 & 마일스톤

### 7.1 Phase 1 (Month 1-3): 파일럿 & 학술 검증

| Week | 마일스톤 | 담당팀 | 목표 |
|------|----------|--------|------|
| **W1** | Neo4j Aura 초기화, 스키마 배포 | Backend | ✅ |
| **W2** | 100명 데이터 수집 50% 완료 | Data | 50명 |
| **W3** | Galaxy3D MVP 개발 (50%) | Frontend | 렌더링 완료 |
| **W4** | Artist API 기본 구현 | Backend | /api/artists GET |
| **W5~W6** | 데이터 정규화 완료, 점수 계산 | Data + Backend | confidence > 0.85 |
| **W7** | Galaxy3D 완성, 필터 구현 | Frontend | 60 FPS |
| **W8** | 분석 API 기본 구현 (중심성) | Backend | centrality API |
| **W9** | MVP 배포, 초기 사용자 모집 | DevOps | 100명 |
| **W10** | 논문 1편 제출 | Research | KCI 등재지 |
| **W11** | 정부 기관 미팅 | Business | 제안서 제출 |
| **W12** | 버그 수정, 성능 최적화 | QA + Eng | KPI 달성 |

**Phase 1 목표**:
- ✅ Galaxy3D 60 FPS 렌더링
- ✅ 100명 데이터 신뢰도 0.85
- ✅ 기본 API 5개 공개
- ✅ 논문 1편 발표
- ✅ MAU 100명 달성

### 7.2 Phase 2 (Month 4-6): 기본 상용화

| Month | 마일스톤 | 담당팀 | 목표 |
|-------|----------|--------|------|
| **M4** | 분석 대시보드 완성 | Frontend | 10+ 메트릭 |
| | 이상치 탐지 구현 | Backend + ML | 정확도 75% |
| | API 15개 공개 | Backend | 전체 명세 |
| **M5** | 정부 계약 체결 (3억) | Business | 계약서 서명 |
| | 기관 구독 5곳 확보 | Business | 5곳 |
| | 논문 4편 추가 (총 5편) | Research | 발표 완료 |
| | MAU 1,000명 달성 | Product | 1,000 DAU |
| **M6** | 성능 최적화 (캐싱) | Backend | 응답시간 < 150ms |
| | 보안 감사 완료 | Security | 0 critical |
| | Year 2 계획 수립 | Planning | 예산 배정 |

**Phase 2 목표**:
- ✅ 수익 4.8억 원 (목표: 3억 + 1.5억 + 0.3억)
- ✅ MAU 1,000명
- ✅ 논문 5편
- ✅ 기관 구독 5곳

### 7.3 Phase 3 (Month 7-12): 확장 & 최적화

| Month | 마일스톤 |
|-------|----------|
| **M7-M8** | 데이터 500명 확장, 국제 협력 시작 |
| **M9-M10** | API 25개 공개, GraphQL 옵션 검토 |
| **M11-M12** | Year 2 성능 목표 달성, 예산 계획 |

**Phase 3 목표**:
- ✅ MAU 5,000명
- ✅ 기관 구독 25곳
- ✅ 수익성 흑자 전환 (6억 원)

---

## 8. 기술 스택 최종 확인

### 8.1 Frontend

```
Framework: React 18 + TypeScript
Builder: Vite 4.0+
3D 렌더링: Three.js r128+
차트: D3.js + Chart.js + Plotly
상태관리: React Hooks + Context API
스타일: Tailwind CSS
테스트: Jest + React Testing Library
배포: Vercel
```

### 8.2 Backend

```
Framework: FastAPI 0.100+
언어: Python 3.10+
데이터베이스: Neo4j Aura
ORM: py2neo
API 문서: Swagger/OpenAPI 3.0
캐싱: Redis
인증: JWT
테스트: Pytest
배포: Railway / Heroku
```

### 8.3 데이터 & ML

```
수집: Python + requests + BeautifulSoup
정규화: Pandas + Polars
분석: scikit-learn + NetworkX
이상치 탐지: Isolation Forest + ARIMA
LLM: Claude 3.5 Sonnet (Anthropic)
시각화: Matplotlib + Seaborn
```

### 8.4 성능 모니터링 및 알림 시스템 (신규)

#### 8.4.1 모니터링 메트릭 정의

**애플리케이션 메트릭:**

| 메트릭 | 측정 방식 | 임계값 (Warning) | 임계값 (Critical) | 알림 채널 |
|--------|----------|------------------|-------------------|----------|
| **API 응답시간** | Prometheus | > 200ms (p90) | > 500ms (p90) | Slack, Email |
| **API 에러율** | Prometheus | > 1% | > 5% | PagerDuty |
| **갤럭시 로딩 시간** | Custom timer | > 3초 | > 5초 | Slack |
| **3D 렌더링 FPS** | Chrome DevTools | < 55 FPS | < 30 FPS | Slack |
| **Neo4j 쿼리 시간** | Neo4j 내장 | > 1초 | > 3초 | Slack |
| **메모리 사용량** | Prometheus | > 80% | > 95% | PagerDuty |
| **CPU 사용량** | Prometheus | > 70% | > 90% | Slack |
| **디스크 사용량** | Prometheus | > 80% | > 95% | PagerDuty |

**비즈니스 메트릭:**

| 메트릭 | 측정 방식 | 임계값 (Warning) | 임계값 (Critical) | 알림 채널 |
|--------|----------|------------------|-------------------|----------|
| **데이터 신뢰도 평균** | 주기적 계산 | < 0.88 | < 0.85 | Email, Slack |
| **데이터 검증 통과율** | 파이프라인 로그 | < 97% | < 95% | Email |
| **API 요청 수** | Prometheus | 일일 목표의 80% | 일일 목표의 50% | Slack |
| **사용자 이탈률** | Google Analytics | > 30% | > 50% | Slack |

#### 8.4.2 모니터링 도구 스택

```
프론트엔드 모니터링:
├─ Sentry: 에러 추적 및 성능 모니터링
├─ Google Analytics: 사용자 행동 분석
├─ Lighthouse CI: 성능 점수 자동 측정
└─ Custom 메트릭: 갤럭시 FPS, 로딩 시간

백엔드 모니터링:
├─ Prometheus: 메트릭 수집 및 저장
├─ Grafana: 메트릭 시각화 및 대시보드
├─ ELK Stack: 로그 수집 및 분석
└─ DataDog: APM (Application Performance Monitoring)

데이터베이스 모니터링:
├─ Neo4j 내장 모니터링: 쿼리 성능, 메모리 사용량
├─ Prometheus Neo4j Exporter: Neo4j 메트릭 수집
└─ Custom 쿼리 모니터링: 느린 쿼리 감지

인프라 모니터링:
├─ CloudWatch (AWS) / Azure Monitor: 서버 리소스
├─ Uptime Robot: 가용성 모니터링 (5분 간격)
└─ Pingdom: 외부 모니터링
```

#### 8.4.3 알림 시스템 구성

**알림 채널:**

```
1. Slack 채널:
   ├─ #argo-alerts-critical: Critical 알림 (즉시 대응)
   ├─ #argo-alerts-warning: Warning 알림 (모니터링)
   └─ #argo-alerts-info: 정보성 알림 (일일 요약)

2. Email:
   ├─ 일일 요약 리포트 (매일 오전 9시)
   ├─ 주간 성능 리포트 (매주 월요일)
   └─ Critical 알림 (즉시)

3. PagerDuty:
   ├─ Critical 알림만 (24/7 온콜)
   └─ 에스컬레이션 정책: 5분 미응답 시 다음 담당자
```

**알림 규칙:**

```
Critical 알림 (즉시 대응):
├─ API 에러율 > 5%
├─ 서비스 가용성 < 99%
├─ 데이터 신뢰도 < 0.85
├─ 메모리 사용량 > 95%
└─ Neo4j 연결 실패 (연속 3회)

Warning 알림 (모니터링):
├─ API 응답시간 > 200ms (p90)
├─ 갤럭시 로딩 시간 > 3초
├─ 3D 렌더링 FPS < 55
├─ 데이터 검증 통과율 < 97%
└─ CPU 사용량 > 70%

Info 알림 (일일 요약):
├─ 일일 API 요청 수
├─ 일일 신규 사용자 수
├─ 평균 응답시간
└─ 에러 통계
```

#### 8.4.4 자동 스케일링 정책

**백엔드 API (Railway/Heroku):**

```
스케일 업 트리거:
├─ CPU 사용량 > 70% (5분 지속)
├─ 메모리 사용량 > 80% (5분 지속)
├─ 응답시간 > 300ms (p90, 5분 지속)
└─ 동시 요청 수 > 50개

스케일 다운 트리거:
├─ CPU 사용량 < 30% (30분 지속)
├─ 메모리 사용량 < 50% (30분 지속)
└─ 동시 요청 수 < 10개

스케일링 범위:
├─ 최소 인스턴스: 1개
├─ 최대 인스턴스: 5개 (Year 1)
└─ 인스턴스 타입: Standard-1X (1GB RAM)
```

**Neo4j Aura (클라우드):**

```
스케일 업 트리거:
├─ 쿼리 응답시간 > 1초 (평균, 10분 지속)
├─ 메모리 사용량 > 80% (10분 지속)
└─ 동시 쿼리 수 > 100개

스케일 다운 트리거:
├─ 쿼리 응답시간 < 200ms (평균, 1시간 지속)
├─ 메모리 사용량 < 50% (1시간 지속)
└─ 동시 쿼리 수 < 20개

스케일링 범위:
├─ 최소 인스턴스: Aura Free (1GB RAM)
├─ 최대 인스턴스: Aura Professional (32GB RAM)
└─ 자동 스케일링: Neo4j Aura 내장 기능 활용
```

#### 8.4.5 SLA 위반 시 대응 프로세스

```
Step 1: 알림 수신 (PagerDuty/Slack)
Step 2: 문제 확인 (Grafana 대시보드)
Step 3: 심각도 평가 (Critical/Warning/Info)
Step 4: 즉시 대응 (Critical만)
   ├─ 자동 스케일링 트리거
   ├─ Circuit Breaker 활성화
   └─ 폴백 모드 전환
Step 5: 근본 원인 분석 (RCA)
Step 6: 장기 해결책 수립
Step 7: 문서화 및 개선 사항 반영
```

---

## 9. 최종 체크리스트

### 9.1 개발 시작 전

```
[ ] BRD 승인 완료 (경영진)
[ ] PRD 승인 완료 (제품팀)
[ ] TSD 승인 완료 (기술팀)
[ ] SRD 승인 완료 (전체 팀)
[ ] 예산 배정 완료 (5~7억 원)
[ ] 팀 구성 완료 (3~5명)
[ ] 개발 환경 준비 (IDE, 클라우드, 도구)
[ ] 데이터 수집 시작 (ARKO API 접근)
```

### 9.2 Phase 1 완료 기준

```
Feature 1 (F1):
[ ] 60 FPS 유지 (desktop)
[ ] 초기 로드 < 3초
[ ] 모든 필터 동작 (7가지)
[ ] 모든 브라우저 호환
[ ] 테스트 커버리지 > 80%

Feature 2 (F2):
[ ] 100명 데이터 신뢰도 > 0.85
[ ] 점수 계산 일관성 (재계산 시 동일)
[ ] Neo4j 관계 설정 완료
[ ] 백업 자동화 완료
[ ] 문서 공개 완료

Feature 1 + 2 (MVP):
[ ] 홈화면 → 갤럭시 렌더링 → 미술가 선택 (완전한 흐름)
[ ] API 응답시간 < 200ms
[ ] 메모리 누수 없음
[ ] QA 테스트 통과율 > 95%
```

### 9.3 전체 프로젝트 체크리스트

```
기술:
[ ] 모든 API 엔드포인트 구현 (20+)
[ ] 모든 테스트 작성 및 통과 (단위, 통합, E2E)
[ ] 성능 최적화 완료 (캐싱, 인덱싱)
[ ] 보안 감사 완료 (0 critical)
[ ] 배포 자동화 완료 (CI/CD)

문서:
[ ] 기술 문서 완성 (API, 스키마, 아키텍처)
[ ] 사용자 문서 완성 (FAQ, 튜토리얼)
[ ] 학술 논문 5편 발표
[ ] 방법론 공개 (Cypher 쿼리)

비즈니스:
[ ] 정부 계약 체결 (3억)
[ ] 기관 구독 5곳 확보
[ ] MAU 1,000명 달성
[ ] 데이터 신뢰도 0.85 확보
[ ] 수익성 목표 달성
```

### 9.4 재해 복구 계획 (DRP) (신규)

#### 9.4.1 재해 시나리오 및 대응

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
   ├─ 새 인스턴스 자동 생성 (Railway/Heroku)
   ├─ 환경 변수 복원
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
├─ CDN 캐싱: 정적 자산은 영향 없음
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

**시나리오 4: 보안 침해**

```
심각도: Critical
영향: 데이터 유출, 서비스 신뢰도 하락
복구 목표 시간 (RTO): 2시간
복구 목표 시점 (RPO): 침해 발견 시점

대응 절차:
1. 즉시 대응 (0-30분)
   ├─ 침해 범위 확인
   ├─ 영향받은 시스템 격리
   ├─ 보안 팀 소집
   └─ 법무팀 통보 (필요시)

2. 침해 차단 (30분-1시간)
   ├─ 침해 경로 차단
   ├─ API 키 무효화
   ├─ 비밀번호 강제 변경
   └─ 로그 분석 (침해 경로 추적)

3. 복구 실행 (1-2시간)
   ├─ 침해된 시스템 재구축
   ├─ 보안 패치 적용
   ├─ 데이터 무결성 검증
   └─ 보안 감사

4. 사후 조치 (2시간 이후)
   ├─ 침해 보고서 작성
   ├─ 사용자 공지 (필요시)
   ├─ 보안 정책 개선
   └─ 재발 방지 조치
```

#### 9.4.2 백업 정책

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

#### 9.4.3 복구 테스트 계획

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

## 결론

**SRD는 BRD → PRD → TSD → SRD의 완벽한 동기화 체계를 완성한다.**

```
BRD (비즈니스 목표)
  ├─ Year 1 MAU: 1,000명
  ├─ Year 1 수익: 4.8억 원
  └─ Year 1 신뢰도: 0.85
       ↓ 달성 수단
PRD (제품 기능)
  ├─ 갤럭시 시각화
  ├─ 분석 대시보드
  ├─ 이상치 탐지
  └─ 공개 API
       ↓ 구현 수단
TSD (기술 아키텍처)
  ├─ React + Three.js (3D)
  ├─ FastAPI + Neo4j (백엔드)
  └─ 20+ API 엔드포인트
       ↓ 상세 명세
SRD (개발 요구사항)
  ├─ F1: Galaxy3D 60 FPS 유지
  ├─ F2: 100명 신뢰도 > 0.85
  ├─ F3: 10+ 분석 메트릭
  ├─ F4: 이상치 탐지 정확도 80%
  └─ F5: 20+ API 엔드포인트
       ↓ 구현 완료
KPI 달성 → 비즈니스 목표 달성
```

**다음 단계**:

1. ✅ 모든 문서 (BRD, PRD, TSD, SRD) 승인
2. ⏳ Antigravity에서 Neo4j 초기화
3. ⏳ Cursor에서 Backend 개발 시작
4. ⏳ Google AI Studio에서 Frontend 코드 생성
5. ⏳ 100명 데이터 수집 & 정규화 병행
6. ⏳ Month 3 MVP 배포

---

**Document Owner**: Engineering & Product Team  
**Last Updated**: 2025-12-08  
**Next Review**: 2025-12-15 (Phase 1 Kick-off Meeting)
