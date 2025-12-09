# ARGO GCP 인프라 설정 가이드

**작성일**: 2025-12-09  
**프로젝트 ID**: artdrive1208  
**리전**: asia-northeast3 (서울)  
**상태**: 인프라 설정 준비

---

## 1. 전체 API 엔드포인트 목록 (31개)

### 1.1 작가 API (9개)

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 1 | GET | `/api/artists` | 모든 작가 조회 (페이지네이션, 필터) |
| 2 | GET | `/api/artists/{artist_id}` | 작가 상세 정보 조회 |
| 3 | GET | `/api/artists/{artist_id}/network` | 작가 네트워크 그래프 조회 |
| 4 | GET | `/api/artists/{artist_id}/exhibitions` | 작가 전시 목록 조회 |
| 5 | GET | `/api/artists/{artist_id}/artworks` | 작가 작품 목록 조회 |
| 6 | GET | `/api/artists/{artist_id}/structural-equivalents` | 구조적 등가성 작가 조회 |
| 7 | GET | `/api/artists/{artist_id}/capital-composition` | 자본 구성 분석 조회 |
| 8 | GET | `/api/artists/{artist_id}/market` | 작가 시장 정보 조회 |
| 9 | POST | `/api/artists/search` | 작가 전문 검색 |

### 1.2 기관 API (5개)

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 10 | GET | `/api/institutions` | 모든 기관 조회 |
| 11 | GET | `/api/institutions/{inst_id}` | 기관 상세 정보 조회 |
| 12 | GET | `/api/institutions/{inst_id}/affiliated-artists` | 기관 소속 미술가 목록 조회 |
| 13 | GET | `/api/institutions/{inst_id}/exhibitions` | 기관 전시 목록 조회 |
| 14 | GET | `/api/institutions/{inst_id}/benchmarking` | 기관 벤치마킹 조회 |

### 1.3 전시 API (2개)

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 15 | GET | `/api/exhibitions` | 모든 전시 조회 |
| 16 | GET | `/api/exhibitions/{exh_id}` | 전시 상세 정보 조회 |

### 1.4 거래 API (3개)

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 17 | GET | `/api/transactions` | 모든 거래 조회 |
| 18 | GET | `/api/transactions/{trans_id}` | 거래 상세 정보 조회 |
| 19 | GET | `/api/transactions/price-history/{artist_id}` | 작가 거래 가격 히스토리 조회 |

### 1.5 군집 API (2개)

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 20 | GET | `/api/clusters` | 모든 군집 조회 |
| 21 | GET | `/api/clusters/{cluster_id}` | 군집 상세 정보 조회 |

### 1.6 분석 API (5개)

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 22 | POST | `/api/analysis/centrality` | 중심성 계산 (Degree, Betweenness, Eigenvector) |
| 23 | POST | `/api/analysis/community-detection` | 커뮤니티 탐지 (Louvain 알고리즘) |
| 24 | GET | `/api/analysis/correlation` | 상관관계 분석 |
| 25 | POST | `/api/analysis/compare` | 작가 비교 분석 |
| 26 | GET | `/api/analysis/field-quadrants` | 필드 분면 분류 조회 |

### 1.7 이상치 탐지 API (2개) - Gemini 3 Pro Preview 사용

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 27 | GET | `/api/anomalies` | 이상치 목록 조회 (LLM 가설 생성) |
| 28 | POST | `/api/anomalies/analyze` | 이상치 재분석 (LLM 가설 생성) |

### 1.8 검색 API (1개)

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 29 | GET | `/api/search` | 통합 검색 (작가, 기관, 전시) |

### 1.9 갤럭시 및 메타데이터 API (2개)

| # | Method | 엔드포인트 | 설명 |
|---|--------|-----------|------|
| 30 | GET | `/api/galaxy-snapshot` | 갤럭시 스냅샷 조회 |
| 31 | GET | `/api/metadata/sources` | 데이터 출처 조회 |

---

## 2. GCP 서비스 및 활성화 필요한 API 목록

