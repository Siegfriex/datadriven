# ARGO Firebase 배포 스크립트
# Created: 2025-12-09
# Project: artdrive1208

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO Firebase Deployment" -ForegroundColor Cyan
Write-Host "Project: artdrive1208" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 빌드
Write-Host "[1/3] Building frontend..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Build completed successfully" -ForegroundColor Green
Write-Host ""

# 2. 빌드 결과 확인
Write-Host "[2/3] Verifying build output..." -ForegroundColor Yellow
if (Test-Path "dist/index.html") {
    Write-Host "  Build output verified: dist/index.html exists" -ForegroundColor Green
} else {
    Write-Host "  Build output not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. Firebase 프로젝트 확인
Write-Host "[3/3] Deploying to Firebase..." -ForegroundColor Yellow

# 프로젝트 설정 확인
firebase use artdrive1208 --quiet 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Setting Firebase project to artdrive1208..." -ForegroundColor Yellow
    firebase use artdrive1208
}

# 배포
Write-Host "  Deploying hosting..." -ForegroundColor Gray
firebase deploy --only hosting

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Deployment Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Frontend URL: https://artdrive1208.web.app" -ForegroundColor Green
    Write-Host ""
    
    # 배포 정보 확인
    firebase hosting:sites:list
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Deployment failed!" -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    exit 1
}

