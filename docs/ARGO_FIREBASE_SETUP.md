# ARGO Firebase 설정 가이드

**작성일**: 2025-12-09  
**프로젝트 ID**: artdrive1208  
**상태**: 초기화 완료

---

## 1. Firebase 프로젝트 정보

- **프로젝트 ID**: `artdrive1208`
- **프로젝트 이름**: ARTDRIVE
- **Hosting URL**: `https://artdrive1208.web.app` (기본)
- **Custom Domain**: `https://argo.art` (향후 설정)

---

## 2. 생성된 파일 구조

```
DATADRIVEN/
├── firebase.json              # Firebase 설정 파일
├── .firebaserc               # Firebase 프로젝트 설정
├── functions/                # Cloud Functions 디렉토리
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   └── index.ts         # Functions 소스 코드
│   └── lib/                  # 컴파일된 JavaScript (자동 생성)
└── scripts/
    ├── init-firebase.ps1     # Firebase 초기화 스크립트
    └── deploy-firebase.ps1   # Firebase 배포 스크립트
```

---

## 3. Firebase 설정 파일

### 3.1 `firebase.json`

- **Hosting**: `dist` 디렉토리를 public으로 설정
- **Functions**: `functions` 디렉토리, Node.js 20 런타임
- **Rewrites**: SPA 라우팅을 위한 모든 경로 → `/index.html`
- **Headers**: 정적 자산 캐싱 설정 (JS, CSS, 이미지)

### 3.2 `.firebaserc`

- 기본 프로젝트: `artdrive1208`

---

## 4. Firebase Functions

### 4.1 Functions 구조

- **버전**: Gen 2 (Cloud Run 기반)
- **런타임**: Node.js 20
- **언어**: TypeScript
- **리전**: asia-northeast3 (서울)
- **컴파일**: `npm run build` → `lib/` 디렉토리에 JavaScript 생성

**Gen 2의 장점**:
- Cloud Run 기반으로 더 나은 성능과 확장성
- 자동 CORS 처리 지원
- 더 긴 타임아웃 (최대 60분)
- 더 많은 메모리 및 CPU 옵션

### 4.2 현재 구현된 Functions

1. **`apiProxy`** (HTTPS 함수, Gen 2)
   - API 프록시 함수 (필요 시 Cloud Run API로 프록시)
   - 리전: asia-northeast3
   - CORS 자동 처리 (Gen 2 기능)

2. **`generateGalaxySnapshot`** (스케줄 함수, Gen 2)
   - 24시간마다 갤럭시 스냅샷 생성 (향후 구현)
   - 리전: asia-northeast3
   - Cloud Scheduler 기반 (Gen 2)

### 4.3 Functions 빌드 및 배포

```powershell
# Functions 빌드
cd functions
npm run build

# Functions 배포 (Gen 2)
firebase deploy --only functions

# 또는 루트에서
npm run deploy:functions
```

**배포 전 확인사항**:
- Firebase 인증: `firebase login` 또는 `firebase login --reauth`
- Cloud Scheduler API 활성화 확인 (스케줄 함수 사용 시)

### 4.4 Gen 2 마이그레이션 정보

**Gen 1에서 Gen 2로 마이그레이션 완료** (2025-12-09)

**주요 변경사항**:
- Import 경로: `firebase-functions` → `firebase-functions/v2`
- 리전 설정: 각 함수에 `region: 'asia-northeast3'` 명시
- CORS 처리: Gen 2의 `cors: true` 옵션 사용
- 스케줄 함수: `functions.pubsub.schedule()` → `functions.scheduler.onSchedule()`

**리전 설정**:
- 모든 Functions는 `asia-northeast3` (서울) 리전에 배포
- Gen 1 기본 리전인 `us-central1`에서 마이그레이션 완료

**배포 확인**:
```powershell
# Functions 목록 확인
firebase functions:list

# 리전별 Functions 확인
gcloud functions list --region=asia-northeast3

# Cloud Scheduler 작업 확인
gcloud scheduler jobs list --location=asia-northeast3
```

---

## 5. Firebase Hosting 배포

### 5.1 배포 전 준비사항

1. **프론트엔드 빌드**
   ```powershell
   npm run build
   ```
   - `dist/` 디렉토리에 빌드 결과 생성

2. **Firebase 인증**
   ```powershell
   firebase login
   ```
   - 브라우저에서 Google 계정으로 로그인

3. **프로젝트 설정 확인**
   ```powershell
   firebase use artdrive1208
   ```

### 5.2 배포 방법

#### 방법 1: npm 스크립트 사용
```powershell
npm run deploy
# 또는
npm run deploy:hosting
```

#### 방법 2: Firebase CLI 직접 사용
```powershell
firebase deploy --only hosting
```

#### 방법 3: 배포 스크립트 사용
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy-firebase.ps1
```

### 5.3 배포 확인

배포 후 다음 URL에서 확인:
- **기본 URL**: `https://artdrive1208.web.app`
- **Custom Domain**: `https://argo.art` (향후 설정)

---

## 6. Firebase 인증 설정 (향후)

### 6.1 Authentication 활성화

Firebase Console에서:
1. Authentication → Sign-in method 활성화
2. 필요한 인증 방법 선택 (Google, Email/Password 등)

