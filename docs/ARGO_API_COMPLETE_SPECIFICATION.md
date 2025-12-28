# ARGO API 통합 명세서
## Complete API Specification

**작성일**: 2025-12-09  
**버전**: 1.0  
**프로젝트 ID**: artdrive1208  
**상태**: 통합 완료  
**대상**: 백엔드 개발자, 프론트엔드 개발자, 데이터 수집 개발자

---

## 문서 개요 및 목적

### 1.1 문서의 목적

이 문서는 ARGO 프로젝트의 모든 API 관련 명세를 통합한 단일 문서입니다.

**통합된 문서:**
- 백엔드 API 명세 (프론트엔드-백엔드 간 API)
- 데이터 소스 API 명세 (외부 데이터 수집용 API)
- API 개발 가이드라인 (백엔드 개발 시 필수 참조)

**주요 목적:**
- 문서 간 일관성 및 정합성 확보
- 참조 관계 명확화
- 유지보수 효율성 향상
- 개발자 경험 개선

### 1.2 문서 사용 가이드

**백엔드 개발 시:**
1. Part I: 백엔드 API 명세 참조
2. Part III: API 개발 가이드 참조
3. OpenAPI 명세서 (`ARGO_API_SPECIFICATION.yaml`) 참조

**데이터 수집 개발 시:**
1. Part II: 데이터 소스 API 명세 참조
2. `ARGO_DATA_COLLECTION_METHODOLOGY.md` 참조

**프론트엔드 개발 시:**
1. Part I: 백엔드 API 명세 참조
2. Part III: API 스키마 상세 정의 참조

### 1.3 프로젝트 정보

- **프로젝트 이름**: ARTDRIVE
- **프로젝트 ID**: artdrive1208
- **리전**: asia-northeast3 (서울)
- **초기 API Base URL**: `https://artdrive1208-api-xxx.run.app/v1`
- **향후 커스텀 도메인**: `https://api.argo.art/v1`

---

## Part I: 백엔드 API 명세

### 2.1 API 개요

ARGO 백엔드 API는 한국 미술계 구조 분석 엔진의 RESTful API입니다.

**특징:**
- 모든 응답은 JSON-LD 형식 (Schema.org 표준)을 따릅니다
- 총 34개 엔드포인트 제공
- 프론트엔드-백엔드 간 API 계약 정의

**AI 모델 정보:**
- 이상치 탐지 가설 생성: Gemini 3 Pro Preview (`gemini-3-pro-preview`)
- 환경변수: `GEMINI_API_KEY` (로컬 `.env` 파일 또는 GCP Secret Manager)

**구분:**
- **백엔드 API** (이 Part): ARGO 시스템이 제공하는 API (프론트엔드-백엔드 간)
- **데이터 소스 API** (Part II): 외부에서 데이터를 수집하는 API

### 2.2 엔드포인트 목록

총 **34개 엔드포인트**가 정의되어 있습니다.

#### 2.2.1 Artists API (9개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/v1/api/artists` | 모든 작가 조회 (페이지네이션, 필터 지원) |
| GET | `/v1/api/artists/{artist_id}` | 작가 상세 정보 조회 |
| GET | `/v1/api/artists/{artist_id}/network` | 작가 네트워크 그래프 조회 |
| GET | `/v1/api/artists/{artist_id}/exhibitions` | 작가 전시 목록 조회 |
| GET | `/v1/api/artists/{artist_id}/artworks` | 작가 작품 목록 조회 |
| GET | `/v1/api/artists/{artist_id}/structural-equivalents` | 구조적 등가성 작가 조회 |
| GET | `/v1/api/artists/{artist_id}/capital-composition` | 자본 구성 분석 조회 |
| GET | `/v1/api/artists/{artist_id}/market` | 작가 시장 정보 조회 |
| POST | `/v1/api/artists/search` | 작가 전문 검색 |

#### 2.2.2 Institutions API (5개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/v1/api/institutions` | 모든 기관 조회 |
| GET | `/v1/api/institutions/{inst_id}` | 기관 상세 정보 조회 |
| GET | `/v1/api/institutions/{inst_id}/affiliated-artists` | 소속 미술가 목록 조회 |
| GET | `/v1/api/institutions/{inst_id}/exhibitions` | 기관 전시 목록 조회 |
| GET | `/v1/api/institutions/{inst_id}/benchmarking` | 기관 벤치마킹 조회 |

#### 2.2.3 Exhibitions API (2개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/v1/api/exhibitions` | 모든 전시 조회 |
| GET | `/v1/api/exhibitions/{exh_id}` | 전시 상세 정보 조회 |

#### 2.2.4 Transactions API (3개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/v1/api/transactions` | 모든 거래 조회 |
| GET | `/v1/api/transactions/{trans_id}` | 거래 상세 정보 조회 |
| GET | `/v1/api/transactions/price-history/{artist_id}` | 작가 가격 히스토리 조회 |

#### 2.2.5 Clusters API (2개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/v1/api/clusters` | 모든 군집 조회 |
| GET | `/v1/api/clusters/{cluster_id}` | 군집 상세 정보 조회 |

#### 2.2.6 Analysis API (8개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/v1/api/analysis/centrality` | 중심성 계산 |
| POST | `/v1/api/analysis/community-detection` | 커뮤니티 탐지 |
| GET | `/v1/api/analysis/correlation` | 상관관계 분석 |
| POST | `/v1/api/analysis/compare` | 작가 비교 분석 |
| GET | `/v1/api/analysis/field-quadrants` | 필드 분면 분류 조회 |
| POST | `/v1/api/analysis/run-gds-centrality` | GDS 중심성 분석 실행 |
| POST | `/v1/api/analysis/run-louvain` | Louvain 커뮤니티 탐지 실행 |
| POST | `/v1/api/analysis/calculate-structuralist` | 구조주의 분석 필드 계산 |

#### 2.2.7 Anomalies API (2개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/v1/api/anomalies` | 이상치 목록 조회 (Gemini 3 Pro Preview) |
| POST | `/v1/api/anomalies/analyze` | 이상치 재분석 (Gemini 3 Pro Preview) |

#### 2.2.8 Search API (1개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/v1/api/search` | 통합 검색 |

