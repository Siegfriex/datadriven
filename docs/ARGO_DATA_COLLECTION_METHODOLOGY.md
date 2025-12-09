# ARGO 데이터 수집 방법론
## Data Collection Methodology

**작성일**: 2025-12-09  
**버전**: 2.0  
**프로젝트 ID**: artdrive1208  
**상태**: 구현 완료

**참조 문서:**
- `ARGO_DATA_SOURCE_APIS.md`: 데이터 소스 API 상세 명세서 (이 문서와 함께 참조)
- `ARGO_API_SPECIFICATION.yaml`: ARGO 백엔드 API 명세서

---

## 1. 개요

ARGO 프로젝트의 데이터 수집 파이프라인은 **6단계 프로세스**로 구성되어 있습니다:

1. **데이터 수집** (Collection)
2. **데이터 정규화** (Normalization)
3. **점수 계산** (Scoring)
4. **데이터 검증** (Validation)
5. **최종 검증** (Final Validation)
6. **Neo4j 업로드** (Upload)

---

## 2. 데이터 소스

### 2.1 데이터 소스 API 목록

**상세 명세는 `ARGO_DATA_SOURCE_APIS.md` 참조**

현재 연동된 API:
1. **ARKO 작가 목록 API** (505명) - Artist 엔터티 생성
2. **ARKO 미술작품 정보 API** (24,762개) - 작가 제도 점수 계산
3. **ARKO 예술단체 목록 API** (94개) - Institution 엔터티 생성
4. **ARKO 채용정보 API** (363개) - Institution 정보 보강

각 API의 상세 정보, 엔드포인트, 인증 방법, 데이터 필드는 `ARGO_DATA_SOURCE_APIS.md` 섹션 2 참조.

---

## 3. 데이터 수집 파이프라인

### 3.1 파이프라인 실행

```bash
# 기본 실행 (50명 수집)
cd argo-backend
python data_collection_pipeline.py

# 지정된 수량 수집
python data_collection_pipeline.py --count 100

# 테스트 모드 (업로드 없이)
python data_collection_pipeline.py --count 10 --dry-run
```

### 3.2 환경변수 설정

`.env` 파일에 다음을 추가:

```env
# ARKO API (공공데이터포털에서 발급받은 실제 키)
ARKO_API_KEY=4fbb6a075eb8b1f1b3d26fdddd3ce975146d23abda85b147c4f186c24f2e5edf
ARKO_SERVICE_KEY=4fbb6a075eb8b1f1b3d26fdddd3ce975146d23abda85b147c4f186c24f2e5edf

# Neo4j
NEO4J_URI=neo4j+s://be57a318.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Gemini API
GEMINI_API_KEY=your_gemini_key
```

---

## 4. 파이프라인 단계별 상세

### Step 1: 데이터 수집

**수집 항목:** (`ARGO_DATA_SOURCE_APIS.md` 섹션 2 참조)
1. 작가 목록 (ARKO 작가 API) - 505명
2. 작품 정보 (ARKO 작품 API) - 24,762개, 작가 점수 계산에 활용
3. 예술단체 정보 (ARKO 기관 API) - 94개, Institution 엔터티 생성
4. 채용정보 (ARKO 채용정보 API) - 363개, Institution 정보 보강

**출력:**
- 작가 데이터 리스트
- 작품 데이터 리스트 (작가별 그룹화)
- 기관 데이터 리스트
- 채용정보 리스트 (기관별 그룹화)

### Step 2: 데이터 정규화

**작가 데이터 정규화:**
- 이름 표준화 (한글 + 영문)
- segment_id 생성
- identifier 생성
- artist_id 생성

**작품 데이터 정규화:**
- 작가 이름으로 매칭
- 설치일자 파싱
- 지역 정보 파싱 (시/구 분리)

**기관 데이터 정규화:**
- 단체명 표준화
- URL 정규화
- 대표자 정보 추출

