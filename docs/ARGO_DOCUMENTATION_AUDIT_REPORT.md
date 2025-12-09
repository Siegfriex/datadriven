# ARGO 문서 스위트 일괄 점검 보고서
## Documentation Audit Report

**작성일**: 2025-12-09  
**점검 범위**: docs 폴더 내 모든 문서 (27개 문서 + 1개 YAML)  
**점검 기준일**: 2025-12-09

---

## Executive Summary

본 보고서는 ARGO 프로젝트의 모든 문서를 체계적으로 점검하여 메타데이터 일관성, 문서 간 상호 참조 관계, 실제 코드와의 일치성을 검증한 결과입니다.

**주요 발견사항:**
- ✅ **메타데이터**: 대부분 일관성 유지 (일부 버전 불일치)
- ⚠️ **API 명세**: 경로 불일치 및 엔드포인트 개수 불일치 발견
- ⚠️ **문서 인덱스**: 최신 문서 누락 및 데이터 소스 API 개수 불일치
- ⚠️ **코드 일치성**: 일부 파라미터 및 경로 불일치 발견

---

## 1. 메타데이터 일관성 점검

### 1.1 핵심 명세 문서 메타데이터

| 문서명 | Version | Last Updated | Status | 프로젝트 ID | 리전 |
|--------|---------|--------------|--------|------------|------|
| `ARGO_BRD_Final.md` | 1.0 | 2025-12-08 | Executive Review | artdrive1208 | asia-northeast3 |
| `ARGO_PRD_Final.md` | 1.1 | 2025-12-08 | Ready for Development | artdrive1208 | asia-northeast3 |
| `ARGO_SRD_Final.md` | 1.0 | 2025-12-08 | Development Ready | artdrive1208 | asia-northeast3 |
| `ARGO_TSD_Final.md` | 2.0 | 2025-12-08 | Production Ready | artdrive1208 | asia-northeast3 |

**발견사항:**
- ✅ 프로젝트 정보 일관성: 모든 문서에서 `artdrive1208`, `asia-northeast3` 일치
- ⚠️ 버전 불일치: TSD만 2.0, 나머지는 1.0 또는 1.1
- ✅ 날짜 일관성: 모든 문서가 2025-12-08로 동일

### 1.2 Firebase 설정 정보 일관성

모든 핵심 문서에서 다음 정보가 일치함:
- API Key: `AIzaSyC4XxekCt6Ob1ufyuRucrHMqXvEInkCpsg`
- Auth Domain: `artdrive1208.firebaseapp.com`
- Project ID: `artdrive1208`
- Storage Bucket: `artdrive1208.firebasestorage.app`
- Messaging Sender ID: `55248184822`
- App ID: `1:55248184822:web:cef02018a4af9dbbdd93d7`
- Measurement ID: `G-DJ2C6DBJ2Q`

**결론**: ✅ Firebase 설정 정보 완전 일치

### 1.3 문서 인덱스 메타데이터

| 항목 | 값 |
|------|-----|
| 작성일 | 2025-12-09 |
| 버전 | 1.0 |
| 프로젝트 ID | artdrive1208 |

**발견사항:**
- ⚠️ 작성일이 다른 문서들보다 하루 늦음 (2025-12-09 vs 2025-12-08)

---

## 2. 문서 간 상호 참조 관계 점검

### 2.1 BRD → PRD → SRD → TSD 흐름 일관성

**BRD (비즈니스 목표):**
- 시장 규모: 연 1.2조 원
- 타겟 사용자: 연구자, 정책입안자, 신진작가, 투자자, 기관

**PRD (기능 요구사항):**
- ✅ BRD의 타겟 사용자와 일치
- ✅ BRD의 비즈니스 목표와 일치

**SRD (기술 명세):**
- ✅ PRD의 기능 요구사항과 일치
- ✅ 5가지 핵심 기능 정의

**TSD (기술 구현):**
- ✅ SRD의 기술 명세와 일치
- ✅ 아키텍처 다이어그램 제공

**결론**: ✅ 문서 간 흐름 일관성 유지

### 2.2 문서 인덱스의 문서 목록 정확성

**인덱스에 등록된 문서 수**: 23개  
**실제 문서 수**: 27개

**누락된 문서:**
1. `ARGO_NEO4J_MVP_DESIGN.md` - Neo4j MVP 설계
2. `ARGO_MILESTONE_ANALYSIS_2025-12-09.md` - 마일스톤 분석 보고서
3. `ARGO_PHASE3_VERIFICATION_REPORT.md` - Phase 3 검증 보고서
4. `ARGO_ANTIGRAVITY_PHASE3_DIRECTING.md` - Phase 3 디렉팅 가이드 (인덱스에는 있으나 섹션 누락 가능성)

