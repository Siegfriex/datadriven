# Firebase Functions Gen 2 배포 문제 해결 가이드

**작성일**: 2025-12-09  
**프로젝트 ID**: artdrive1208  
**프로젝트 번호**: 55248184822  
**문제**: Gen 1으로 배포되고, 서비스 계정 권한 오류 발생

---

## 문제 분석

### 현재 발생하는 문제

1. **Gen 1으로 배포됨**: 코드는 Gen 2로 작성했지만 Firebase CLI가 Gen 1으로 배포
2. **잘못된 리전**: `us-central1`에 배포됨 (목표: `asia-northeast3`)
3. **서비스 계정 권한 오류**: Cloud Scheduler API 활성화 시 권한 부족

### 원인

- Firebase CLI가 Gen 2 코드를 자동 감지하지 못함
- Firebase Functions Gen 2 배포에 필요한 서비스 계정 권한 미부여
- Cloud Scheduler API 활성화 권한 부족

---

## 해결 방법

### 1. Firebase Functions Gen 2 배포에 필요한 서비스 계정

Firebase Functions Gen 2 배포 시 다음 서비스 계정들이 자동으로 사용됩니다:

#### 1.1 Cloud Functions Service Agent

**서비스 계정 이메일**: `service-55248184822@gcp-sa-cloudfunctions.iam.gserviceaccount.com`  
**용도**: Cloud Functions (Gen 2) 배포 및 관리

**필요한 IAM 역할**:
- `roles/cloudfunctions.serviceAgent` (자동 부여됨)
- `roles/run.serviceAgent` (Cloud Run 기반이므로 필요)

#### 1.2 Cloud Build Service Account

**서비스 계정 이메일**: `55248184822@cloudbuild.gserviceaccount.com`  
**용도**: Functions 빌드 및 배포

**필요한 IAM 역할**:
- `roles/cloudbuild.builds.builder` (자동 부여됨)
- `roles/run.admin` (Cloud Run 서비스 배포)
- `roles/iam.serviceAccountUser` (서비스 계정 사용)
- `roles/cloudscheduler.admin` (스케줄 함수 배포 시)

#### 1.3 Cloud Scheduler Service Agent

**서비스 계정 이메일**: `service-55248184822@gcp-sa-cloudscheduler.iam.gserviceaccount.com`  
**용도**: 스케줄 함수 (Cloud Scheduler) 관리

**필요한 IAM 역할**:
- `roles/cloudscheduler.serviceAgent` (자동 부여됨)
- `roles/run.invoker` (Cloud Run 함수 호출)

---

## 해결 단계

### 단계 1: 필요한 서비스 계정 권한 부여

#### 방법 A: GCP Console에서 수동 부여 (권장)

1. **GCP Console 접속**
   - https://console.cloud.google.com/iam-admin/iam?project=artdrive1208

2. **Cloud Build Service Account 권한 부여**
   - 서비스 계정: `55248184822@cloudbuild.gserviceaccount.com`
   - 추가할 역할:
     - `Cloud Run Admin` (`roles/run.admin`)
     - `Service Account User` (`roles/iam.serviceAccountUser`)
     - `Cloud Scheduler Admin` (`roles/cloudscheduler.admin`)

3. **Cloud Scheduler Service Agent 권한 확인**
   - 서비스 계정: `service-55248184822@gcp-sa-cloudscheduler.iam.gserviceaccount.com`
   - 확인할 역할:
     - `Cloud Scheduler Service Agent` (`roles/cloudscheduler.serviceAgent`)
     - `Cloud Run Invoker` (`roles/run.invoker`) - 없으면 추가

#### 방법 B: gcloud CLI로 자동 부여

```powershell
# 프로젝트 번호
$PROJECT_NUMBER = "55248184822"
$PROJECT_ID = "artdrive1208"

# Cloud Build Service Account에 권한 부여
$BUILD_SA = "${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$BUILD_SA" `
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$BUILD_SA" `
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$BUILD_SA" `
    --role="roles/cloudscheduler.admin"

# Cloud Scheduler Service Agent에 권한 부여
$SCHEDULER_SA = "service-${PROJECT_NUMBER}@gcp-sa-cloudscheduler.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SCHEDULER_SA" `
    --role="roles/run.invoker"
```

### 단계 2: Firebase CLI Gen 2 인식 문제 해결

#### 방법 A: firebase.json에 Gen 2 명시적 설정 추가

`firebase.json` 파일을 다음과 같이 수정:

```json
{
  "functions": {
    "source": "functions",
    "runtime": "nodejs20",
    "codebase": "default",
    "predeploy": [
      "npm --prefix \"$RESOURCE_DIR\" run build"
    ]
  }
}
```

**참고**: Firebase CLI v14.27.0은 Gen 2를 자동 감지해야 하지만, 명시적 설정이 도움이 될 수 있습니다.

#### 방법 B: Firebase CLI 업데이트

```powershell
npm install -g firebase-tools@latest
firebase --version  # 최신 버전 확인
```

### 단계 3: 코드 확인

`functions/src/index.ts`가 Gen 2로 작성되었는지 확인:

```typescript
import * as functions from 'firebase-functions/v2';  // ✅ v2 import
// import * as functions from 'firebase-functions';  // ❌ Gen 1

const region = 'asia-northeast3';  // ✅ 리전 명시

export const apiProxy = functions.https.onRequest(
  { region, cors: true },  // ✅ Gen 2 옵션 객체
  async (req, res) => { ... }
);
```