#### 2.2.9 Galaxy API (2개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/v1/api/galaxy-snapshot` | 갤럭시 스냅샷 조회 |
| GET | `/v1/api/metadata/sources` | 데이터 출처 조회 |

### 2.3 엔드포인트 상세 명세

각 엔드포인트의 상세 명세는 `ARGO_API_SPECIFICATION.yaml` 파일을 참조하세요.

**주요 엔드포인트 예시:**

#### GET /v1/api/artists

**요청 파라미터:**
- `skip` (query, integer, 기본값: 0): 건너뛸 레코드 수
- `limit` (query, integer, 기본값: 20, 최대: 100): 페이지당 항목 수
- `segment_id` (query, string, 선택): 세그먼트 ID 필터
- `career_stage` (query, string, 선택): 경력 단계 필터 (early, mid, late, established)
- `min_score` (query, float, 선택): 최소 복합 점수 필터 (0-100)

**응답 형식:**
```json
{
  "artists": [
    {
      "@context": "https://schema.org/",
      "@type": "Person",
      "@id": "argo://artist/artist_001",
      "name": "작가 A",
      "argo:scores": {
        "argo:composite_score": 74.15
      }
    }
  ],
  "total": 100,
  "page": 1
}
```

#### GET /v1/api/artists/{artist_id}

**경로 파라미터:**
- `artist_id` (path, string, 필수): 작가 ID

**응답 형식:**
- 작가 상세 정보 및 모든 관계 데이터 포함
- `collaborations`, `institutions`, `exhibitions` 배열 포함
- `coordinates_3d` 필드 필수 포함

### 2.4 요청/응답 스키마

#### 2.4.1 공통 스키마

**페이지네이션 응답:**
```json
{
  "{entity_plural}": [/* 엔터티 배열 */],
  "total": 100,
  "page": 1
}
```

**에러 응답:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지",
    "details": "상세 정보",
    "timestamp": "2025-12-09T00:00:00Z",
    "request_id": "uuid"
  }
}
```

#### 2.4.2 엔터티 스키마

각 엔터티의 상세 스키마는 Part III 섹션 4.2를 참조하세요.

**주요 엔터티:**
- Artist (작가)
- Institution (기관)
- Exhibition (전시)
- Transaction (거래)
- Cluster (군집)
- Artwork (작품)
- NetworkGraph (네트워크 그래프)
- GalaxySnapshot (갤럭시 스냅샷)

### 2.5 OpenAPI 명세서 참조

**파일 위치:** `docs/ARGO_API_SPECIFICATION.yaml`

**OpenAPI 표준 사용 이유:**
- 산업 표준 형식으로 다양한 도구 지원
- Swagger UI를 통한 대화형 문서 제공
- 코드 자동 생성 (FastAPI, TypeScript 등)
- API 클라이언트 자동 생성

**YAML 파일 사용법:**

1. **Swagger UI로 확인:**
   - `https://editor.swagger.io/` 에서 YAML 파일 업로드
   - 또는 FastAPI의 `/docs` 엔드포인트 사용

2. **코드 생성:**
   - OpenAPI Generator를 사용하여 클라이언트 코드 생성
   - FastAPI는 YAML 파일을 직접 읽어서 라우터 자동 생성 가능

3. **검증:**
   - OpenAPI 스키마 검증 도구 사용
   - 요청/응답 형식 자동 검증

**중요 사항:**
- YAML 파일은 OpenAPI 3.0.3 표준을 따릅니다
- 모든 엔드포인트는 `/v1/api/*` 경로를 사용합니다
- 모든 응답은 JSON-LD 형식을 따릅니다

---

## Part II: 데이터 소스 API 명세

### 3.1 데이터 소스 API 개요

데이터 소스 API는 ARGO 시스템이 외부에서 데이터를 수집하기 위해 호출하는 API입니다.

**목적:**
- 작가, 작품, 기관, 전시 등 미술계 데이터 수집
- 점수 계산에 필요한 데이터 수집
- 네트워크 분석을 위한 관계 데이터 수집

**데이터 수집 프로세스:**
```
외부 API → Collector → 정규화 → 점수 계산 → Neo4j 업로드
```

**구분:**
- **데이터 소스 API** (이 Part): 외부에서 데이터를 수집하는 API
- **백엔드 API** (Part I): ARGO 시스템이 제공하는 API

### 3.2 전체 API 목록

현재 **9개 API**가 연동되어 있습니다.

| # | API 이름 | 데이터량 | 신뢰도 | 상태 | 구현 파일 |
|---|---------|---------|--------|------|-----------|
| 1 | ARKO 작가 목록 | 505명 | 0.95 | ✅ 완료 | `app/collectors/arko_collector.py` |
| 2 | ARKO 미술작품 정보 | 24,762개 | 0.95 | ✅ 완료 | `app/collectors/artwork_collector.py` |
| 3 | ARKO 예술단체 목록 | 94개 | 0.95 | ✅ 완료 | `app/collectors/institution_collector.py` |
| 4 | ARKO 채용정보 | 363개 | 0.85 | ✅ 완료 | `app/collectors/job_collector.py` |
| 5 | KCI 논문 정보 | ~10,000개 (미술 관련) | 0.85 | ✅ 완료 | `app/collectors/kci_collector.py` |
| 6 | KCI 인용 정보 | ~1,400,000명 (미술 관련 필터링) | 0.90 | ✅ 완료 | `app/collectors/kci_citation_collector.py` |
| 7 | 청주공예비엔날레 | 수천 개 (작품 기준) | 0.90 | ✅ 완료 | `app/collectors/cheongju_biennale_collector.py` |
| 8 | MMCA 레지던시작가소식 | 수백 개 (소식 기준) | 0.92 | ✅ 완료 | `app/collectors/mmca_residency_collector.py` |
| 9 | MMCA 소장작품 | 수천 개 (작품 기준) | 0.95 | ✅ 완료 | `app/collectors/mmca_collection_collector.py` |

**총 데이터량**: 작가 505명, 작품 24,762개, 기관 94개, 채용정보 363개, 논문 ~10,000개, 인용 정보 ~1,400,000명, 비엔날레 작품 수천 개, 레지던시 소식 수백 개, MMCA 소장작품 수천 개

