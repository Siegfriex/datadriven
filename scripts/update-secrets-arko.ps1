# ARKO API 서비스키를 GCP Secret Manager에 업데이트하는 스크립트
# 사용법: .\scripts\update-secrets-arko.ps1
# 주의: 실제 API 키 값은 .env 파일에서 읽어오거나 수동으로 입력해야 합니다.

$PROJECT_ID = "artdrive1208"
$SERVICE_ACCOUNT = "argo-api@${PROJECT_ID}.iam.gserviceaccount.com"

Write-Host "ARKO API 서비스키를 GCP Secret Manager에 업데이트합니다..." -ForegroundColor Green
Write-Host "주의: 실제 API 키 값은 .env 파일에서 확인하거나 수동으로 입력해야 합니다." -ForegroundColor Yellow

# .env 파일에서 ARKO 키 읽기 시도
$envFile = "argo-backend\.env"
$arkoApiKey = $null
$arkoServiceKey = $null

if (Test-Path $envFile) {
    Write-Host "`n.env 파일에서 ARKO 키 읽기 시도 중..." -ForegroundColor Cyan
    $envContent = Get-Content $envFile
    
    foreach ($line in $envContent) {
        if ($line -match "^ARKO_API_KEY=(.+)$") {
            $arkoApiKey = $matches[1].Trim()
        }
        if ($line -match "^ARKO_SERVICE_KEY=(.+)$") {
            $arkoServiceKey = $matches[1].Trim()
        }
    }
}

# .env 파일에서 읽지 못한 경우 수동 입력 요청
if (-not $arkoApiKey) {
    Write-Host "`nARKO_API_KEY를 찾을 수 없습니다." -ForegroundColor Yellow
    $arkoApiKey = Read-Host "ARKO_API_KEY를 입력하세요 (또는 Enter로 건너뛰기)"
}

if (-not $arkoServiceKey) {
    Write-Host "`nARKO_SERVICE_KEY를 찾을 수 없습니다." -ForegroundColor Yellow
    $arkoServiceKey = Read-Host "ARKO_SERVICE_KEY를 입력하세요 (또는 Enter로 건너뛰기)"
}

if (-not $arkoApiKey -or -not $arkoServiceKey) {
    Write-Host "`n❌ ARKO API 키가 제공되지 않았습니다. 스크립트를 종료합니다." -ForegroundColor Red
    Write-Host "   .env 파일에 ARKO_API_KEY와 ARKO_SERVICE_KEY를 설정하거나," -ForegroundColor Yellow
    Write-Host "   스크립트 실행 시 수동으로 입력하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ ARKO 키 확인 완료" -ForegroundColor Green
Write-Host "   ARKO_API_KEY: $($arkoApiKey.Substring(0, [Math]::Min(8, $arkoApiKey.Length)))..." -ForegroundColor Gray
Write-Host "   ARKO_SERVICE_KEY: $($arkoServiceKey.Substring(0, [Math]::Min(8, $arkoServiceKey.Length)))..." -ForegroundColor Gray

# ARKO_API_KEY 시크릿 생성 또는 업데이트
Write-Host "`n1. ARKO_API_KEY 시크릿 처리 중..." -ForegroundColor Yellow
$secretName = "ARKO_API_KEY"

# 시크릿 존재 여부 확인
$secretExists = gcloud secrets describe $secretName --project=$PROJECT_ID 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   기존 시크릿 발견. 새 버전 추가 중..." -ForegroundColor Cyan
    echo $arkoApiKey | gcloud secrets versions add $secretName --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "   새 시크릿 생성 중..." -ForegroundColor Cyan
    echo $arkoApiKey | gcloud secrets create $secretName --data-file=- --project=$PROJECT_ID
}

# 서비스 계정에 접근 권한 부여
Write-Host "   서비스 계정에 접근 권한 부여 중..." -ForegroundColor Cyan
gcloud secrets add-iam-policy-binding $secretName `
    --member="serviceAccount:${SERVICE_ACCOUNT}" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

# ARKO_SERVICE_KEY 시크릿 생성 또는 업데이트
Write-Host "`n2. ARKO_SERVICE_KEY 시크릿 처리 중..." -ForegroundColor Yellow
$secretName = "ARKO_SERVICE_KEY"

# 시크릿 존재 여부 확인
$secretExists = gcloud secrets describe $secretName --project=$PROJECT_ID 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   기존 시크릿 발견. 새 버전 추가 중..." -ForegroundColor Cyan
    echo $arkoServiceKey | gcloud secrets versions add $secretName --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "   새 시크릿 생성 중..." -ForegroundColor Cyan
    echo $arkoServiceKey | gcloud secrets create $secretName --data-file=- --project=$PROJECT_ID
}

# 서비스 계정에 접근 권한 부여
Write-Host "   서비스 계정에 접근 권한 부여 중..." -ForegroundColor Cyan
gcloud secrets add-iam-policy-binding $secretName `
    --member="serviceAccount:${SERVICE_ACCOUNT}" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

Write-Host "`n✅ ARKO API 서비스키 시크릿 업데이트 완료!" -ForegroundColor Green
Write-Host "`n업데이트된 시크릿:" -ForegroundColor Cyan
Write-Host "  - ARKO_API_KEY" -ForegroundColor White
Write-Host "  - ARKO_SERVICE_KEY" -ForegroundColor White

Write-Host "`n다음 단계:" -ForegroundColor Yellow
Write-Host "  1. Cloud Run 서비스의 환경변수에 다음을 추가하세요:" -ForegroundColor White
Write-Host "     ARKO_API_KEY (Secret Manager reference)" -ForegroundColor Gray
Write-Host "     ARKO_SERVICE_KEY (Secret Manager reference)" -ForegroundColor Gray
Write-Host "  2. 또는 Cloud Run 배포 시 자동으로 Secret Manager에서 로드되도록 설정하세요." -ForegroundColor Gray






