# ARGO Firebase 초기화 스크립트
# Created: 2025-12-09
# Project: artdrive1208

$PROJECT_ID = "artdrive1208"
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARGO Firebase Initialization" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Firebase CLI 확인
Write-Host "[1/4] Checking Firebase CLI..." -ForegroundColor Yellow
try {
    $firebaseVersion = firebase --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Firebase CLI version: $firebaseVersion" -ForegroundColor Green
    } else {
        Write-Host "  Firebase CLI not found. Installing..." -ForegroundColor Yellow
        npm install -g firebase-tools
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  Failed to install Firebase CLI" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "  Firebase CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g firebase-tools
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Failed to install Firebase CLI" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# 2. Firebase 로그인 확인
Write-Host "[2/4] Checking Firebase authentication..." -ForegroundColor Yellow
try {
    $authStatus = firebase projects:list 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -or $authStatus -match "not logged in" -or $authStatus -match "인증") {
        Write-Host "  Not logged in. Please login..." -ForegroundColor Yellow
        firebase login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  Firebase login failed" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  Already authenticated" -ForegroundColor Green
    }
} catch {
    Write-Host "  Authentication check failed. Please login manually:" -ForegroundColor Yellow
    Write-Host "    firebase login" -ForegroundColor Cyan
}

Write-Host ""

# 3. 프로젝트 설정 확인
Write-Host "[3/4] Checking Firebase project configuration..." -ForegroundColor Yellow

if (Test-Path ".firebaserc") {
    Write-Host "  .firebaserc file exists" -ForegroundColor Green
    
    # 프로젝트 설정
    firebase use $PROJECT_ID
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Project set to: $PROJECT_ID" -ForegroundColor Green
    } else {
        Write-Host "  Failed to set project" -ForegroundColor Yellow
    }
} else {
    Write-Host "  .firebaserc file not found. Creating..." -ForegroundColor Yellow
    # .firebaserc는 이미 생성되어 있어야 함
}

Write-Host ""

# 4. Functions 디렉토리 확인 및 설정
Write-Host "[4/4] Checking Functions directory..." -ForegroundColor Yellow

if (Test-Path "functions") {
    Write-Host "  Functions directory exists" -ForegroundColor Green
    
    if (Test-Path "functions/package.json") {
        Write-Host "  Installing Functions dependencies..." -ForegroundColor Gray
        Push-Location functions
        npm install
        Pop-Location
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Functions dependencies installed" -ForegroundColor Green
        } else {
            Write-Host "  Failed to install Functions dependencies" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  Functions directory not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firebase Initialization Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Build frontend: npm run build" -ForegroundColor Gray
Write-Host "  2. Deploy hosting: firebase deploy --only hosting" -ForegroundColor Gray
Write-Host "  3. Or use: npm run deploy" -ForegroundColor Gray
Write-Host ""