### 3.3 API 상세 명세

각 API의 상세 명세는 아래 섹션을 참조하세요.

#### 3.3.1 ARKO 작가 목록 API

**기본 정보:**
- **API 이름**: 한국문화예술위원회_미술작가목록_20200518
- **데이터 제공자**: 한국문화예술위원회
- **데이터 시점**: 2020년 5월
- **데이터량**: 505명
- **신뢰도**: 0.95 (최고)

**API 엔드포인트:**
```
GET https://api.odcloud.kr/api/15046037/v1/uddi:0688d256-3e27-4714-b5a6-c67c2b0e34e3
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`ARKO_API_KEY`)

**파라미터:**
- `page`: 페이지 번호 (기본: 1)
- `perPage`: 페이지당 항목 수 (기본: 10, 최대: 100)
- `returnType`: 응답 형식 (기본: JSON)

**데이터 필드:**
- `이름`: 작가 한글 이름
- `이형표기`: 작가 영문 이름
- `분야`: 작가 전문 분야 (회화, 조각, 공예, 사진 등)

**활용 목적:**
- Artist 엔터티 생성
- 작가 기본 정보 수집
- segment_id 생성 (분야 기반)

**구현 파일:**
- `app/collectors/arko_collector.py`
- `test_arko_api.py`

#### 3.3.2 ARKO 미술작품 정보 API

**기본 정보:**
- **API 이름**: 한국문화예술위원회_미술작품 정보_20250430
- **데이터 제공자**: 한국문화예술위원회
- **데이터 시점**: 1988년~2024년
- **데이터량**: 24,762개
- **신뢰도**: 0.95 (최고)

**API 엔드포인트:**
```
GET https://api.odcloud.kr/api/15083293/v1/uddi:53bdef84-da7b-4635-a6a7-b820b5dc8f86
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`ARKO_API_KEY`)

**데이터 필드:**
- `설치일자`: 작품 설치 날짜 (YYYY-MM-DD)
- `지역`: 설치 지역 (시/구 형식)
- `작품명`: 작품 이름
- `작가명`: 작가 이름
- `분류`: 작품 분류 (조각, 회화, 미디어 등)
- `건축물명`: 설치된 건축물 이름
- `건축물주소`: 건축물 주소
- `건축물용도`: 건축물 용도 (공동주택, 업무시설 등)

**활용 목적:**
- 작가의 제도 점수(inst_score) 계산
- 작가별 작품 수 집계
- 작가-작품 관계 매핑
- 지역별 작품 분포 분석

**구현 파일:**
- `app/collectors/artwork_collector.py`
- `test_artwork_api.py`

**데이터 활용 인사이트:**
- 건축물 미술작품 설치 = 제도 레이어 활동
- 작품 수를 `museum_exhibitions` 필드에 반영
- `inst_score` 계산에 활용: `(작품수 * 20)`

#### 3.3.3 ARKO 예술단체 목록 API

**기본 정보:**
- **API 이름**: 한국예술디지털아카이브 등록 예술단체 및 예술인 목록_20200518
- **데이터 제공자**: 한국문화예술위원회
- **데이터 시점**: 2020년 5월
- **데이터량**: 94개
- **신뢰도**: 0.95 (최고)

**API 엔드포인트:**
```
GET https://api.odcloud.kr/api/15046039/v1/uddi:832b90cb-c626-4381-9ebe-9e0bf527e118
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`ARKO_API_KEY`)

**데이터 필드:**
- `단체명`: 예술단체 이름
- `대표명`: 단체 대표자 이름
- `관련페이지주소`: 단체 상세 정보 URL

**활용 목적:**
- Institution 엔터티 생성
- 작가-기관 관계 매핑 (대표자 이름 기반)
- 기관 네트워크 구축

**구현 파일:**
- `app/collectors/institution_collector.py`
- `test_institution_api.py`

#### 3.3.4 ARKO 채용정보 API

**기본 정보:**
- **API 이름**: 한국문화예술위원회_문화예술 채용정보_20160705
- **데이터 제공자**: 한국문화예술위원회
- **데이터 시점**: 2016년 7월 (1회성 데이터)
- **데이터량**: 363개
- **신뢰도**: 0.85 (과거 데이터이므로 신뢰도 낮음)

**API 엔드포인트:**
```
GET https://api.odcloud.kr/api/15012952/v1/uddi:047d7b05-2abc-4f26-957f-a20ec21f773e_201607051740
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`ARKO_API_KEY`)

**데이터 필드:**
- `기관명`: 채용 기관 이름
- `근무지역`: 근무 지역 (시/구 형식 또는 상세 주소)
- `마감일`: 채용 마감일 (YYYY-MM-DD)

**활용 목적:**
- Institution 정보 보강
- 기관 활동성 측정
- 지역별 기관 분포 분석

**구현 파일:**
- `app/collectors/job_collector.py`
- `test_job_api.py`

**데이터 활용 인사이트:**
- 2016년 데이터이므로 현재 시점에서는 제한적 활용
- 기관의 과거 활동성 측정에 활용 가능
- 향후 최신 채용정보 API 연동 필요

#### 3.3.5 KCI 논문 정보 API

**기본 정보:**
- **API 이름**: 한국연구재단_KCI논문정보_20250825
- **데이터 제공자**: 한국연구재단
- **데이터 시점**: 2025년 8월 25일 (최신 버전)
- **데이터량**: 전체 ~수십만 개 (미술 관련 필터링 시 ~10,000개 예상)
- **신뢰도**: 0.85 (학술 데이터, 공식 소스)
- **업데이트 주기**: 연간