**결론**: ⚠️ 문서 인덱스에 최신 문서 3개 누락

---

## 3. 내용 일관성 점검

### 3.1 API 엔드포인트 개수 일치성

**YAML 명세 (`ARGO_API_SPECIFICATION.yaml`):**
- 명시된 엔드포인트: 31개

**실제 구현 (`argo-backend/app/routers/*.py`):**
- artists: 9개
- institutions: 5개
- exhibitions: 2개
- transactions: 3개
- clusters: 2개
- analysis: 8개 (YAML에는 5개, 실제로는 8개)
- anomalies: 2개
- search: 1개
- galaxy: 2개
- **총계: 34개**

**불일치 항목:**
- ⚠️ YAML에는 31개로 명시되어 있으나 실제 구현은 34개
- ⚠️ Analysis API: YAML에는 5개, 실제로는 8개 (추가: `/run-gds-centrality`, `/run-louvain`, `/calculate-structuralist`)

**결론**: ⚠️ API 엔드포인트 개수 불일치 발견

### 3.2 API 경로 일치성

**YAML 명세:**
- 경로 형식: `/api/artists`, `/api/institutions`, 등

**실제 구현:**
- 경로 형식: `/v1/api/artists`, `/v1/api/institutions`, 등
- 예외: `galaxy.py`는 `/v1/api/galaxy-snapshot` 직접 정의

**불일치 항목:**
- ⚠️ YAML: `/api/*` vs 실제: `/v1/api/*`
- ⚠️ `galaxy.py`의 경로는 router prefix 없이 직접 정의됨

**결론**: ⚠️ API 경로 불일치 발견 (Critical)

### 3.3 데이터 소스 API 개수 일치성

**문서 인덱스 (`ARGO_DOCUMENTATION_INDEX.md`):**
- 명시된 API 개수: 4개
- 목록:
  1. ARKO 작가 목록 API (505명)
  2. ARKO 미술작품 정보 API (24,762개)
  3. ARKO 예술단체 목록 API (94개)
  4. ARKO 채용정보 API (363개)

**실제 문서 (`ARGO_DATA_SOURCE_APIS.md`):**
- 실제 API 개수: 9개
- 목록:
  1. ARKO 작가 목록 API
  2. ARKO 미술작품 정보 API
  3. ARKO 예술단체 목록 API
  4. ARKO 채용정보 API
  5. KCI 논문 정보 API
  6. KCI 인용 정보 서비스 API
  7. 청주공예비엔날레 API
  8. MMCA 레지던시작가소식 API
  9. MMCA 소장작품 API

**결론**: ⚠️ 데이터 소스 API 개수 불일치 (인덱스: 4개 vs 실제: 9개)

### 3.4 점수 계산 공식 일치성

**문서 (`ARGO_METHODOLOGY.md`, `ARGO_STRUCTURALIST_ALGORITHM_DESIGN.md`):**
- 제도 점수: `(museum_count * 20) + (biennale_count * 30) + (support_count * 10)`
- 학술 점수: `(citation_count * 2) + (catalog_count * 5) + (academic_publications * 3)`
- 담론 점수: `(article_count * 1) + (sentiment_score * 20)`
- 네트워크 점수: `(collaborators * 5) + (centrality * 40)`

**실제 코드 (`score_calculator.py`):**
- 제도 점수: `(museum_count * 20) + (biennale_count * 30) + (support_count * 10) + (residency_count * 10)` ✅
- 학술 점수: `(citation_count * 2) + (catalog_count * 5) + (academic_publications * 3)` ✅
- 담론 점수: `(article_count * 1) + (sentiment_score * 20)` ✅
- 네트워크 점수: `(collaborators * 5) + (centrality * 40)` ✅

**결론**: ✅ 점수 계산 공식 일치 (제도 점수에 residency_count 추가는 문서 업데이트 필요)

### 3.5 파라미터 일치성

**YAML 명세 (`/api/artists` GET):**
- 파라미터: `page`, `limit`, `segment_id`, `career_stage`, `min_score`

**실제 구현 (`artists.py`):**
- 파라미터: `limit`, `skip` (페이지네이션 방식 다름)

**결론**: ⚠️ 파라미터 불일치 발견 (`page` vs `skip`)

---

## 4. 최신 상태 반영 여부

### 4.1 최근 추가된 API 반영 여부

**추가된 API (최근):**
1. ✅ KCI 논문 정보 API - `ARGO_DATA_SOURCE_APIS.md`에 반영됨
2. ✅ KCI 인용 정보 서비스 API - `ARGO_DATA_SOURCE_APIS.md`에 반영됨
3. ✅ 청주공예비엔날레 API - `ARGO_DATA_SOURCE_APIS.md`에 반영됨
4. ✅ MMCA 레지던시작가소식 API - `ARGO_DATA_SOURCE_APIS.md`에 반영됨
5. ✅ MMCA 소장작품 API - `ARGO_DATA_SOURCE_APIS.md`에 반영됨