### 6.2 환경변수 설정

프론트엔드에서 Firebase 설정 사용:
```typescript
import { initializeApp } from 'firebase/app';

const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "artdrive1208.firebaseapp.com",
  projectId: "artdrive1208",
  storageBucket: "artdrive1208.appspot.com",
  messagingSenderId: "...",
  appId: "...",
  measurementId: "..."
};

const app = initializeApp(firebaseConfig);
```

---

## 7. Firebase Storage 설정 (향후)

### 7.1 Storage 활성화

Firebase Console에서:
1. Storage → 시작하기
2. 리전 선택: `asia-northeast3` (서울)
3. 보안 규칙 설정

### 7.2 보안 규칙 예시

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

---

## 8. Firebase Analytics 설정 (향후)

### 8.1 Analytics 활성화

Firebase Console에서:
1. Analytics → 시작하기
2. Google Analytics 계정 연결

### 8.2 프론트엔드 통합

```typescript
import { getAnalytics } from 'firebase/analytics';

const analytics = getAnalytics(app);
```

---

## 9. 커스텀 도메인 설정 (향후)

### 9.1 도메인 추가

Firebase Console에서:
1. Hosting → 커스텀 도메인 추가
2. 도메인 입력: `argo.art`
3. DNS 레코드 설정 (A 레코드, CNAME)

### 9.2 SSL 인증서

- Firebase가 자동으로 SSL 인증서 발급 및 관리

---

## 10. 배포 스크립트 사용법

### 10.1 초기화 스크립트

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-firebase.ps1
```

**기능**:
- Firebase CLI 확인 및 설치
- Firebase 인증 확인
- 프로젝트 설정 확인
- Functions 의존성 설치

### 10.2 배포 스크립트

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy-firebase.ps1
```

**기능**:
- 프론트엔드 빌드 (`npm run build`)
- 빌드 결과 확인
- Firebase Hosting 배포
- 배포 URL 표시

---

## 11. 트러블슈팅

### 11.1 Firebase 인증 오류

**문제**: `Authentication Error: Your credentials are no longer valid`

**해결**:
```powershell
firebase login --reauth
```

### 11.2 프로젝트 접근 오류

**문제**: `Invalid project selection`

**해결**:
```powershell
firebase use artdrive1208
firebase projects:list  # 프로젝트 목록 확인
```

### 11.3 빌드 실패

**문제**: `dist/` 디렉토리가 생성되지 않음

**해결**:
```powershell
npm run build
# 빌드 결과 확인
Test-Path dist/index.html
```

### 11.4 Functions 빌드 오류

**문제**: TypeScript 컴파일 오류

**해결**:
```powershell
cd functions
npm install
npm run build
```

### 11.5 Gen 2 배포 오류

**문제**: `Authentication Error: Your credentials are no longer valid`

**해결**:
```powershell
firebase login --reauth
```

**문제**: Functions가 잘못된 리전에 배포됨

**해결**:
- `functions/src/index.ts`에서 `region` 상수 확인
- `asia-northeast3`로 설정되어 있는지 확인
- 재배포: `firebase deploy --only functions`

**문제**: Gen 1 함수가 남아있음

**해결**:
```powershell
# 기존 Gen 1 함수 삭제
firebase functions:delete <function-name> --region us-central1 --force

# Gen 2로 재배포
firebase deploy --only functions
```

### 11.6 Cloud Scheduler API 오류

**문제**: 스케줄 함수 배포 시 Cloud Scheduler API 오류

**해결**:
```powershell
# API 활성화 확인
gcloud services list --enabled --filter="name:cloudscheduler.googleapis.com"

# 필요 시 활성화
gcloud services enable cloudscheduler.googleapis.com --project=artdrive1208
```

---

## 12. 다음 단계

1. ✅ **Firebase 초기화**: 완료
2. ✅ **Functions 설정**: 완료 (Gen 2로 마이그레이션 완료)
3. ✅ **Functions 코드 마이그레이션**: Gen 2로 완료
4. ⏳ **Firebase 인증**: `firebase login --reauth` 실행 필요
5. ⏳ **Gen 2 Functions 배포**: 인증 후 `firebase deploy --only functions`
6. ⏳ **배포 검증**: 리전 및 Gen 2 여부 확인
7. ⏳ **프론트엔드 빌드**: `npm run build`
8. ⏳ **Hosting 배포**: `npm run deploy`
9. ⏳ **Storage 설정**: Firebase Console에서 활성화
10. ⏳ **Analytics 설정**: Firebase Console에서 활성화
11. ⏳ **커스텀 도메인 설정**: DNS 설정 후 Firebase Console에서 추가

---

## 13. 참고 문서

- [Firebase Hosting 문서](https://firebase.google.com/docs/hosting)
- [Firebase Functions 문서](https://firebase.google.com/docs/functions)
- [Firebase Functions Gen 2 문서](https://firebase.google.com/docs/functions/2nd-gen)
- [Firebase Functions 리전 목록](https://firebase.google.com/docs/functions/locations)
- [Cloud Scheduler API 문서](https://cloud.google.com/scheduler/docs)
- [Firebase CLI 참조](https://firebase.google.com/docs/cli)