**API 엔드포인트:**
```
GET https://api.odcloud.kr/api/15083283/v1/uddi:9cdf9a0d-6563-4dfe-9957-ecbe798c53e6
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`ARKO_API_KEY`)

**주요 데이터 필드:**
- `논문명(국문)`: 논문 한글 제목
- `저자`: 제1저자 이름
- `공동저자`: 공동저자 이름 (쉼표 구분)
- `학술지명(국문)`: 학술지 한글 이름
- `발행년`: 논문 발행 연도
- `주제분야`: 논문 주제 분야
- `키워드(국문)`: 논문 키워드

**활용 목적:**
- 작가의 학술 점수(acad_score) 계산
- 작가별 논문 수 집계
- 작가-연구자 네트워크 구축
- 학술 인용 패턴 분석

**구현 파일:**
- `app/collectors/kci_collector.py`
- `test_kci_api.py`

**데이터 활용 인사이트:**
- **학술 점수 계산 강화**: KCI 등재 논문 수를 `academic_publications` 필드에 반영
- **학술 점수 계산식**: `(citation_count * 2) + (catalog_count * 5) + (academic_publications * 3)`
- **작가-연구자 네트워크**: 공동저자 정보를 활용하여 작가 간 학술 협력 관계 발견 가능

**매칭 전략:**
- 작가 이름(한글, 영문)으로 저자 필드 매칭
- 정확 일치 우선, 부분 일치 보조

**필터링 전략:**
- 미술 관련 키워드 기반 필터링 (주제분야, 논문명, 키워드)
- 필터링 키워드: "미술", "예술", "조형", "회화", "조각", "공예", "디자인" 등

#### 3.3.6 KCI 인용 정보 서비스 API

**기본 정보:**
- **API 이름**: 한국연구재단_KCI 인용 정보 서비스
- **데이터 제공자**: 한국연구재단
- **데이터 시점**: 실시간 (일 1회 갱신)
- **데이터량**: 전체 ~1,400,000명 (미술 관련 필터링 시 수천~수만 명 예상)
- **신뢰도**: 0.90 (인용 통계 데이터, 공식 소스)
- **업데이트 주기**: 일 1회
- **데이터 형식**: XML

**API 엔드포인트:**
```
저자별 인용지수: GET http://apis.data.go.kr/B552540/KCIOpenApi/citedInfo/openApiM376List
인용정보(학술지별): GET http://apis.data.go.kr/B552540/KCIOpenApi/citedInfo/openApiM373List
공용코드: GET http://apis.data.go.kr/B552540/KCIOpenApi/citedInfo/openApiM372List
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`ARKO_API_KEY`)

**주요 데이터 필드:**
- `CRET_KOR_NM`: 저자명(한글)
- `CRET_ENG_NM`: 저자명(영문)
- `TOT_SERE_CNT`: 전체년도 피인용수 (가장 중요)
- `TOT_ARTI_CNT`: 전체년도 논문수
- `H_IDX`: H지수
- `SERE_AVG`: 평균 피인용 횟수

**활용 목적:**
- 작가의 실제 인용 수 확인 (기존 추정값 대체)
- H지수 등 학술 영향력 지표 제공
- 자기 인용 수 분석

**구현 파일:**
- `app/collectors/kci_citation_collector.py`
- `test_kci_citation_api.py`

**데이터 활용 인사이트:**
- 실제 인용 수를 제공하여 기존 추정값 대체 가능 ✅
- H지수, 평균 인용 수 등 학술 영향력 지표 제공
- Rate Limit: 초당 30회 제한

#### 3.3.7 청주공예비엔날레 API

**기본 정보:**
- **API 이름**: 청주공예비엔날레 출품작 정보
- **데이터 제공자**: 청주공예비엔날레 조직위원회
- **데이터량**: 수천 개 (작품 기준)
- **신뢰도**: 0.90

**API 엔드포인트:**
```
GET https://api.odcloud.kr/api/15083294/v1/uddi:...
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`ARKO_API_KEY`)

**활용 목적:**
- 비엔날레 참여 정보 수집 및 제도 점수 계산에 반영
- 작가-비엔날레 매칭 로직 구현
- 입상 정보 수집 기능 추가

**구현 파일:**
- `app/collectors/cheongju_biennale_collector.py`
- `test_cheongju_biennale_api.py`

**데이터 활용 인사이트:**
- 공예 작가 중심 데이터 (도자, 목칠, 섬유, 금속 등)
- 국제 비엔날레 데이터 (국가별 작가 정보 포함)
- 비엔날레 참여 정보를 제도 점수 계산에 반영 가능 ✅

#### 3.3.8 MMCA 레지던시작가소식 API

**기본 정보:**
- **API 이름**: 국립현대미술관 레지던시작가소식
- **데이터 제공자**: 국립현대미술관
- **데이터량**: 수백 개 (소식 기준)
- **신뢰도**: 0.92

**API 엔드포인트:**
```
GET https://api.odcloud.kr/api/.../v1/uddi:...
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`MMCA_RESIDENCY_SERVICE_KEY`)

**활용 목적:**
- 레지던시 참여 정보 수집 및 제도 점수 계산에 반영
- 작가 이름 추출 로직 구현 (제목/설명에서 파싱)
- 작가-레지던시 매칭 로직 구현

**구현 파일:**
- `app/collectors/mmca_residency_collector.py`
- `test_mmca_residency_api.py`

**데이터 활용 인사이트:**
- 국립현대미술관 공식 레지던시 작가 소식 데이터
- 레지던시 참여 정보를 제도 점수 계산에 반영 가능 ✅
- 제도 점수 계산식: `(museum_count * 20) + (biennale_count * 30) + (support_count * 10) + (residency_count * 10)`

#### 3.3.9 MMCA 소장작품 API

**기본 정보:**
- **API 이름**: 국립현대미술관 소장작품
- **데이터 제공자**: 국립현대미술관
- **데이터량**: 수천 개 (작품 기준)
- **신뢰도**: 0.95 (최고)

**API 엔드포인트:**
```
GET https://api.odcloud.kr/api/.../v1/uddi:...
```

**인증:**
- `serviceKey` 쿼리 파라미터: GCP Secret Manager에서 관리 (`MMCA_COLLECTION_SERVICE_KEY`)

**활용 목적:**
- 소장작품 정보 수집 및 제도 점수 계산에 반영
- 작가-소장작품 매칭 로직 구현 (creator 필드 기반)
- 제도적 인정의 최고 지표로 활용

**구현 파일:**
- `app/collectors/mmca_collection_collector.py`
- `test_mmca_collection_api.py`

