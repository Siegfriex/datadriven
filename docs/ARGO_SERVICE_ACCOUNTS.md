# ARGO 서비스 계정 및 IAM 역할 정의

**작성일**: 2025-12-09  
**프로젝트 ID**: artdrive1208  
**상태**: 서비스 계정 생성 준비

---

## 1. 필수 서비스 계정 목록

### 1.1 서비스 계정 네이밍 규칙

**규칙**: `argo-{purpose}@{project-id}.iam.gserviceaccount.com`

- **프로젝트 ID**: `artdrive1208`
- **네이밍 패턴**: `argo-{목적}`
- **전체 이메일 형식**: `argo-{목적}@artdrive1208.iam.gserviceaccount.com`

---

## 2. 필수 서비스 계정 상세

### 2.1 ARGO API 서비스 계정 (필수)

**서비스 계정 ID**: `argo-api`  
**전체 이메일**: `argo-api@artdrive1208.iam.gserviceaccount.com`  
**용도**: Cloud Run 백엔드 API 실행

**역할**:
- FastAPI 백엔드 서비스 실행
- Secret Manager에서 환경변수 읽기
- Cloud Memorystore (Redis) 접근
- Cloud Logging에 로그 작성
- Cloud Monitoring에 메트릭 전송
- Neo4j Aura (외부) 연결

**필요한 IAM 역할**:

| 역할 | 권한 범위 | 용도 |
|------|----------|------|
| `roles/secretmanager.secretAccessor` | Secret Manager | 환경변수 읽기 (GEMINI_API_KEY, NEO4J_URI 등) |
| `roles/logging.logWriter` | Cloud Logging | 애플리케이션 로그 작성 |
| `roles/monitoring.metricWriter` | Cloud Monitoring | 메트릭 전송 |
| `roles/cloudtrace.agent` | Cloud Trace | 분산 추적 (선택적) |
| `roles/errorreporting.writer` | Error Reporting | 에러 리포트 작성 |

**VPC 접근**:
- VPC Access Connector를 통해 Cloud Memorystore 접근
- 별도 IAM 역할 불필요 (VPC 네트워크 레벨 접근)

---

### 2.2 ARGO Build 서비스 계정 (선택적, CI/CD용)

**서비스 계정 ID**: `argo-build`  
**전체 이메일**: `argo-build@artdrive1208.iam.gserviceaccount.com`  
**용도**: Cloud Build CI/CD 파이프라인

**역할**:
- Cloud Run 서비스 배포
- Container Registry 이미지 푸시/풀
- Secret Manager 읽기 (배포 시 환경변수 주입)
- Cloud Build 트리거 실행

**필요한 IAM 역할**:

| 역할 | 권한 범위 | 용도 |
|------|----------|------|
| `roles/run.admin` | Cloud Run | 서비스 배포 및 관리 |
| `roles/storage.admin` | Cloud Storage | Container Registry 접근 |
| `roles/secretmanager.secretAccessor` | Secret Manager | 배포 시 시크릿 읽기 |
| `roles/iam.serviceAccountUser` | IAM | Cloud Run 서비스 계정 사용 권한 |
| `roles/logging.logWriter` | Cloud Logging | 빌드 로그 작성 |

**참고**: GitHub Actions를 사용하는 경우 이 서비스 계정은 선택적입니다.

---

### 2.3 Firebase 서비스 계정 (자동 생성)

**서비스 계정**: Firebase가 자동으로 생성  
**용도**: Firebase Hosting 배포

**참고**: Firebase CLI를 사용하여 배포하는 경우, 사용자 계정 권한으로 충분합니다.

---

## 3. 서비스 계정 생성 스크립트

### 3.1 PowerShell 스크립트

**파일**: `scripts/create-service-accounts.ps1`