### 2.1 필수 GCP 서비스 및 API

#### A. Firebase 서비스 (프론트엔드)

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| Firebase Hosting | Firebase Hosting API | `firebasehosting.googleapis.com` | 프론트엔드 배포 |
| Firebase Storage | Firebase Storage API | `firebasestorage.googleapis.com` | 정적 자산 저장 |
| Firebase Analytics | Firebase Analytics API | `firebaseanalytics.googleapis.com` | 사용자 분석 |
| Firebase Authentication | Identity Toolkit API | `identitytoolkit.googleapis.com` | 사용자 인증 (향후) |

#### B. Cloud Run (백엔드 API)

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| Cloud Run | Cloud Run Admin API | `run.googleapis.com` | 서버리스 컨테이너 배포 |
| Cloud Run | Cloud Run API | `run.googleapis.com` | API 엔드포인트 관리 |

#### C. Cloud Memorystore (Redis 캐싱)

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| Cloud Memorystore | Redis API | `redis.googleapis.com` | Redis 인스턴스 관리 |

#### D. 네트워킹

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| VPC Access | Serverless VPC Access API | `vpcaccess.googleapis.com` | Cloud Run과 Memorystore 연결 |
| Service Networking | Service Networking API | `servicenetworking.googleapis.com` | VPC 피어링 |
| Cloud CDN | Cloud CDN API | `cloudcdn.googleapis.com` | 콘텐츠 전송 네트워크 (Firebase Hosting 자동 포함) |

#### E. 보안 및 관리

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| Secret Manager | Secret Manager API | `secretmanager.googleapis.com` | 환경변수 관리 (GEMINI_API_KEY 등) |
| Cloud IAM | Identity and Access Management API | `iam.googleapis.com` | 리소스 접근 제어 |
| Cloud Resource Manager | Cloud Resource Manager API | `cloudresourcemanager.googleapis.com` | 프로젝트 관리 |

#### F. 모니터링 및 로깅

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| Cloud Monitoring | Cloud Monitoring API | `monitoring.googleapis.com` | 메트릭 수집 및 알림 |
| Cloud Logging | Cloud Logging API | `logging.googleapis.com` | 로그 수집 및 분석 |
| Error Reporting | Error Reporting API | `clouderrorreporting.googleapis.com` | 에러 추적 |

#### G. 컴퓨팅 리소스

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| Compute Engine | Compute Engine API | `compute.googleapis.com` | VPC 네트워크 생성 (필요시) |
| Cloud Build | Cloud Build API | `cloudbuild.googleapis.com` | CI/CD 파이프라인 (선택사항) |

### 2.2 선택적 GCP 서비스 및 API

#### H. 보안 강화 (선택사항)

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| Cloud Armor | Cloud Armor API | `compute.googleapis.com` | WAF (웹 애플리케이션 방화벽) |

#### I. AI/ML 서비스 (향후 확장)

| 서비스 | API 이름 | API ID | 용도 |
|--------|---------|--------|------|
| Vertex AI | Vertex AI API | `aiplatform.googleapis.com` | ML 모델 배포 (향후) |
| Generative AI | Generative Language API | `generativelanguage.googleapis.com` | Gemini API (현재는 외부 API 사용) |

---

## 3. GCP API 활성화 명령어

### 3.1 PowerShell 스크립트로 일괄 활성화 (권장)

**Windows 환경에서 사용:**

```powershell
# 스크립트 실행 (관리자 권한 불필요)
.\scripts\enable-gcp-apis.ps1
```

**스크립트 기능:**
- 프로젝트 자동 설정 확인
- 모든 필수 API 일괄 활성화
- 진행 상황 실시간 표시
- 성공/실패 요약 출력
- 이미 활성화된 API 자동 감지

**활성화 상태 확인:**

```powershell
# 활성화 상태 확인 스크립트
.\scripts\verify-gcp-apis.ps1
```

### 3.2 수동 활성화 (Bash/Linux/Mac)