**데이터 활용 인사이트:**
- 국립현대미술관 공식 소장작품 데이터
- 작가명이 명시적으로 제공됨 (creator 필드)
- 소장작품 정보를 제도 점수 계산에 반영 가능 ✅
- 국립현대미술관 소장은 제도적 인정의 최고 지표

### 3.4 데이터 활용 인사이트

각 API의 데이터가 점수 계산에 어떻게 반영되는지 요약합니다.

#### 3.4.1 제도 점수(inst_score) 계산에 반영

**계산식:**
```
inst_score = (museum_count * 20) + (biennale_count * 30) + (support_count * 10) + (residency_count * 10)
```

**반영되는 API:**
- ARKO 미술작품 정보: `museum_count` 증가 (작품 수 기반)
- 청주공예비엔날레: `biennale_count` 증가
- MMCA 레지던시작가소식: `residency_count` 증가
- MMCA 소장작품: `museum_count` 증가 (최고 가중치)

#### 3.4.2 학술 점수(acad_score) 계산에 반영

**계산식:**
```
acad_score = (citation_count * 2) + (catalog_count * 5) + (academic_publications * 3)
```

**반영되는 API:**
- KCI 논문 정보: `academic_publications` 증가
- KCI 인용 정보: `citation_count` 증가 (실제 인용 수)

#### 3.4.3 데이터 매칭 전략

**작가 이름 매칭:**
- 한글 이름 정확 일치 우선
- 영문 이름 부분 일치 보조
- 동명이인 문제 해결 필요

**기관 매칭:**
- 기관명 정확 일치
- URL 정규화 필요

### 3.5 향후 추가 예정 API

**계획된 API:**
- MMCA 전시 정보 크롤링 (버전 1.6 예정)
- 경매사 API 연동 (버전 2.0 예정)

---

## Part III: API 개발 가이드

### 4.1 백엔드 개발 가이드라인

#### 4.1.1 Antigravity IDE 사용 가이드

**OpenAPI 명세서 입력:**
1. Antigravity IDE에서 새 프로젝트 생성
2. "Import OpenAPI Specification" 선택
3. `docs/ARGO_API_SPECIFICATION.yaml` 파일 업로드 또는 경로 지정
4. Pydantic 모델 자동 생성 옵션 활성화

**예상 결과:**
- FastAPI 라우터 자동 생성
- Pydantic 모델 자동 생성 (OpenAPI 스키마 기반)
- 요청/응답 검증 로직 자동 생성

#### 4.1.2 프로젝트 구조

```
argo-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 애플리케이션 진입점
│   ├── config.py                    # 설정 관리
│   ├── database.py                  # Neo4j 연결 관리
│   ├── middleware.py                # 미들웨어 (JSON-LD, CORS, 에러 처리)
│   ├── models/                      # Pydantic 모델
│   │   ├── __init__.py
│   │   ├── artist.py
│   │   ├── institution.py
│   │   ├── exhibition.py
│   │   ├── transaction.py
│   │   ├── cluster.py
│   │   └── common.py                # 공통 모델 (Scores, Coordinates3D 등)
│   ├── routers/                     # API 라우터
│   │   ├── __init__.py
│   │   ├── artists.py               # 9개 엔드포인트
│   │   ├── institutions.py          # 5개 엔드포인트
│   │   ├── exhibitions.py           # 2개 엔드포인트
│   │   ├── transactions.py          # 3개 엔드포인트
│   │   ├── clusters.py              # 2개 엔드포인트
│   │   ├── analysis.py              # 8개 엔드포인트
│   │   ├── anomalies.py             # 2개 엔드포인트
│   │   └── search.py                # 1개 엔드포인트
│   ├── services/                     # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── artist_service.py
│   │   ├── neo4j_service.py
│   │   └── coordinate_service.py   # 좌표 계산 로직
│   └── utils/                       # 유틸리티 함수
│       ├── __init__.py
│       ├── jsonld.py                # JSON-LD 변환
│       └── errors.py                # 에러 응답 생성
├── requirements.txt                 # Python 의존성
├── .env.example                     # 환경변수 예제
└── README.md                        # 프로젝트 설명
```

