# ARGO Service Account Creation Script
# Created: 2025-12-09
# Project: artdrive1208

$PROJECT_ID = "artdrive1208"
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO Service Account Creation" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. ARGO API Service Account
Write-Host "[1/2] Creating argo-api service account..." -ForegroundColor Yellow
$apiSa = "argo-api@${PROJECT_ID}.iam.gserviceaccount.com"

try {
    # Check if service account exists
    $existing = gcloud iam service-accounts describe $apiSa --project=$PROJECT_ID 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Service account already exists: $apiSa" -ForegroundColor Yellow
    } else {
        # Create service account
        gcloud iam service-accounts create argo-api `
            --display-name="ARGO API Service Account" `
            --description="Service account for ARGO backend API (Cloud Run)" `
            --project=$PROJECT_ID
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Service account created: $apiSa" -ForegroundColor Green
        } else {
            Write-Host "  Failed to create service account" -ForegroundColor Red
            exit 1
        }
    }
    
    # Grant IAM roles
    Write-Host "  Granting IAM roles..." -ForegroundColor Gray
    
    $roles = @(
        "roles/secretmanager.secretAccessor",
        "roles/logging.logWriter",
        "roles/monitoring.metricWriter",
        "roles/errorreporting.writer"
    )
    
    foreach ($role in $roles) {
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$apiSa" `
            --role=$role `
            --condition=None 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    Granted: $role" -ForegroundColor Green
        } else {
            Write-Host "    Failed: $role" -ForegroundColor Yellow
        }
    }
    
    Write-Host "  IAM roles granted successfully" -ForegroundColor Green
} catch {
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. ARGO Build Service Account (Optional)
Write-Host "[2/2] Creating argo-build service account (optional)..." -ForegroundColor Yellow
$buildSa = "argo-build@${PROJECT_ID}.iam.gserviceaccount.com"

try {
    # Check if service account exists
    $existing = gcloud iam service-accounts describe $buildSa --project=$PROJECT_ID 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Service account already exists: $buildSa" -ForegroundColor Yellow
    } else {
        # Create service account
        gcloud iam service-accounts create argo-build `
            --display-name="ARGO Build Service Account" `
            --description="Service account for ARGO CI/CD pipeline (Cloud Build)" `
            --project=$PROJECT_ID
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Service account created: $buildSa" -ForegroundColor Green
        } else {
            Write-Host "  Failed to create service account" -ForegroundColor Red
            exit 1
        }
    }
    
    # Grant IAM roles
    Write-Host "  Granting IAM roles..." -ForegroundColor Gray
    
    $roles = @(
        "roles/run.admin",
        "roles/storage.admin",
        "roles/secretmanager.secretAccessor",
        "roles/iam.serviceAccountUser",
        "roles/logging.logWriter"
    )
    
    foreach ($role in $roles) {
        gcloud projects add-iam-policy-binding $PROJECT_ID `
            --member="serviceAccount:$buildSa" `
            --role=$role `
            --condition=None 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    Granted: $role" -ForegroundColor Green
        } else {
            Write-Host "    Failed: $role" -ForegroundColor Yellow
        }
    }
    
    # Grant permission to use argo-api service account
    Write-Host "  Granting permission to use argo-api service account..." -ForegroundColor Gray
    gcloud iam service-accounts add-iam-policy-binding $apiSa `
        --member="serviceAccount:$buildSa" `
        --role="roles/iam.serviceAccountUser" `
        --project=$PROJECT_ID 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    Granted: argo-api usage permission" -ForegroundColor Green
    }
    
    Write-Host "  IAM roles granted successfully" -ForegroundColor Green
} catch {
    Write-Host "  Error: $_" -ForegroundColor Red
    Write-Host "  Continuing without argo-build service account..." -ForegroundColor Yellow
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