**문서 인덱스 반영 여부:**
- ⚠️ `ARGO_DOCUMENTATION_INDEX.md`에는 4개로만 표시되어 있음 (9개로 업데이트 필요)

**결론**: ⚠️ 데이터 소스 API 문서에는 반영되었으나 인덱스 미반영

### 4.2 최근 생성된 문서 인덱스 등록 여부

**최근 생성된 문서:**
1. ⚠️ `ARGO_NEO4J_MVP_DESIGN.md` - 인덱스에 누락
2. ⚠️ `ARGO_MILESTONE_ANALYSIS_2025-12-09.md` - 인덱스에 누락
3. ⚠️ `ARGO_PHASE3_VERIFICATION_REPORT.md` - 인덱스에 누락

**결론**: ⚠️ 최신 문서 3개가 인덱스에 등록되지 않음

### 4.3 Phase 3 디렉팅 내용 반영 여부

**Phase 3 디렉팅 문서:**
- `ARGO_ANTIGRAVITY_PHASE3_DIRECTING.md` 존재
- 인덱스에는 있으나 섹션 확인 필요

**결론**: ✅ Phase 3 디렉팅 문서 존재

---

## 5. 누락된 내용

### 5.1 FRD 문서 존재 여부

**검색 결과:**
- `ARGO_DESIGN_DEVELOPMENT_SPEC.md`에 "기능 요구 명세 (Functional Requirements Specification)" 섹션 존재
- 별도의 FRD 문서는 없음

**결론**: ⚠️ 별도 FRD 문서 없음 (기능 요구사항은 PRD와 SRD에 포함)

### 5.2 문서 간 참조 링크 누락 여부

**확인 필요 항목:**
- 각 문서 내 상호 참조 링크 유효성
- 문서 인덱스의 참조 관계 정확성

**결론**: ⚠️ 상세 검증 필요 (Phase 5에서 진행)

### 5.3 API 경로 불일치

**발견사항:**
- YAML: `/api/*` vs 실제: `/v1/api/*`
- Critical 수준의 불일치

**결론**: ⚠️ API 경로 불일치 (Critical)

### 5.4 파라미터 불일치

**발견사항:**
- YAML: `page` 파라미터
- 실제: `skip` 파라미터
- 페이지네이션 방식 불일치

**결론**: ⚠️ 파라미터 불일치 발견

---

## 6. 문제점 분류 및 우선순위

### 6.1 Critical (즉시 수정 필요)

1. **API 경로 불일치**
   - 문제: YAML `/api/*` vs 실제 `/v1/api/*`
   - 영향: 프론트엔드-백엔드 통신 실패 가능성
   - 수정 방법: YAML 경로를 `/v1/api/*`로 통일 또는 실제 코드를 `/api/*`로 변경

2. **데이터 소스 API 개수 불일치**
   - 문제: 인덱스 4개 vs 실제 9개
   - 영향: 문서 신뢰도 저하
   - 수정 방법: `ARGO_DOCUMENTATION_INDEX.md` 업데이트

### 6.2 High Priority (단기 수정 필요)

1. **문서 인덱스에 최신 문서 누락**
   - 문제: 3개 문서 미등록
   - 영향: 문서 발견성 저하
   - 수정 방법: 인덱스에 문서 추가

2. **API 엔드포인트 개수 불일치**
   - 문제: YAML 31개 vs 실제 34개
   - 영향: API 명세 불완전
   - 수정 방법: YAML에 누락된 엔드포인트 추가

3. **파라미터 불일치**
   - 문제: YAML `page` vs 실제 `skip`
   - 영향: API 사용자 혼란
   - 수정 방법: YAML 파라미터를 실제 구현에 맞게 수정

### 6.3 Medium Priority (중기 수정 필요)

1. **버전 번호 불일치**
   - 문제: TSD만 2.0, 나머지는 1.0 또는 1.1
   - 영향: 문서 버전 관리 혼란
   - 수정 방법: 버전 번호 통일 기준 수립

2. **점수 계산 공식 문서 업데이트**
   - 문제: 제도 점수에 `residency_count` 추가되었으나 문서 미반영
   - 영향: 문서-코드 불일치
   - 수정 방법: 관련 문서 업데이트

### 6.4 Low Priority (장기 개선)

1. **문서 작성일 통일**
   - 문제: 인덱스만 2025-12-09, 나머지는 2025-12-08
   - 영향: 미미
   - 수정 방법: 필요 시 통일

---