```powershell
# ARGO 서비스 계정 생성 스크립트
# Created: 2025-12-09
# Project: artdrive1208

$PROJECT_ID = "artdrive1208"
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO Service Account Creation" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. ARGO API 서비스 계정 생성
Write-Host "[1/2] Creating argo-api service account..." -ForegroundColor Yellow
$apiSa = "argo-api@${PROJECT_ID}.iam.gserviceaccount.com"

try {
    # 서비스 계정 생성
    gcloud iam service-accounts create argo-api `
        --display-name="ARGO API Service Account" `
        --description="Service account for ARGO backend API (Cloud Run)" `
        --project=$PROJECT_ID
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Service account created: $apiSa" -ForegroundColor Green
        
        # IAM 역할 부여
        Write-Host "  Granting IAM roles..." -ForegroundColor Gray
        
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$apiSa" `
            --role="roles/secretmanager.secretAccessor" `
            --condition=None
        
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$apiSa" `
            --role="roles/logging.logWriter" `
            --condition=None
        
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$apiSa" `
            --role="roles/monitoring.metricWriter" `
            --condition=None
        
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$apiSa" `
            --role="roles/errorreporting.writer" `
            --condition=None
        
        Write-Host "  IAM roles granted successfully" -ForegroundColor Green
    } else {
        Write-Host "  Service account may already exist" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Error: $_" -ForegroundColor Red
}

Write-Host ""

# 2. ARGO Build 서비스 계정 생성 (선택적)
Write-Host "[2/2] Creating argo-build service account (optional)..." -ForegroundColor Yellow
$buildSa = "argo-build@${PROJECT_ID}.iam.gserviceaccount.com"

try {
    # 서비스 계정 생성
    gcloud iam service-accounts create argo-build `
        --display-name="ARGO Build Service Account" `
        --description="Service account for ARGO CI/CD pipeline (Cloud Build)" `
        --project=$PROJECT_ID
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Service account created: $buildSa" -ForegroundColor Green
        
        # IAM 역할 부여
        Write-Host "  Granting IAM roles..." -ForegroundColor Gray
        
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$buildSa" `
            --role="roles/run.admin" `
            --condition=None
        
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$buildSa" `
            --role="roles/storage.admin" `
            --condition=None
        
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$buildSa" `
            --role="roles/secretmanager.secretAccessor" `
            --condition=None
        
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$buildSa" `
            --role="roles/iam.serviceAccountUser" `
            --condition=None
        
        # argo-api 서비스 계정 사용 권한 부여
        gcloud iam service-accounts add-iam-policy-binding $apiSa `
            --member="serviceAccount:$buildSa" `
            --role="roles/iam.serviceAccountUser" `
            --project=$PROJECT_ID
        
        Write-Host "  IAM roles granted successfully" -ForegroundColor Green
    } else {
        Write-Host "  Service account may already exist" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Account Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created Service Accounts:" -ForegroundColor Yellow
Write-Host "  1. $apiSa" -ForegroundColor Green
Write-Host "  2. $buildSa" -ForegroundColor Green
Write-Host ""
Write-Host "To verify:" -ForegroundColor Yellow
Write-Host "  gcloud iam service-accounts list --project=$PROJECT_ID" -ForegroundColor Gray
Write-Host ""
```

---

## 4. 서비스 계정 확인 스크립트

### 4.1 PowerShell 스크립트

**파일**: `scripts/verify-service-accounts.ps1`

```powershell
# ARGO 서비스 계정 확인 스크립트
# Created: 2025-12-09
# Project: artdrive1208

$PROJECT_ID = "artdrive1208"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO Service Account Verification" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 필수 서비스 계정 목록
$requiredSAs = @(
    "argo-api@${PROJECT_ID}.iam.gserviceaccount.com",
    "argo-build@${PROJECT_ID}.iam.gserviceaccount.com"
)

Write-Host "Checking service accounts..." -ForegroundColor Yellow
Write-Host ""

foreach ($sa in $requiredSAs) {
    Write-Host "  Checking: $sa" -ForegroundColor Gray -NoNewline
    
    try {
        $result = gcloud iam service-accounts describe $sa --project=$PROJECT_ID 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " - Found" -ForegroundColor Green
            
            # IAM 역할 확인
            Write-Host "    Roles:" -ForegroundColor Gray
            $roles = gcloud projects get-iam-policy $PROJECT_ID `
                --flatten="bindings[].members" `
                --filter="bindings.members:$sa" `
                --format="value(bindings.role)" 2>&1
            
            if ($roles) {
                foreach ($role in $roles) {
                    Write-Host "      - $role" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host " - Not found" -ForegroundColor Red
        }
    } catch {
        Write-Host " - Error" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All service accounts:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
gcloud iam service-accounts list --project=$PROJECT_ID --format="table(email,displayName)"
```

---

## 5. IAM 역할 요약

### 5.1 argo-api 서비스 계정 역할

```
roles/secretmanager.secretAccessor    # Secret Manager 접근
roles/logging.logWriter               # Cloud Logging 쓰기
roles/monitoring.metricWriter         # Cloud Monitoring 메트릭
roles/errorreporting.writer           # Error Reporting
```

### 5.2 argo-build 서비스 계정 역할

```
roles/run.admin                       # Cloud Run 배포
roles/storage.admin                   # Container Registry
roles/secretmanager.secretAccessor   # Secret 읽기
roles/iam.serviceAccountUser         # 서비스 계정 사용
roles/logging.logWriter               # 빌드 로그
```

---

## 6. 다음 단계

1. ✅ **서비스 계정 생성**: `.\scripts\create-service-accounts.ps1` 실행
2. ⏳ **서비스 계정 확인**: `.\scripts\verify-service-accounts.ps1` 실행
3. ⏳ **Secret Manager 설정**: 시크릿 생성 및 접근 권한 부여
4. ⏳ **Cloud Run 배포**: 서비스 계정 지정하여 배포

---

**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 인프라 팀