```bash
# 프로젝트 설정
export PROJECT_ID="artdrive1208"
gcloud config set project $PROJECT_ID

# Firebase 서비스
gcloud services enable firebasehosting.googleapis.com
gcloud services enable firebasestorage.googleapis.com
gcloud services enable firebaseanalytics.googleapis.com
gcloud services enable identitytoolkit.googleapis.com

# Cloud Run
gcloud services enable run.googleapis.com

# Cloud Memorystore (Redis)
gcloud services enable redis.googleapis.com

# 네트워킹
gcloud services enable vpcaccess.googleapis.com
gcloud services enable servicenetworking.googleapis.com
gcloud services enable cloudcdn.googleapis.com

# 보안 및 관리
gcloud services enable secretmanager.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# 모니터링 및 로깅
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable clouderrorreporting.googleapis.com

# 컴퓨팅 리소스
gcloud services enable compute.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3.3 선택적 API 활성화

```bash
# Cloud Armor (WAF)
gcloud services enable compute.googleapis.com  # 이미 활성화되어 있으면 생략

# Vertex AI (향후 확장)
gcloud services enable aiplatform.googleapis.com
```

### 3.4 API 활성화 확인

```bash
# 활성화된 API 목록 확인
gcloud services list --enabled --project=$PROJECT_ID

# 특정 API 활성화 상태 확인
gcloud services list --enabled --filter="name:run.googleapis.com" --project=$PROJECT_ID
```

---

## 4. 인프라 구성 계층

### 4.1 계층별 서비스 매핑

```
┌─────────────────────────────────────────┐
│ Layer 1: 프론트엔드 (Presentation)      │
│ - Firebase Hosting                      │
│ - Cloud CDN (자동 포함)                 │
│ - Firebase Storage                      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Layer 2: 백엔드 API (Business Logic)    │
│ - Cloud Run (FastAPI)                   │
│ - Secret Manager (환경변수)            │
│ - Cloud IAM (인증/권한)                 │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Layer 3: 캐싱 (Caching)                 │
│ - Cloud Memorystore (Redis)             │
│ - VPC Access (연결)                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Layer 4: 데이터베이스 (Data Layer)      │
│ - Neo4j Aura (외부 서비스)              │
│ - 연결만 관리                            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Layer 5: 모니터링 (Observability)       │
│ - Cloud Monitoring                      │
│ - Cloud Logging                         │
│ - Error Reporting                       │
└─────────────────────────────────────────┘
```

### 4.2 네트워크 아키텍처

```
Internet
    ↓
Cloud CDN (Firebase Hosting 자동 포함)
    ↓
Firebase Hosting (프론트엔드)
    ↓
Cloud Run (백엔드 API)
    ├─ VPC Access Connector
    │   ↓
    │   Cloud Memorystore (Redis)
    │
    └─ Internet (HTTPS)
        ↓
        Neo4j Aura (외부 서비스)
