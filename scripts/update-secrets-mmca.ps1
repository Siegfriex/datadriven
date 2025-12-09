# MMCA API 서비스키를 GCP Secret Manager에 업데이트하는 스크립트
# 사용법: .\scripts\update-secrets-mmca.ps1

$PROJECT_ID = "artdrive1208"
$SERVICE_ACCOUNT = "argo-api@${PROJECT_ID}.iam.gserviceaccount.com"

# MMCA 레지던시 API 서비스키
$MMCA_RESIDENCY_KEY = "0cc9c852-cd3b-417c-91b4-15722d964013"
$MMCA_COLLECTION_KEY = "c080ac2b-93ba-4300-af2d-8cc0ff71dda7"

Write-Host "MMCA API 서비스키를 GCP Secret Manager에 업데이트합니다..." -ForegroundColor Green

# MMCA 레지던시 서비스키 시크릿 생성 또는 업데이트
Write-Host "`n1. MMCA_RESIDENCY_SERVICE_KEY 시크릿 처리 중..." -ForegroundColor Yellow
$secretName = "MMCA_RESIDENCY_SERVICE_KEY"

# 시크릿 존재 여부 확인
$secretExists = gcloud secrets describe $secretName --project=$PROJECT_ID 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   기존 시크릿 발견. 새 버전 추가 중..." -ForegroundColor Cyan
    echo $MMCA_RESIDENCY_KEY | gcloud secrets versions add $secretName --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "   새 시크릿 생성 중..." -ForegroundColor Cyan
    echo $MMCA_RESIDENCY_KEY | gcloud secrets create $secretName --data-file=- --project=$PROJECT_ID
}

# 서비스 계정에 접근 권한 부여
Write-Host "   서비스 계정에 접근 권한 부여 중..." -ForegroundColor Cyan
gcloud secrets add-iam-policy-binding $secretName `
    --member="serviceAccount:${SERVICE_ACCOUNT}" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

# MMCA 소장작품 서비스키 시크릿 생성 또는 업데이트
Write-Host "`n2. MMCA_COLLECTION_SERVICE_KEY 시크릿 처리 중..." -ForegroundColor Yellow
$secretName = "MMCA_COLLECTION_SERVICE_KEY"

# 시크릿 존재 여부 확인
$secretExists = gcloud secrets describe $secretName --project=$PROJECT_ID 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   기존 시크릿 발견. 새 버전 추가 중..." -ForegroundColor Cyan
    echo $MMCA_COLLECTION_KEY | gcloud secrets versions add $secretName --data-file=- --project=$PROJECT_ID
} else {
    Write-Host "   새 시크릿 생성 중..." -ForegroundColor Cyan
    echo $MMCA_COLLECTION_KEY | gcloud secrets create $secretName --data-file=- --project=$PROJECT_ID
}

# 서비스 계정에 접근 권한 부여
Write-Host "   서비스 계정에 접근 권한 부여 중..." -ForegroundColor Cyan
gcloud secrets add-iam-policy-binding $secretName `
    --member="serviceAccount:${SERVICE_ACCOUNT}" `
    --role="roles/secretmanager.secretAccessor" `
    --project=$PROJECT_ID

Write-Host "`n✅ MMCA API 서비스키 시크릿 업데이트 완료!" -ForegroundColor Green
Write-Host "`n업데이트된 시크릿:" -ForegroundColor Cyan
Write-Host "  - MMCA_RESIDENCY_SERVICE_KEY" -ForegroundColor White
Write-Host "  - MMCA_COLLECTION_SERVICE_KEY" -ForegroundColor White

Write-Host "`n다음 단계:" -ForegroundColor Yellow
Write-Host "  1. Cloud Run 서비스의 환경변수에 다음을 추가하세요:" -ForegroundColor White
Write-Host "     MMCA_RESIDENCY_SERVICE_KEY (Secret Manager reference)" -ForegroundColor Gray
Write-Host "     MMCA_COLLECTION_SERVICE_KEY (Secret Manager reference)" -ForegroundColor Gray
Write-Host "  2. 또는 Cloud Run 배포 시 자동으로 Secret Manager에서 로드되도록 설정하세요." -ForegroundColor Gray