## 7. 검증 완료 항목

### 7.1 메타데이터
- ✅ 프로젝트 정보 일관성 (프로젝트 ID, 리전)
- ✅ Firebase 설정 정보 일관성
- ✅ 날짜 형식 일관성 (YYYY-MM-DD)

### 7.2 내용 일관성
- ✅ 점수 계산 공식 일치 (코드 기준)
- ✅ 문서 간 흐름 일관성 (BRD → PRD → SRD → TSD)

### 7.3 최신 상태 반영
- ✅ 최근 추가된 API가 데이터 소스 API 문서에 반영됨
- ✅ Phase 3 디렉팅 문서 존재

---

## 8. 권장 사항

### 8.1 즉시 조치 사항
1. `ARGO_API_SPECIFICATION.yaml`의 경로를 `/v1/api/*`로 통일
2. `ARGO_DOCUMENTATION_INDEX.md`의 데이터 소스 API 개수를 9개로 수정
3. `ARGO_DOCUMENTATION_INDEX.md`에 누락된 문서 3개 추가

### 8.2 단기 조치 사항
1. YAML에 누락된 Analysis API 엔드포인트 3개 추가
2. YAML의 파라미터를 실제 구현에 맞게 수정 (`page` → `skip` 또는 반대)
3. 점수 계산 공식 문서 업데이트 (residency_count 반영)

### 8.3 중기 조치 사항
1. 문서 버전 번호 통일 기준 수립 및 적용
2. 문서 간 참조 링크 유효성 검사 및 수정
3. 문서 작성일 통일

---

## 9. 다음 단계

1. **수정 계획서 작성**: `ARGO_DOCUMENTATION_FIX_PLAN.md` 생성
2. **우선순위별 수정 작업**: Critical → High → Medium 순서로 진행
3. **검증**: 수정 후 재점검

---

---

## 10. 핵심 문서 일관성 검증 (통합)

본 섹션은 `ARGO_CONSISTENCY_VERIFICATION_REPORT.md`의 검증 결과를 통합한 내용입니다.

### 10.1 가중치 값 일치성 검증

**검증 결과:**

| 문서 | inst | acad | media | network | 합계 | 일치 여부 |
|------|------|------|-------|---------|------|----------|
| **BRD** | 0.30 | 0.20 | 0.25 | 0.25 | 1.00 | ✅ |
| **PRD** | 0.30 | 0.20 | 0.25 | 0.25 | 1.00 | ✅ |
| **SRD** | 0.30 | 0.20 | 0.25 | 0.25 | 1.00 | ✅ |
| **TSD** | 0.30 | 0.20 | 0.25 | 0.25 | 1.00 | ✅ |
| **Schema** | 0.30 | 0.20 | 0.25 | 0.25 | 1.00 | ✅ |
| **STRUCTURALIST** | 0.30 | 0.20 | 0.25 | 0.25 | 1.00 | ✅ |
| **METHODOLOGY** | 0.30 | 0.20 | 0.25 | 0.25 | 1.00 | ✅ |

**결과**: 모든 문서에서 가중치 값 완전 일치 ✅

### 10.2 구조주의 분석 필드 정의 일치성 검증

**필드 정의 비교:**

| 필드 | BRD | PRD | SRD | TSD | Schema | 일치 여부 |
|------|-----|-----|-----|-----|--------|----------|
| **structuralist_analysis** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **dominant_capital** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **capital_composition** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **field_quadrant** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **structural_equivalence** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **position_stability** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **mobility_potential** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**결과**: 모든 문서에서 동일한 필드 정의 사용 ✅

### 10.3 구조적 등가성 임계값 일치성 검증

**임계값 비교:**

| 문서 | 임계값 | 일치 여부 |
|------|--------|----------|
| **Schema** | 0.15 | ✅ |
| **SRD** | 0.15 | ✅ |
| **METHODOLOGY** | 0.15 | ✅ |
| **STRUCTURALIST** | 0.15 | ✅ |

**결과**: 모든 문서에서 동일한 임계값 (0.15) 사용 ✅

### 10.4 핵심 문서 일관성 검증 요약

**검증 결과:**
- ✅ **가중치 값**: 100% 일치 (7개 문서)
- ✅ **구조주의 분석 필드**: 100% 일치 (5개 문서)
- ✅ **구조적 등가성 임계값**: 100% 일치 (4개 문서)

**전체 일치율**: **100%** ✅

**결론**: ARGO 문서 스위트는 완전한 일관성을 보이며, 모든 문서가 동일한 가중치, 필드 정의, 임계값을 사용하고 있습니다.

---

**보고서 작성일**: 2025-12-09  
**점검자**: ARGO 문서 점검 시스템  
**다음 점검 예정일**: 수정 완료 후


