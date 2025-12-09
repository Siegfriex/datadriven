# ARGO IAM Roles Grant Script
# Created: 2025-12-09
# Project: artdrive1208

$PROJECT_ID = "artdrive1208"
$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO IAM Roles Grant" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Service Account Emails
$apiSa = "argo-api@${PROJECT_ID}.iam.gserviceaccount.com"
$buildSa = "argo-build@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. ARGO API Service Account Roles
Write-Host "[1/2] Granting IAM roles to argo-api..." -ForegroundColor Yellow
Write-Host "  Service Account: $apiSa" -ForegroundColor Gray
Write-Host ""

$apiRoles = @(
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/errorreporting.writer"
)

$apiSuccessCount = 0
$apiFailCount = 0

foreach ($role in $apiRoles) {
    Write-Host "  Granting: $role" -ForegroundColor Gray -NoNewline
    
    try {
        $result = gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$apiSa" `
            --role=$role `
            --condition=None 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " - Success" -ForegroundColor Green
            $apiSuccessCount++
        } else {
            # Check if role already exists
            if ($result -match "already" -or $result -match "이미") {
                Write-Host " - Already granted" -ForegroundColor Yellow
                $apiSuccessCount++
            } else {
                Write-Host " - Failed" -ForegroundColor Red
                Write-Host "    Error: $result" -ForegroundColor Red
                $apiFailCount++
            }
        }
    } catch {
        Write-Host " - Failed" -ForegroundColor Red
        Write-Host "    Exception: $_" -ForegroundColor Red
        $apiFailCount++
    }
}

Write-Host ""
Write-Host "  Summary: $apiSuccessCount succeeded, $apiFailCount failed" -ForegroundColor $(if ($apiFailCount -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

# 2. ARGO Build Service Account Roles
Write-Host "[2/2] Granting IAM roles to argo-build..." -ForegroundColor Yellow
Write-Host "  Service Account: $buildSa" -ForegroundColor Gray
Write-Host ""

# Check if argo-build exists
$buildExists = gcloud iam service-accounts describe $buildSa --project=$PROJECT_ID 2>&1 | Out-String

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Service account does not exist. Creating..." -ForegroundColor Yellow
    gcloud iam service-accounts create argo-build `
        --display-name="ARGO Build Service Account" `
        --description="Service account for ARGO CI/CD pipeline (Cloud Build)" `
        --project=$PROJECT_ID 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Service account created" -ForegroundColor Green
    } else {
        Write-Host "  Failed to create service account. Skipping..." -ForegroundColor Red
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Final Summary" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  argo-api: $apiSuccessCount / $($apiRoles.Count) roles granted" -ForegroundColor $(if ($apiFailCount -eq 0) { "Green" } else { "Yellow" })
        Write-Host "  argo-build: Skipped (service account not created)" -ForegroundColor Yellow
        exit 0
    }
}

$buildRoles = @(
    "roles/run.admin",
    "roles/storage.admin",
    "roles/secretmanager.secretAccessor",
    "roles/iam.serviceAccountUser",
    "roles/logging.logWriter"
)

$buildSuccessCount = 0
$buildFailCount = 0

foreach ($role in $buildRoles) {
    Write-Host "  Granting: $role" -ForegroundColor Gray -NoNewline
    
    try {
        $result = gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$buildSa" `
            --role=$role `
            --condition=None 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " - Success" -ForegroundColor Green
            $buildSuccessCount++
        } else {
            if ($result -match "already" -or $result -match "이미") {
                Write-Host " - Already granted" -ForegroundColor Yellow
                $buildSuccessCount++
            } else {
                Write-Host " - Failed" -ForegroundColor Red
                Write-Host "    Error: $result" -ForegroundColor Red
                $buildFailCount++
            }
        }
    } catch {
        Write-Host " - Failed" -ForegroundColor Red
        Write-Host "    Exception: $_" -ForegroundColor Red
        $buildFailCount++
    }
}

# Grant permission to use argo-api service account
Write-Host "  Granting permission to use argo-api..." -ForegroundColor Gray -NoNewline

try {
    $result = gcloud iam service-accounts add-iam-policy-binding $apiSa `
        --member="serviceAccount:$buildSa" `
        --role="roles/iam.serviceAccountUser" `
        --project=$PROJECT_ID 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " - Success" -ForegroundColor Green
    } else {
        if ($result -match "already" -or $result -match "이미") {
            Write-Host " - Already granted" -ForegroundColor Yellow
        } else {
            Write-Host " - Failed" -ForegroundColor Yellow
            Write-Host "    Error: $result" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host " - Failed" -ForegroundColor Yellow
    Write-Host "    Exception: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Summary: $buildSuccessCount / $($buildRoles.Count) roles granted" -ForegroundColor $(if ($buildFailCount -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

# Final Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Final Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "argo-api Service Account:" -ForegroundColor Yellow
Write-Host "  Roles granted: $apiSuccessCount / $($apiRoles.Count)" -ForegroundColor $(if ($apiFailCount -eq 0) { "Green" } else { "Yellow" })
Write-Host "  Email: $apiSa" -ForegroundColor Gray
Write-Host ""
Write-Host "argo-build Service Account:" -ForegroundColor Yellow
Write-Host "  Roles granted: $buildSuccessCount / $($buildRoles.Count)" -ForegroundColor $(if ($buildFailCount -eq 0) { "Green" } else { "Yellow" })
Write-Host "  Email: $buildSa" -ForegroundColor Gray
Write-Host ""

if ($apiFailCount -eq 0 -and $buildFailCount -eq 0) {
    Write-Host "All IAM roles have been successfully granted!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some roles failed to grant. Please check the errors above." -ForegroundColor Yellow
    exit 1
}

