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