### Step 3: 점수 계산

**작가 점수 계산 (작품 정보 활용):**
- 작가별 작품 수 계산
- 건축물 미술작품 설치 = 제도 레이어 활동
- `museum_exhibitions` 필드에 작품 수 반영
- `inst_score` 계산에 활용

**4개 레이어 점수:**
- inst_score: 제도 레이어 (작품 수 기반)
- acad_score: 학술 레이어
- media_score: 담론 레이어
- network_score: 네트워크 레이어

### Step 4-6: 검증 및 업로드

기존과 동일

---

## 5. 실행 예시

### 5.1 개별 API 테스트

```bash
# 작가 API 테스트
python test_arko_api.py

# 작품 API 테스트
python test_artwork_api.py

# 기관 API 테스트
python test_institution_api.py
```

### 5.2 통합 파이프라인 실행

```bash
python data_collection_pipeline.py --count 50 --dry-run
```

**예상 출력:**
```
============================================================
Step 1: 데이터 수집 시작
============================================================
작가 수집 완료: 50명
작품 수집 완료: 1000개
예술단체 수집 완료: 94개

작가별 작품 수 계산 완료: 535명
점수 계산 완료: 50명
...
```

---

## 6. 데이터 활용

**상세 인사이트는 `ARGO_DATA_SOURCE_APIS.md` 섹션 3 참조**

### 6.1 작가-작품 관계

- 작가 이름으로 작품 매칭 (53.5% 성공률, 1000개 샘플 기준)
- 작품 수를 제도 점수에 반영 (`inst_score` 계산)
- 향후: 작품 상세 정보를 Neo4j Artwork 노드로 저장

### 6.2 작가-기관 관계

- 대표자 이름으로 작가-기관 매칭 (정확도 낮음)
- 향후: 작가 소속 정보 별도 수집 필요
- 기관 정보는 Institution 노드로 저장

### 6.3 점수 계산 개선

현재 작품 정보를 활용하여:
- `public_artwork_count`: 공공 미술작품 설치 수
- `museum_exhibitions`: 작품 수를 전시 횟수로 간주 (임시)

향후 개선:
- 실제 전시 정보 수집 (MMCA 크롤링 예정)
- 논문 인용 수집 (KCI API 예정)
- 언론 기사 수집 (웹 크롤링 예정)

---

## 7. 다음 단계

**향후 추가 예정 API는 `ARGO_DATA_SOURCE_APIS.md` 섹션 6 참조**

### 7.1 추가 데이터 소스 구현

1. **MMCA 크롤링** (`app/collectors/mmca_collector.py`) - P1
2. **KCI API** (`app/collectors/kci_collector.py`) - P1
3. **경매사 API** (`app/collectors/auction_collector.py`) - P2

### 7.2 작가-기관 관계 매핑 개선

- 작가 소속 정보 별도 수집
- 퍼지 매칭으로 이름 변형 처리
- 작가 ID 기반 매칭

### 7.3 자동화 스케줄링

Firebase Functions 또는 Cloud Scheduler를 사용하여:
- 주 1회 자동 수집
- 신규 작가 자동 추가
- 점수 자동 재계산

---

## 8. 참조 문서

### 8.1 데이터 소스 API
- **`ARGO_DATA_SOURCE_APIS.md`**: 데이터 소스 API 상세 명세서
  - 모든 외부 API 엔드포인트 및 인증 정보
  - API별 활용 목적 및 데이터 필드
  - 데이터 활용 인사이트

### 8.2 프로젝트 문서
- `ARGO_SRD_Final.md` 섹션 3.2: 데이터 수집 및 정규화 프로세스
- `ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md`: 백엔드 스펙
- `ARGO_Final_Schema.md`: Neo4j 스키마 정의
- `ARGO_API_SPECIFICATION.yaml`: ARGO 백엔드 API 명세서

---

**문서 버전**: 2.0  
**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 개발팀