### 단계 4: 배포 재시도

권한 부여 후 배포 재시도:

```powershell
firebase deploy --only functions
```

---

## 서비스 계정 권한 요약

### Cloud Build Service Account (`55248184822@cloudbuild.gserviceaccount.com`)

| 역할 | 권한 범위 | 용도 |
|------|----------|------|
| `roles/cloudbuild.builds.builder` | Cloud Build | 빌드 실행 (자동 부여) |
| `roles/run.admin` | Cloud Run | Gen 2 Functions 배포 |
| `roles/iam.serviceAccountUser` | IAM | 서비스 계정 사용 |
| `roles/cloudscheduler.admin` | Cloud Scheduler | 스케줄 함수 생성 |

### Cloud Scheduler Service Agent (`service-55248184822@gcp-sa-cloudscheduler.iam.gserviceaccount.com`)

| 역할 | 권한 범위 | 용도 |
|------|----------|------|
| `roles/cloudscheduler.serviceAgent` | Cloud Scheduler | 스케줄 관리 (자동 부여) |
| `roles/run.invoker` | Cloud Run | Gen 2 함수 호출 |

### Cloud Functions Service Agent (`service-55248184822@gcp-sa-cloudfunctions.iam.gserviceaccount.com`)

| 역할 | 권한 범위 | 용도 |
|------|----------|------|
| `roles/cloudfunctions.serviceAgent` | Cloud Functions | Functions 관리 (자동 부여) |
| `roles/run.serviceAgent` | Cloud Run | Gen 2 Functions 실행 (자동 부여) |

---

## 권한 부여 스크립트

다음 PowerShell 스크립트를 실행하여 필요한 권한을 자동으로 부여할 수 있습니다:

**파일**: `scripts/grant-firebase-functions-permissions.ps1`

```powershell
# Firebase Functions Gen 2 배포 권한 부여 스크립트
# Created: 2025-12-09
# Project: artdrive1208

$PROJECT_ID = "artdrive1208"
$PROJECT_NUMBER = "55248184822"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firebase Functions Gen 2 Permissions" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "Project Number: $PROJECT_NUMBER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cloud Build Service Account
$BUILD_SA = "${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
Write-Host "[1/2] Granting permissions to Cloud Build Service Account..." -ForegroundColor Yellow
Write-Host "  Service Account: $BUILD_SA" -ForegroundColor Gray

$buildRoles = @(
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/cloudscheduler.admin"
)

foreach ($role in $buildRoles) {
    Write-Host "    Granting: $role" -ForegroundColor Gray -NoNewline
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$BUILD_SA" `
        --role=$role `
        --condition=None 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " - OK" -ForegroundColor Green
    } else {
        Write-Host " - Failed" -ForegroundColor Red
    }
}

Write-Host ""

# Cloud Scheduler Service Agent
$SCHEDULER_SA = "service-${PROJECT_NUMBER}@gcp-sa-cloudscheduler.iam.gserviceaccount.com"
Write-Host "[2/2] Granting permissions to Cloud Scheduler Service Agent..." -ForegroundColor Yellow
Write-Host "  Service Account: $SCHEDULER_SA" -ForegroundColor Gray

Write-Host "    Granting: roles/run.invoker" -ForegroundColor Gray -NoNewline
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SCHEDULER_SA" `
    --role="roles/run.invoker" `
    --condition=None 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host " - OK" -ForegroundColor Green
} else {
    Write-Host " - Failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Permission Grant Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify permissions in GCP Console" -ForegroundColor Gray
Write-Host "  2. Run: firebase deploy --only functions" -ForegroundColor Gray
Write-Host ""
```

---

## 배포 검증

권한 부여 후 배포가 성공하면 다음 명령어로 확인:

```powershell
# Functions 목록 확인 (Gen 2로 표시되어야 함)
firebase functions:list

# 리전 확인 (asia-northeast3로 배포되었는지)
gcloud functions list --region=asia-northeast3 --gen2

# Cloud Scheduler 작업 확인
gcloud scheduler jobs list --location=asia-northeast3
```

---

## 문제 해결 체크리스트

- [ ] Cloud Build Service Account에 `roles/run.admin` 부여
- [ ] Cloud Build Service Account에 `roles/iam.serviceAccountUser` 부여
- [ ] Cloud Build Service Account에 `roles/cloudscheduler.admin` 부여
- [ ] Cloud Scheduler Service Agent에 `roles/run.invoker` 부여
- [ ] Firebase CLI 최신 버전 확인
- [ ] `functions/src/index.ts`가 Gen 2 API 사용 확인
- [ ] `firebase.json` 설정 확인
- [ ] 배포 재시도 및 검증

---

## 참고 문서

- [Firebase Functions Gen 2 문서](https://firebase.google.com/docs/functions/2nd-gen)
- [Cloud Functions Service Agent](https://cloud.google.com/functions/docs/concepts/iam#service_accounts)
- [Cloud Build Service Account](https://cloud.google.com/build/docs/iam/service-account-permissions)
- [Cloud Scheduler IAM](https://cloud.google.com/scheduler/docs/iam)

---

**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 인프라 팀

