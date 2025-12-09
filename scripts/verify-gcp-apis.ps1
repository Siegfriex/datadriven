# ARGO GCP API Activation Status Verification Script
# Created: 2025-12-09
# Project: artdrive1208

$PROJECT_ID = "artdrive1208"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO GCP API Activation Status Check" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Required APIs List
$requiredApis = @(
    @{Name="firebasehosting.googleapis.com"; Category="Firebase Services"},
    @{Name="firebasestorage.googleapis.com"; Category="Firebase Services"},
    @{Name="firebaseanalytics.googleapis.com"; Category="Firebase Services"},
    @{Name="identitytoolkit.googleapis.com"; Category="Firebase Services"},
    @{Name="run.googleapis.com"; Category="Cloud Run"},
    @{Name="redis.googleapis.com"; Category="Cloud Memorystore"},
    @{Name="vpcaccess.googleapis.com"; Category="Networking"},
    @{Name="servicenetworking.googleapis.com"; Category="Networking"},
    @{Name="cloudcdn.googleapis.com"; Category="Networking"},
    @{Name="secretmanager.googleapis.com"; Category="Security & Management"},
    @{Name="iam.googleapis.com"; Category="Security & Management"},
    @{Name="cloudresourcemanager.googleapis.com"; Category="Security & Management"},
    @{Name="monitoring.googleapis.com"; Category="Monitoring & Logging"},
    @{Name="logging.googleapis.com"; Category="Monitoring & Logging"},
    @{Name="clouderrorreporting.googleapis.com"; Category="Monitoring & Logging"},
    @{Name="compute.googleapis.com"; Category="Compute Resources"},
    @{Name="cloudbuild.googleapis.com"; Category="Compute Resources"}
)

Write-Host "Checking required API activation status..." -ForegroundColor Yellow
Write-Host ""

$enabledApis = @()
$disabledApis = @()

foreach ($api in $requiredApis) {
    $apiName = $api.Name
    $category = $api.Category
    
    try {
        $result = gcloud services list --enabled --project=$PROJECT_ID --filter="name:$apiName" --format="value(name)" 2>&1 | Out-String
        
        if ($result -and $result.Trim() -match $apiName) {
            Write-Host "  [OK] $apiName" -ForegroundColor Green
            $enabledApis += $api
        } else {
            Write-Host "  [X] $apiName" -ForegroundColor Red
            $disabledApis += $api
        }
    } catch {
        Write-Host "  [?] $apiName (Check failed)" -ForegroundColor Yellow
        $disabledApis += $api
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Enabled: $($enabledApis.Count) / $($requiredApis.Count) APIs" -ForegroundColor $(if ($enabledApis.Count -eq $requiredApis.Count) { "Green" } else { "Yellow" })
Write-Host "  Disabled: $($disabledApis.Count) APIs" -ForegroundColor $(if ($disabledApis.Count -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($disabledApis.Count -gt 0) {
    Write-Host "Disabled APIs:" -ForegroundColor Red
    foreach ($api in $disabledApis) {
        Write-Host "  - $($api.Name) ($($api.Category))" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "To enable, run:" -ForegroundColor Yellow
    Write-Host "  .\scripts\enable-gcp-apis.ps1" -ForegroundColor Cyan
    Write-Host ""
}

# List All Enabled APIs
Write-Host "All enabled APIs (first 20):" -ForegroundColor Yellow
Write-Host ""
gcloud services list --enabled --project=$PROJECT_ID --format="table(name,title)" | Select-Object -First 20

Write-Host ""
Write-Host "Full list: gcloud services list --enabled --project=$PROJECT_ID" -ForegroundColor Gray
