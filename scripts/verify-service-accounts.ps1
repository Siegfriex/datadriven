# ARGO Service Account Verification Script
# Created: 2025-12-09
# Project: artdrive1208

$PROJECT_ID = "artdrive1208"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO Service Account Verification" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Required Service Accounts
$requiredSAs = @(
    @{Email="argo-api@${PROJECT_ID}.iam.gserviceaccount.com"; Name="ARGO API"; Required=$true},
    @{Email="argo-build@${PROJECT_ID}.iam.gserviceaccount.com"; Name="ARGO Build"; Required=$false}
)

Write-Host "Checking service accounts..." -ForegroundColor Yellow
Write-Host ""

$foundCount = 0
$missingCount = 0

foreach ($sa in $requiredSAs) {
    $saEmail = $sa.Email
    $saName = $sa.Name
    $isRequired = $sa.Required
    
    Write-Host "  Checking: $saName" -ForegroundColor Gray -NoNewline
    Write-Host " ($saEmail)" -ForegroundColor DarkGray
    
    try {
        $result = gcloud iam service-accounts describe $saEmail --project=$PROJECT_ID 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    [OK] Service account exists" -ForegroundColor Green
            $foundCount++
            
            # Get IAM roles
            Write-Host "    Roles:" -ForegroundColor Gray
            $roles = gcloud projects get-iam-policy $PROJECT_ID `
                --flatten="bindings[].members" `
                --filter="bindings.members:serviceAccount:$saEmail" `
                --format="value(bindings.role)" 2>&1 | Out-String
            
            if ($roles -and $roles.Trim().Length -gt 0) {
                $roleList = $roles.Trim() -split "`n" | Where-Object { $_.Trim().Length -gt 0 }
                foreach ($role in $roleList) {
                    Write-Host "      - $role" -ForegroundColor DarkGray
                }
            } else {
                Write-Host "      (No roles found)" -ForegroundColor Yellow
            }
        } else {
            if ($isRequired) {
                Write-Host "    [X] Service account not found (REQUIRED)" -ForegroundColor Red
                $missingCount++
            } else {
                Write-Host "    [-] Service account not found (optional)" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "    [?] Error checking service account" -ForegroundColor Yellow
        if ($isRequired) {
            $missingCount++
        }
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Found: $foundCount service accounts" -ForegroundColor Green
Write-Host "  Missing: $missingCount required service accounts" -ForegroundColor $(if ($missingCount -eq 0) { "Green" } else { "Red" })
Write-Host ""

# List all service accounts
Write-Host "All service accounts in project:" -ForegroundColor Yellow
Write-Host ""
gcloud iam service-accounts list --project=$PROJECT_ID --format="table(email,displayName)" | Select-Object -First 10

Write-Host ""
Write-Host "Full list: gcloud iam service-accounts list --project=$PROJECT_ID" -ForegroundColor Gray

if ($missingCount -gt 0) {
    Write-Host ""
    Write-Host "To create missing service accounts:" -ForegroundColor Yellow
    Write-Host "  .\scripts\create-service-accounts.ps1" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host ""
    Write-Host "All required service accounts are configured!" -ForegroundColor Green
    exit 0
}

