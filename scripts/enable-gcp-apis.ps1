# ARGO GCP API Activation Script
# Created: 2025-12-09
# Project: artdrive1208

# Project Configuration
$PROJECT_ID = "artdrive1208"
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO GCP API Activation Script" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify Project Configuration
Write-Host "[1/3] Verifying project configuration..." -ForegroundColor Yellow
try {
    $currentProject = gcloud config get-value project 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "gcloud CLI is not installed or not authenticated." -ForegroundColor Red
        Write-Host "Please run: gcloud auth login" -ForegroundColor Yellow
        exit 1
    }
    
    if ($currentProject -ne $PROJECT_ID) {
        Write-Host "Setting project to $PROJECT_ID..." -ForegroundColor Yellow
        gcloud config set project $PROJECT_ID
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to set project" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Project is already set: $PROJECT_ID" -ForegroundColor Green
    }
} catch {
    Write-Host "Error during project configuration: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Required APIs List
$requiredApis = @(
    # Firebase Services
    "firebasehosting.googleapis.com",
    "firebasestorage.googleapis.com",
    "firebaseanalytics.googleapis.com",
    "identitytoolkit.googleapis.com",
    
    # Cloud Run
    "run.googleapis.com",
    
    # Cloud Memorystore (Redis)
    "redis.googleapis.com",
    
    # Networking
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "cloudcdn.googleapis.com",
    
    # Security & Management
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    
    # Monitoring & Logging
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "clouderrorreporting.googleapis.com",
    
    # Compute Resources
    "compute.googleapis.com",
    "cloudbuild.googleapis.com"
)

# Optional APIs List
$optionalApis = @(
    # Vertex AI (Future expansion)
    "aiplatform.googleapis.com"
)

Write-Host "[2/3] Enabling required APIs..." -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0
$alreadyEnabledCount = 0

foreach ($api in $requiredApis) {
    Write-Host "  Enabling: $api" -ForegroundColor Gray -NoNewline
    
    try {
        $result = gcloud services enable $api --project=$PROJECT_ID 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            # Check if already enabled
            if ($result -match "already enabled" -or $result -match "already") {
                Write-Host " - Already enabled" -ForegroundColor Yellow
                $alreadyEnabledCount++
            } else {
                Write-Host " - Success" -ForegroundColor Green
                $successCount++
            }
        } else {
            Write-Host " - Failed" -ForegroundColor Red
            Write-Host "    Error: $result" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host " - Failed" -ForegroundColor Red
        Write-Host "    Exception: $_" -ForegroundColor Red
        $failCount++
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "[3/3] Enabling optional APIs..." -ForegroundColor Yellow
Write-Host ""

foreach ($api in $optionalApis) {
    Write-Host "  Enabling: $api" -ForegroundColor Gray -NoNewline
    
    try {
        $result = gcloud services enable $api --project=$PROJECT_ID 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            if ($result -match "already enabled" -or $result -match "already") {
                Write-Host " - Already enabled" -ForegroundColor Yellow
                $alreadyEnabledCount++
            } else {
                Write-Host " - Success" -ForegroundColor Green
                $successCount++
            }
        } else {
            Write-Host " - Failed" -ForegroundColor Red
            Write-Host "    Error: $result" -ForegroundColor Red
            $failCount++
        }
    } catch {
        Write-Host " - Failed" -ForegroundColor Red
        Write-Host "    Exception: $_" -ForegroundColor Red
        $failCount++
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Activation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Newly enabled: $successCount APIs" -ForegroundColor Green
Write-Host "  Already enabled: $alreadyEnabledCount APIs" -ForegroundColor Yellow
Write-Host "  Failed: $failCount APIs" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })
Write-Host ""

# List Enabled APIs
Write-Host "Listing enabled APIs..." -ForegroundColor Yellow
Write-Host ""
gcloud services list --enabled --project=$PROJECT_ID --format="table(name,title)" | Select-Object -First 25

Write-Host ""
Write-Host "Full list: gcloud services list --enabled --project=$PROJECT_ID" -ForegroundColor Gray
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "All APIs have been successfully enabled!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some APIs failed to enable. Please check the error messages above." -ForegroundColor Red
    exit 1
}
