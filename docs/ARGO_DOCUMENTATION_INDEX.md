# ARGO 프로젝트 문서 인덱스
## Documentation Index

**작성일**: 2025-12-09  
**버전**: 1.0  
**프로젝트 ID**: artdrive1208

---

## 문서 구조 개요

ARGO 프로젝트 문서는 다음 3가지 카테고리로 구분됩니다:

1. **프로젝트 명세 문서**: BRD, PRD, SRD, TSD 등
2. **API 명세 문서**: 백엔드 API, 데이터 소스 API
3. **기술 가이드 문서**: 개발 가이드, 방법론, 인프라 설정 등

---

## 1. 프로젝트 명세 문서

### 1.1 비즈니스 문서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_BRD_Final.md` | 비즈니스 요구사항 문서 | ✅ 완료 |
| `ARGO_PRD_Final.md` | 제품 요구사항 문서 | ✅ 완료 |

### 1.2 기술 명세 문서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_SRD_Final.md` | 소프트웨어 요구사항 명세서 | ✅ 완료 |
| `ARGO_TSD_Final.md` | 기술 명세서 | ✅ 완료 |
| `ARGO_Final_Schema.md` | Neo4j 데이터베이스 스키마 | ✅ 완료 |
| `ARGO_NEO4J_MVP_DESIGN.md` | Neo4j MVP 설계 문서 | ✅ 완료 |

### 1.3 알고리즘 및 방법론 문서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_STRUCTURALIST_ALGORITHM_DESIGN.md` | 구조주의 알고리즘 설계 | ✅ 완료 |
| `ARGO_METHODOLOGY.md` | 구조주의 방법론 | ✅ 완료 |
| `ARGO_WEIGHT_RESEARCH_FRAMEWORK.md` | 가중치 연구 프레임워크 | ✅ 완료 |
| `ARGO_DESIGN_DEVELOPMENT_SPEC.md` | 디자인 개발 명세 | ✅ 완료 |

### 1.4 분석 및 검증 문서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_RISK_ANALYSIS_REPORT.md` | 리스크 분석 보고서 | ✅ 완료 |
| `ARGO_DOCUMENTATION_AUDIT_REPORT.md` | 문서 스위트 일괄 점검 보고서 | ✅ 완료 |

---

## 2. API 명세 문서

### 2.1 통합 API 명세서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_API_COMPLETE_SPECIFICATION.md` | ARGO API 통합 명세서 | ✅ 완료 |
| | - 백엔드 API 명세 (Part I) | |
| | - 데이터 소스 API 명세 (Part II) | |
| | - API 개발 가이드 (Part III) | |
| | - 문서 간 참조 관계 (Part IV) | |

**구조:**
- **Part I**: 백엔드 API 명세 (34개 엔드포인트)
- **Part II**: 데이터 소스 API 명세 (9개 API)
- **Part III**: API 개발 가이드 (스키마 정의, 타입 일치성 보장 등)
- **Part IV**: 문서 간 참조 관계 및 의존성

**참조 문서:**
- `ARGO_API_SPECIFICATION.yaml`: OpenAPI 표준 명세서 (Part I에서 참조)
- `ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md`: 백엔드 개발 명세서 (Part III에 통합)

### 2.2 OpenAPI 명세서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_API_SPECIFICATION.yaml` | ARGO 백엔드 API 명세서 (OpenAPI 3.0) | ✅ 완료 |
| | - 프론트엔드-백엔드 간 API 계약 | |
| | - 34개 엔드포인트 정의 | |
| | - JSON-LD 형식 명세 | |
| | - Swagger UI, 코드 생성용 | |

**구분**: ARGO 시스템이 제공하는 API (프론트엔드-백엔드 간)

**참조**: `ARGO_API_COMPLETE_SPECIFICATION.md` Part I에서 상세 설명

---

## 3. 기술 가이드 문서

### 3.1 인프라 설정 문서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_GCP_INFRASTRUCTURE_SETUP.md` | GCP 인프라 설정 가이드 | ✅ 완료 |
| `ARGO_SERVICE_ACCOUNTS.md` | 서비스 계정 정의 | ✅ 완료 |
| `ARGO_FIREBASE_SETUP.md` | Firebase 설정 가이드 | ✅ 완료 |
| `ARGO_FIREBASE_FUNCTIONS_GEN2_DEPLOYMENT.md` | Firebase Functions Gen 2 배포 가이드 | ✅ 완료 |