```

---

## 5. 리소스 사양

### 5.1 Cloud Run 사양

| 항목 | Phase 1 | Phase 2 | 비고 |
|------|---------|---------|------|
| CPU | 1 vCPU | 2 vCPU | |
| Memory | 1GB | 2GB | |
| 최대 인스턴스 수 | 10 | 100 | 자동 스케일링 |
| 최소 인스턴스 수 | 0 | 1 | 콜드 스타트 방지 |
| 타임아웃 | 300초 | 300초 | |
| 동시성 | 80 | 80 | 요청당 인스턴스 |

### 5.2 Cloud Memorystore (Redis) 사양

| 항목 | Phase 1 | Phase 2 | 비고 |
|------|---------|---------|------|
| 인스턴스 크기 | Basic (1GB) | Standard (5GB) | |
| 리전 | asia-northeast3 | asia-northeast3 | |
| 네트워크 | VPC | VPC | VPC Access Connector 필요 |

### 5.3 Firebase Hosting 사양

| 항목 | 사양 | 비고 |
|------|------|------|
| 스토리지 | 10GB (무료 티어) | |
| 전송량 | 360MB/일 (무료 티어) | |
| Cloud CDN | 자동 포함 | |

---

## 6. 환경변수 관리 (Secret Manager)

### 6.1 저장할 시크릿 목록

| 시크릿 이름 | 용도 | 접근 권한 |
|------------|------|-----------|
| `GEMINI_API_KEY` | Gemini 3 Pro Preview API 키 | Cloud Run 서비스 계정 |
| `NEO4J_URI` | Neo4j Aura 연결 URI | Cloud Run 서비스 계정 |
| `NEO4J_USER` | Neo4j 사용자명 | Cloud Run 서비스 계정 |
| `NEO4J_PASSWORD` | Neo4j 비밀번호 | Cloud Run 서비스 계정 |
| `REDIS_HOST` | Cloud Memorystore 호스트 | Cloud Run 서비스 계정 |
| `REDIS_PORT` | Cloud Memorystore 포트 | Cloud Run 서비스 계정 |

### 6.2 Secret Manager 설정 명령어

```bash
# 시크릿 생성
gcloud secrets create GEMINI_API_KEY --data-file=- <<< "your-api-key-here"
gcloud secrets create NEO4J_URI --data-file=- <<< "neo4j+s://your-instance.databases.neo4j.io"
gcloud secrets create NEO4J_USER --data-file=- <<< "neo4j"
gcloud secrets create NEO4J_PASSWORD --data-file=- <<< "your-password-here"

# Cloud Run 서비스 계정에 시크릿 접근 권한 부여
export SERVICE_ACCOUNT="argo-api@artdrive1208.iam.gserviceaccount.com"
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
```

---

## 7. 서비스 계정 및 IAM 설정

### 7.1 필수 서비스 계정

**서비스 계정 네이밍 규칙**: `argo-{purpose}@artdrive1208.iam.gserviceaccount.com`

| 서비스 계정 ID | 전체 이메일 | 용도 |
|---------------|------------|------|
| `argo-api` | `argo-api@artdrive1208.iam.gserviceaccount.com` | Cloud Run 백엔드 API 실행 |
| `argo-build` | `argo-build@artdrive1208.iam.gserviceaccount.com` | Cloud Build CI/CD (선택적) |

**상세 정보**: [ARGO_SERVICE_ACCOUNTS.md](ARGO_SERVICE_ACCOUNTS.md) 참조

### 7.2 서비스 계정 생성

```powershell
# PowerShell 스크립트로 생성
.\scripts\create-service-accounts.ps1

# 확인
.\scripts\verify-service-accounts.ps1
```

---

## 8. 다음 단계

1. ✅ **API 활성화**: 위의 필수 API 활성화 명령어 실행
2. ✅ **서비스 계정 생성**: `.\scripts\create-service-accounts.ps1` 실행
3. ⏳ **VPC 네트워크 생성**: Cloud Memorystore를 위한 VPC 네트워크 설정
4. ⏳ **VPC Access Connector 생성**: Cloud Run과 Memorystore 연결
5. ⏳ **Cloud Memorystore 인스턴스 생성**: Redis 인스턴스 생성
6. ⏳ **Secret Manager 설정**: 환경변수 저장 및 서비스 계정 권한 부여
7. ⏳ **Cloud Run 서비스 배포**: FastAPI 백엔드 배포 (argo-api 서비스 계정 사용)
8. ⏳ **Firebase Hosting 배포**: React 프론트엔드 배포
9. ⏳ **모니터링 설정**: Cloud Monitoring 알림 설정

---

## 8. 참조 문서

- [ARGO_API_SPECIFICATION.yaml](ARGO_API_SPECIFICATION.yaml) - 전체 API 명세서
- [ARGO_TSD_Final.md](ARGO_TSD_Final.md) - 기술 명세서
- [ARGO_SRD_Final.md](ARGO_SRD_Final.md) - 소프트웨어 요구사항 명세서

---

**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 인프라 팀