#### 4.1.3 의존성 설정

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
neo4j==5.14.0
py2neo==2021.2.4
redis==5.0.1
google-cloud-secret-manager==2.18.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
google-generativeai==0.3.0  # Gemini API
```

**주의사항:**
- Pydantic 2.x 사용 필수 (JSON-LD 변환 미들웨어 호환성)
- FastAPI 0.104+ 사용 (최신 기능 지원)

#### 4.1.4 환경변수 설정

**GCP Secret Manager 연동:**
```python
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    """GCP Secret Manager에서 시크릿 가져오기"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/artdrive1208/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

**로컬 개발 환경:**
- `.env` 파일 사용 (프로덕션에서는 Secret Manager 사용)

### 4.2 API 스키마 상세 정의

이 섹션에서는 각 엔터티별로 상세한 스키마를 정의합니다. **모든 필드명은 정확히 일치해야 하며, 타입과 제약조건을 반드시 준수해야 합니다.**

#### 4.2.1 Artist 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Artist`
- 프론트엔드 타입: `types/argo.ts` → `interface Artist`
- 데이터베이스 스키마: `ARGO_Final_Schema.md` → 섹션 2.1

**필수 필드:**

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 | 프론트엔드 매핑 |
|--------|------------|-----------|----------|--------------|------|----------------|
| `@context` | `str` | `string` | 필수 | `"https://schema.org/"` | `"https://schema.org/"` | - |
| `@type` | `str` | `string` | 필수 | `"Person"` | `"Person"` | - |
| `@id` | `str` | `string` | 필수 | `argo://artist/{artist_id}` 형식 | `"argo://artist/artist_001"` | - |
| `identifier` | `dict` | `object` | 필수 | PropertyValue 타입 | `{"@type": "PropertyValue", "propertyID": "ARGO", "value": "artist_001"}` | - |
| `name` | `str` | `string` | 필수 | - | `"작가 A"` | `artist.name` |
| `alternateName` | `Optional[str]` | `string` | 선택 | - | `"Artist A"` | `artist.alternativeName` |
| `birthDate` | `Optional[str]` | `string` | 선택 | YYYY 형식 | `"1975"` | `artist.birth_year` (변환 필요) |
| `url` | `Optional[str]` | `string` | 선택 | URI 형식 | `"https://example.com/artist_a"` | `artist.url` |
| `argo:scores` | `dict` | `object` | 필수 | - | 아래 참조 | `artist.scores` |
| `argo:inst_score` | `float` | `number` | 필수 | 0-100 | `82.5` | `artist.scores.inst_score` |
| `argo:acad_score` | `float` | `number` | 필수 | 0-100 | `68.0` | `artist.scores.acad_score` |
| `argo:media_score` | `float` | `number` | 필수 | 0-100 | `75.0` | `artist.scores.media_score` |
| `argo:network_score` | `float` | `number` | 필수 | 0-100 | `71.0` | `artist.scores.network_score` |
| `argo:composite_score` | `float` | `number` | 필수 | 0-100 | `74.15` | `artist.scores.composite_score` |
| `argo:composite_confidence` | `Optional[float]` | `number` | 선택 | 0-1 | `0.92` | - |
| `argo:structuralist_analysis` | `Optional[dict]` | `object` | 선택 | - | 아래 참조 | `artist.structuralist_analysis` |
| `argo:coordinates_3d` | `dict` | `object` | 필수 | - | 아래 참조 | `artist.coordinates_3d` |
| `argo:cluster` | `Optional[dict]` | `object` | 선택 | - | 아래 참조 | - |
| `collaborators` | `Optional[List[str]]` | `array` | 선택 | 하위 호환성 유지 | `["artist_002", "artist_003"]` | `artist.collaborators` |
| `collaborations` | `Optional[List[dict]]` | `array` | 선택 | Collaboration 객체 배열 | 아래 참조 | `artist.collaborations` |
| `institutions` | `Optional[List[dict]]` | `array` | 선택 | Institution 객체 배열 | 아래 참조 | `artist.institutions` |
| `exhibitions` | `Optional[List[dict]]` | `array` | 선택 | Exhibition 객체 배열 | 아래 참조 | `artist.exhibitions` |

**중요 사항:**
- `@context`, `@type`, `@id`는 JSON-LD 필수 필드입니다. 반드시 포함해야 합니다.
- `argo:` 네임스페이스는 ARGO 커스텀 필드에 사용됩니다.
- `birthDate`는 문자열 형식 (YYYY)이며, 프론트엔드에서는 `birth_year` (number)로 변환됩니다.
- **관계 데이터 필드**: `collaborations`, `institutions`, `exhibitions`는 프론트엔드에서 연결선 시각화에 사용됩니다.
- **하위 호환성**: `collaborators` 배열도 지원하되, `collaborations` 배열을 우선 사용합니다.

**argo:scores 객체 구조:**
```python
{
    "argo:inst_score": float,      # 0-100
    "argo:acad_score": float,      # 0-100
    "argo:media_score": float,     # 0-100
    "argo:network_score": float,   # 0-100
    "argo:composite_score": float, # 0-100
    "argo:composite_confidence": Optional[float]  # 0-1
}
```

**argo:structuralist_analysis 객체 구조:**
```python
{
    "dominant_capital": str,  # enum: "institutional" | "academic" | "media" | "network"
    "capital_composition": {
        "institutional_ratio": float,  # 0-1
        "academic_ratio": float,       # 0-1
        "media_ratio": float,          # 0-1
        "network_ratio": float         # 0-1
    },
    "structural_position": {
        "field_quadrant": str,  # enum: "Q1_established" | "Q2_academic_elite" | "Q3_media_star" | "Q4_emerging"
        "position_stability": float,    # 0-1
        "mobility_potential": float     # 0-1
    },
    "algorithm_version": str,
    "weights_applied": {
        "inst": float,
        "acad": float,
        "media": float,
        "network": float
    },
    "theoretical_basis": str
}
```

**argo:coordinates_3d 객체 구조:**

**중요**: 이 필드는 프론트엔드에서 3D 갤럭시 렌더링에 필수입니다. 반드시 포함해야 합니다.

```python
{
    "argo:x": float,        # inst_score 정규화 (-30 ~ 30)
    "argo:y": float,        # acad_score 정규화 (-30 ~ 30)
    "argo:z": float,        # media_score 정규화 (-30 ~ 30)
    "argo:radius": float,   # network_score 기반 (10 + score/5)
    "computed_at": Optional[str],  # ISO 8601 형식
    "algorithm": Optional[str]      # "normalize_v1" 등
}
```

**collaborations 배열 구조:**
```python
[
    {
        "artist_id": str,    # 협력 작가 ID
        "strength": float    # 관계 강도 (0-1 범위, 0.3 이상만 프론트엔드에서 표시)
    }
]
```

**중요**: `strength` 값이 0.3 미만인 경우 프론트엔드에서 연결선이 표시되지 않습니다.

**institutions 배열 구조:**
```python
[
    {
        "institution_id": str,  # 기관 ID
        "name": str,             # 기관 이름
        "type": Optional[str]    # 기관 타입 (예: "museum")
    }
]
```

**exhibitions 배열 구조:**
```python
[
    {
        "exhibition_id": str,  # 전시 ID
        "name": str,           # 전시 이름
        "year": Optional[int]  # 전시 연도
    }
]
```

#### 4.2.2 Institution 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Institution`
- 데이터베이스 스키마: `ARGO_Final_Schema.md` → 섹션 2.2

**필수 필드:**

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 |
|--------|------------|-----------|----------|--------------|------|
| `@context` | `str` | `string` | 필수 | `"https://schema.org/"` | `"https://schema.org/"` |
| `@type` | `str` | `string` | 필수 | `"Organization"` | `"Organization"` |
| `@id` | `str` | `string` | 필수 | `argo://institution/{inst_id}` | `"argo://institution/inst_001"` |
| `name` | `str` | `string` | 필수 | - | `"국립현대미술관"` |
| `url` | `Optional[str]` | `string` | 선택 | URI 형식 | `"https://www.mmca.go.kr"` |
| `address` | `Optional[dict]` | `object` | 선택 | PostalAddress 타입 | `{"@type": "PostalAddress", "addressLocality": "Seoul"}` |

#### 4.2.3 Exhibition 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Exhibition`
- 데이터베이스 스키마: `ARGO_Final_Schema.md` → 섹션 2.3

**필수 필드:**

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 |
|--------|------------|-----------|----------|--------------|------|
| `@context` | `str` | `string` | 필수 | `"https://schema.org/"` | `"https://schema.org/"` |
| `@type` | `str` | `string` | 필수 | `"Event"` | `"Event"` |
| `@id` | `str` | `string` | 필수 | `argo://exhibition/{exh_id}` | `"argo://exhibition/exh_001"` |
| `name` | `str` | `string` | 필수 | - | `"한국 추상미술의 맥락"` |
| `startDate` | `str` | `string` | 필수 | YYYY-MM-DD 형식 | `"2024-03-15"` |
| `endDate` | `str` | `string` | 필수 | YYYY-MM-DD 형식 | `"2024-06-30"` |
| `location` | `Optional[dict]` | `object` | 선택 | Place 타입 | `{"@type": "Place", "name": "국립현대미술관"}` |

#### 4.2.4 기타 엔터티

Transaction, Cluster, Artwork, NetworkGraph, GalaxySnapshot 엔터티의 상세 스키마는 `ARGO_API_SPECIFICATION.yaml` 파일의 `components/schemas/` 섹션을 참조하세요.

### 4.3 타입 일치성 보장

#### 4.3.1 프론트엔드-백엔드 타입 일치성 가이드

**타입 매핑 테이블:**

| 백엔드 필드 (JSON) | 프론트엔드 필드 (TypeScript) | 변환 필요 여부 |
|-------------------|---------------------------|--------------|
| `birthDate` (string, YYYY) | `birth_year` (number) | ✅ 변환 필요 |
| `alternateName` (string) | `alternativeName` (string) | ✅ 변환 필요 |
| `argo:scores` (object) | `scores` (object) | 네임스페이스 제거 |
| `argo:coordinates_3d` (object) | `coordinates_3d` (object) | 네임스페이스 제거 |
| `collaborations` (array) | `collaborations` (array) | 직접 사용 가능 |

**검증 체크리스트:**
- [ ] 모든 필드명이 snake_case인가?
- [ ] 프론트엔드 타입과 일치하는가?
- [ ] `coordinates_3d` 필드가 모든 Artist 응답에 포함되어 있는가?
- [ ] `collaborations` 배열의 `strength` 값이 0-1 범위 내에 있는가?

### 4.4 JSON-LD 형식 명시

#### 4.4.1 JSON-LD 필수 필드

모든 API 응답은 JSON-LD 형식을 따라야 합니다. 다음 필드는 반드시 포함해야 합니다:

1. **@context**: `"https://schema.org/"`
2. **@type**: Schema.org 타입 (Person, Organization, Event 등)
3. **@id**: `argo://` URI 형식

#### 4.4.2 ARGO 커스텀 필드 네임스페이스

ARGO 프로젝트의 커스텀 필드는 `argo:` 네임스페이스를 사용합니다.

**예제:**
```json
{
  "@context": "https://schema.org/",
  "@type": "Person",
  "@id": "argo://artist/artist_001",
  "name": "작가 A",
  "argo:scores": {
    "argo:inst_score": 82,
    "argo:acad_score": 68,
    "argo:media_score": 75,
    "argo:network_score": 71,
    "argo:composite_score": 74.15
  },
  "argo:coordinates_3d": {
    "argo:x": 2.34,
    "argo:y": -1.23,
    "argo:z": 0.67,
    "argo:radius": 15
  },
  "collaborations": [
    {
      "artist_id": "artist_002",
      "strength": 0.65
    }
  ],
  "institutions": [
    {
      "institution_id": "inst_001",
      "name": "국립현대미술관",
      "type": "museum"
    }
  ],
  "exhibitions": [
    {
      "exhibition_id": "exh_001",
      "name": "한국 추상미술의 맥락",
      "year": 2024
    }
  ]
}
```

#### 4.4.3 관계 데이터의 JSON-LD 표현

관계 데이터(`collaborations`, `institutions`, `exhibitions`)는 JSON-LD 형식에서 일반 배열로 표현됩니다.

**주의사항:**
- 관계 데이터는 `argo:` 네임스페이스를 사용하지 않습니다.
- 프론트엔드에서 직접 사용 가능한 형식으로 제공됩니다.
- `collaborations` 배열의 `strength` 값이 0.3 미만인 경우 프론트엔드에서 연결선이 표시되지 않습니다.

#### 4.4.4 JSON-LD 변환 미들웨어

FastAPI에서 JSON-LD 형식으로 변환하는 미들웨어 예제는 `ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` 섹션 6.4를 참조하세요.

### 4.5 에러 처리 가이드

#### 4.5.1 표준 에러 응답 형식

**에러 응답 구조:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지",
    "details": "상세 정보",
    "timestamp": "2025-12-09T00:00:00Z",
    "request_id": "uuid",
    "documentation": "https://artdrive1208-api-xxx.run.app/docs/errors/ERROR_CODE"
  }
}
```

**HTTP 상태 코드 매핑:**

| 상태 코드 | 에러 코드 예시 | 설명 |
|----------|--------------|------|
| 400 | `BAD_REQUEST`, `VALIDATION_ERROR` | 잘못된 요청 |
| 401 | `UNAUTHORIZED` | 인증 실패 |
| 404 | `NOT_FOUND` | 리소스 없음 |
| 429 | `TOO_MANY_REQUESTS` | 레이트 제한 초과 |
| 500 | `INTERNAL_ERROR`, `DATABASE_ERROR` | 서버 오류 |

**에러 처리 미들웨어:**

에러 처리 미들웨어 구현 예제는 `ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` 섹션 7을 참조하세요.

### 4.6 좌표 계산 로직

#### 4.6.1 좌표 계산 공식

**정규화 함수:**
```python
def normalize_score(
    score: float,
    min_score: float,
    max_score: float,
    target_min: float,
    target_max: float
) -> float:
    """점수를 정규화하여 target 범위로 변환"""
    if max_score == min_score:
        return (target_min + target_max) / 2
    
    normalized = ((score - min_score) / (max_score - min_score)) * (target_max - target_min) + target_min
    return round(normalized, 2)
```

**좌표 계산 함수:**
```python
def calculate_coordinates_3d(
    inst_score: float,
    acad_score: float,
    media_score: float,
    network_score: float
) -> Dict:
    """3D 갤럭시 좌표 계산"""
    x = normalize_score(inst_score, 0, 100, -30, 30)
    y = normalize_score(acad_score, 0, 100, -30, 30)
    z = normalize_score(media_score, 0, 100, -30, 30)
    radius = round(10 + (network_score / 5), 2)
    
    return {
        "argo:x": x,
        "argo:y": y,
        "argo:z": z,
        "argo:radius": radius,
        "computed_at": datetime.utcnow().isoformat() + "Z",
        "algorithm": "normalize_v1"
    }
```

**중요 사항:**
- 모든 Artist 응답에 `coordinates_3d` 필드가 필수로 포함되어야 합니다.
- 좌표 값은 -30 ~ 30 범위 내에 있어야 합니다.
- radius 값은 10 ~ 30 범위 내에 있어야 합니다.

---

## Part IV: 문서 간 참조 관계

### 5.1 다른 문서 스위트와의 관계

#### 5.1.1 프로젝트 명세 문서와의 관계

**BRD (비즈니스 요구사항 문서):**
- 비즈니스 목표와 API 기능의 일치성 확인
- 타겟 사용자와 API 사용 시나리오 일치성 확인

**PRD (제품 요구사항 문서):**
- 기능 요구사항과 API 엔드포인트의 일치성 확인
- 사용자 시나리오와 API 흐름의 일치성 확인

**SRD (소프트웨어 요구사항 명세서):**
- 기능 명세와 API 엔드포인트의 일치성 확인
- KPI 및 성능 목표와 API 성능의 일치성 확인

**TSD (기술 명세서):**
- 기술 스택과 API 구현의 일치성 확인
- 아키텍처 다이어그램과 API 구조의 일치성 확인
- JSON-LD 형식 규칙 일치성 확인

#### 5.1.2 Schema 문서와의 관계

**ARGO_Final_Schema.md:**
- Neo4j 데이터베이스 스키마와 API 응답 스키마의 일치성 확인
- 엔터티 필드 정의와 API 필드 정의의 일치성 확인
- 관계 타입 정의와 API 관계 데이터의 일치성 확인

#### 5.1.3 데이터 수집 방법론과의 관계

**ARGO_DATA_COLLECTION_METHODOLOGY.md:**
- 데이터 수집 파이프라인과 데이터 소스 API의 일치성 확인
- 정규화 및 점수 계산 로직과 API 응답의 일치성 확인

### 5.2 데이터 흐름도

```
외부 데이터 소스 API (Part II)
    ↓
데이터 수집 파이프라인 (ARGO_DATA_COLLECTION_METHODOLOGY.md)
    ↓
정규화 및 점수 계산
    ↓
Neo4j 데이터베이스 (ARGO_Final_Schema.md)
    ↓
백엔드 API (Part I)
    ↓
프론트엔드 (types/argo.ts)
```

**각 단계별 문서 참조:**

1. **데이터 수집 단계**
   - Part II: 데이터 소스 API 명세 참조
   - `ARGO_DATA_COLLECTION_METHODOLOGY.md` 참조

2. **데이터 저장 단계**
   - `ARGO_Final_Schema.md` 참조
   - Neo4j 스키마 정의 확인

3. **API 제공 단계**
   - Part I: 백엔드 API 명세 참조
   - Part III: API 개발 가이드 참조

4. **프론트엔드 연동 단계**
   - Part III: 타입 일치성 보장 가이드 참조
   - `types/argo.ts` 참조

### 5.3 의존성 관계

#### 5.3.1 문서 간 의존성 그래프

```
ARGO_API_COMPLETE_SPECIFICATION.md (이 문서)
    ↓
    ├─→ ARGO_API_SPECIFICATION.yaml (OpenAPI 명세서)
    │
    ├─→ ARGO_Final_Schema.md (데이터베이스 스키마)
    │
    ├─→ ARGO_DATA_COLLECTION_METHODOLOGY.md (데이터 수집 방법론)
    │
    ├─→ ARGO_SRD_Final.md (소프트웨어 요구사항)
    │
    ├─→ ARGO_TSD_Final.md (기술 명세서)
    │
    └─→ types/argo.ts (프론트엔드 타입)
```

#### 5.3.2 업데이트 시 영향 범위

**백엔드 API 변경 시:**
1. `ARGO_API_SPECIFICATION.yaml` 업데이트 필요
2. 이 문서의 Part I 업데이트 필요
3. Part III의 API 스키마 상세 정의 업데이트 필요
4. `types/argo.ts` 업데이트 필요 (프론트엔드 타입)

**데이터 소스 API 추가 시:**
1. 이 문서의 Part II 업데이트 필요
2. `ARGO_DATA_COLLECTION_METHODOLOGY.md` 업데이트 필요
3. Collector 구현 파일 추가 필요

**스키마 변경 시:**
1. `ARGO_Final_Schema.md` 업데이트 필요
2. 이 문서의 Part III API 스키마 상세 정의 업데이트 필요
3. `ARGO_API_SPECIFICATION.yaml` 스키마 섹션 업데이트 필요

---

## 부록

### 6.1 OpenAPI 명세서

**파일 위치:** `docs/ARGO_API_SPECIFICATION.yaml`

**사용 방법:**
- Swagger UI: `https://editor.swagger.io/` 에서 YAML 파일 업로드
- FastAPI 자동 문서: `/docs` 엔드포인트에서 확인
- 코드 생성: OpenAPI Generator 사용

### 6.2 버전 히스토리

**버전 1.0 (2025-12-09)**
- API 관련 문서 통합 완료
- 백엔드 API 34개 엔드포인트 명세 통합
- 데이터 소스 API 9개 명세 통합
- API 개발 가이드 통합

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 개발팀  
**다음 검토 예정일**: 새 API 추가 시 또는 주요 변경 시