### 3.2 개발 가이드 문서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` | Antigravity 백엔드 개발 명세서 | ✅ 완료 |

### 3.3 데이터 수집 문서

| 문서명 | 설명 | 상태 |
|--------|------|------|
| `ARGO_DATA_COLLECTION_METHODOLOGY.md` | 데이터 수집 방법론 | ✅ 완료 |
| `ARGO_API_COMPLETE_SPECIFICATION.md` | API 통합 명세서 (Part II: 데이터 소스 API) | ✅ 완료 |

---

## 4. 문서 간 참조 관계

### 4.1 API 명세 문서 관계

```
ARGO_API_COMPLETE_SPECIFICATION.md (통합 API 명세서)
    ├─→ Part I: 백엔드 API 명세
    │   └─→ ARGO_API_SPECIFICATION.yaml (OpenAPI 표준)
    ├─→ Part II: 데이터 소스 API 명세
    │   └─→ ARGO_DATA_COLLECTION_METHODOLOGY.md (수집 방법론)
    └─→ Part III: API 개발 가이드
        └─→ ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md (백엔드 개발 명세)
```

**설명:**
- `ARGO_API_COMPLETE_SPECIFICATION.md`: 모든 API 관련 명세를 통합한 단일 문서
- `ARGO_API_SPECIFICATION.yaml`: OpenAPI 표준 형식의 백엔드 API 명세서 (Part I에서 참조)
- `ARGO_DATA_COLLECTION_METHODOLOGY.md`: 데이터 수집 파이프라인 및 방법론 (Part II에서 참조)

### 4.2 개발 가이드 문서 관계

```
ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md
    ↓ 참조
ARGO_API_SPECIFICATION.yaml
ARGO_Final_Schema.md
types/argo.ts (프론트엔드 타입)
```

**설명:**
- `ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md`: Antigravity IDE를 통한 백엔드 개발의 핵심 명세서 (디렉팅 가이드 포함)

---

## 5. 문서 업데이트 규칙

### 5.1 새 API 추가 시

**데이터 소스 API 추가:**
1. `ARGO_API_COMPLETE_SPECIFICATION.md` Part II 섹션 3.3에 상세 명세 추가
2. Part II 섹션 3.2의 전체 API 목록 업데이트
3. Part II 섹션 3.4의 데이터 활용 인사이트 업데이트
4. Part II 섹션 3.5의 향후 추가 예정 API에서 제거
5. `ARGO_DATA_COLLECTION_METHODOLOGY.md` 참조 업데이트

**백엔드 API 추가:**
1. `ARGO_API_SPECIFICATION.yaml`에 엔드포인트 추가
2. `ARGO_API_COMPLETE_SPECIFICATION.md` Part I 섹션 2.2 엔드포인트 목록 업데이트
3. Part I 섹션 2.3에 상세 명세 추가
4. 버전 업데이트 (필요 시)

### 5.2 문서 버전 관리

- **주요 변경**: 버전 번호 증가 (예: 1.0 → 2.0)
- **소소한 변경**: 최종 업데이트 날짜만 갱신
- **버전 히스토리**: 각 문서의 하단에 기록

---

## 6. 빠른 참조 가이드

### 6.1 백엔드 개발 시

1. `ARGO_API_COMPLETE_SPECIFICATION.md` Part I & Part III - 통합 API 명세서 및 개발 가이드
2. `ARGO_API_SPECIFICATION.yaml` - OpenAPI 표준 명세서 (코드 생성용)
3. `ARGO_Final_Schema.md` - 데이터베이스 스키마
4. `ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` - Antigravity IDE 디렉팅 가이드 (섹션 12)

### 6.2 데이터 수집 시

1. `ARGO_API_COMPLETE_SPECIFICATION.md` Part II - 데이터 소스 API 명세서
2. `ARGO_DATA_COLLECTION_METHODOLOGY.md` - 수집 방법론
3. `data_collection_pipeline.py` - 실제 구현 코드

### 6.3 인프라 설정 시

1. `ARGO_GCP_INFRASTRUCTURE_SETUP.md` - GCP 인프라 설정
2. `ARGO_FIREBASE_SETUP.md` - Firebase 설정
3. `ARGO_SERVICE_ACCOUNTS.md` - 서비스 계정 정의

---

**문서 버전**: 1.2  
**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 개발팀  
**업데이트 내역**: 
- API 관련 문서 통합 완료 (`ARGO_API_COMPLETE_SPECIFICATION.md` 생성)
- 문서 인덱스 업데이트 (통합 문서 반영)

