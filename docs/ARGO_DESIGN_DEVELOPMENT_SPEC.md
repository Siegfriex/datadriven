# ARGO: 디자인 디벨롭먼트 명세서
## Design Development Specification (DDS)

**Version**: 1.0  
**Last Updated**: 2025-12-08  
**Status**: Ready for Design Development  
**Target Audience**: Design Team, Cline AI Assistant  
**Reference Documents**: PRD, SRD, TSD (docs 폴더)

---

## Executive Summary

이 문서는 **ARGO 3D 갤러리**의 세부 디자인 디벨롭먼트를 위한 명확한 기능 요구 명세(FRS)와 사용자 경험 요구 명세(UXRS)를 제공합니다.

**현재 구현 상태:**
- ✅ 기본 3D 갤러리 구조 완성 (`features/galaxy/components/`)
- ✅ InstancedMesh 기반 입자 시스템 구현
- ✅ 미니멀 패널 UI (LeftPanel, RightPanel)
- ✅ 기본 상호작용 (호버, 클릭)
- ✅ 쉐이더 관련 파일 정리 완료 (2025-12-08)
- ✅ AppContext/useAppStore ARGO 전용으로 재작성 완료
- ✅ 전체화면 캔버스 구현 완료
- ⚠️ 디자인 디테일 및 UX 개선 필요

**목표:**
- 문서 스위트(PRD, SRD, TSD)를 기준으로 디자인 완성도 향상
- 사용자 경험 최적화
- 시각적 일관성 확보

---

## 1. 폴더 구조 및 파일 참조

### 1.1 핵심 문서 위치

```
C:\DATADRIVEN\docs\
├── ARGO_PRD_Final.md          # 제품 요구사항 (홈화면, 갤럭시 시각화 명세)
├── ARGO_SRD_Final.md          # 소프트웨어 요구사항 (기능별 상세 명세)
├── ARGO_TSD_Final.md          # 기술 명세 (데이터 구조, API, 알고리즘)
├── ARGO_BRD_Final.md          # 비즈니스 요구사항
└── ARGO_Final_Schema.md        # 데이터 스키마 정의
```

### 1.2 현재 구현 파일 위치

```
C:\DATADRIVEN\
├── App.tsx                                        # 메인 앱 컴포넌트
├── index.tsx                                      # 진입점
├── index.css                                      # 전역 스타일
├── index.html                                     # HTML 템플릿
│
├── features\
│   └── galaxy\
│       ├── components\
│       │   ├── GalaxyScene.tsx                    # 메인 3D 씬 (Canvas 설정)
│       │   ├── ArtistParticles.tsx                # 입자 시스템 (InstancedMesh)
│       │   ├── GalaxyControls.tsx                 # 카메라 제어
│       │   ├── HoverLabel.tsx                     # 호버 라벨
│       │   ├── LeftPanel.tsx                      # 좌측 패널 (필터/통계)
│       │   └── RightPanel.tsx                     # 우측 패널 (작가 정보)
│       ├── hooks\
│       │   └── useGalaxy.ts                       # 갤럭시 상태 관리
│       └── utils\
│           ├── colorMapping.ts                   # 색상 매핑 유틸리티
│           └── coordinateTransform.ts             # 좌표 변환 유틸리티
│
├── types\
│   └── argo.ts                                    # TypeScript 타입 정의
│
├── data\
│   └── mockArtists.json                           # 목업 데이터 (100명)
│
├── context\
│   └── AppContext.tsx                             # ARGO 전용 앱 컨텍스트
│
├── hooks\
│   └── useAppStore.ts                             # ARGO 전용 앱 스토어
│
├── config.ts                                      # ARGO 전용 설정
├── tailwind.config.js                             # Tailwind CSS 설정
├── tsconfig.json                                  # TypeScript 설정
├── vite.config.ts                                 # Vite 설정
└── package.json                                   # 의존성 관리
```

### 1.3 주요 참조 문서 섹션

| 문서 | 관련 섹션 | 내용 |
|------|----------|------|
| **PRD** | 3. 홈화면 | 레이아웃, 갤럭시 시각화 원칙 |
| **PRD** | 3.3 갤럭시 시각화 | 입자 시스템, 색상 매핑, 크기 |
| **SRD** | 2. Feature 1: 3D 갤럭시 시각화 | 기술 명세, 상호작용, 필터 |
| **TSD** | 2.1.1 Artist | 데이터 구조, 점수, 좌표 |
| **TSD** | 10.2 프론트엔드 컴포넌트 | 컴포넌트 구조 |

---

## 2. 기능 요구 명세 (Functional Requirements Specification)

### 2.1 F1: 3D 갤럭시 시각화 (Core Feature)

#### 2.1.1 입자 시스템 (Particle System)

**참조 파일:** `features/galaxy/components/ArtistParticles.tsx`  
**참조 문서:** PRD 3.3.1, SRD 2.2.2, TSD 2.1.1

**요구사항:**

1. **입자 렌더링**
   - ✅ InstancedMesh 사용 (현재 구현됨)
   - ⚠️ **개선 필요:** 입자 가시성 향상 (색상, 크기, 발광)
   - ⚠️ **개선 필요:** LOD (Level of Detail) 구현 (SRD 2.2.2 참조)
   - ⚠️ **개선 필요:** 뷰 프러스텀 컬링 최적화

2. **색상 매핑** (PRD 3.3.1)
   ```
   R = inst_score (0-100 → 0-255)
   G = acad_score (0-100 → 0-255)
   B = media_score (0-100 → 0-255)
   ```
   - ✅ 기본 구현 완료 (`colorMapping.ts`)
   - ⚠️ **개선 필요:** 색상 대비 및 가시성 향상
   - ⚠️ **개선 필요:** Alpha 채널 조정 (기본 0.8, 선택 시 1.0)

3. **크기 매핑** (PRD 3.3.1)
   ```
   radius = 10 + (network_score / 5)
   범위: 5px ~ 20px
   ```
   - ✅ 기본 구현 완료
   - ⚠️ **개선 필요:** 크기 범위 최적화 (현재 0.5-0.8 스케일)

4. **발광 효과** (SRD 2.2.2)
   ```
   composite_score 기반:
   0-50: 어두움
   50-70: 중간
   70-100: 밝음
   ```
   - ⚠️ **구현 필요:** `scoreToEmissive` 함수 완성 (`colorMapping.ts`)

#### 2.1.2 카메라 제어 (Camera Controls)

**참조 파일:** `features/galaxy/components/GalaxyControls.tsx`  
**참조 문서:** SRD 2.2.3, TSD 10.2.2

**요구사항:**

1. **기본 제어**
   - ✅ Trackball Camera 구현 (camera-controls 사용)
   - ✅ 키보드 단축키 (R, F, H)
   - ⚠️ **개선 필요:** 애니메이션 타이밍 조정 (0.5초 easing)

2. **포커싱**
   - ✅ 선택된 작가로 자동 포커싱 (`zoomToArtist`)
   - ⚠️ **개선 필요:** 더블클릭 포커싱 구현
   - ⚠️ **개선 필요:** 우클릭 리셋 구현

3. **줌 범위**
   ```
   목표: 0.5x ~ 10x
   현재: minDistance=5, maxDistance=100
   ```
   - ⚠️ **검증 필요:** 실제 줌 범위 확인 및 조정

#### 2.1.3 상호작용 (Interaction)

**참조 파일:** `features/galaxy/components/ArtistParticles.tsx`, `HoverLabel.tsx`  
**참조 문서:** SRD 2.2.4

**요구사항:**

1. **클릭 탐지**
   - ✅ Raycaster 사용 (현재 구현됨)
   - ⚠️ **개선 필요:** 클릭 가능 반경 확대 (입자 크기의 2배)
   - ⚠️ **개선 필요:** 겹침 처리 개선 (카메라에 가장 가까운 입자 우선)

2. **선택 시각화**
   - ✅ 선택 입자 색상 증폭 (현재 구현됨)
   - ⚠️ **구현 필요:** 연결선 표시 (SRD 2.2.4)
     - 협력자: 파란색 선 (strength ≥ 0.3)
     - 소속 기관: 초록색 선
     - 전시 참여: 황색 선
   - ⚠️ **구현 필요:** 연결선 애니메이션 (0.3초 fade-in)

3. **호버 효과**
   - ✅ 호버 입자 확대 (1.8x)
   - ✅ Tooltip 표시 (`HoverLabel.tsx`)
   - ⚠️ **개선 필요:** 아우라 표시 (0.2초 애니메이션)
   - ⚠️ **개선 필요:** Tooltip 위치 최적화 (마우스 우상향 20px)
   - ⚠️ **개선 필요:** Tooltip 자동 사라짐 (3초 후)

#### 2.1.4 필터 동적 업데이트

**참조 파일:** `features/galaxy/components/LeftPanel.tsx`  
**참조 문서:** SRD 2.2.5

**요구사항:**

1. **필터 UI**
   - ✅ 기본 필터 UI 구현 (Segment, Career)
   - ⚠️ **구현 필요:** 필터 상태 관리 및 API 연동
   - ⚠️ **구현 필요:** 추가 필터 (region, score_range, institution_id)

2. **동적 업데이트**
   - ⚠️ **구현 필요:** 필터 적용 시 갤럭시 업데이트
     - 숨김 입자: opacity → 0 (0.5초)
     - 표시 입자: opacity → 0.8 (0.5초)
   - ⚠️ **구현 필요:** 카메라 자동 조정 (새 데이터 범위에 맞춤)

---

### 2.2 F2: UI 패널 시스템

#### 2.2.1 좌측 패널 (Left Panel)

**참조 파일:** `features/galaxy/components/LeftPanel.tsx`  
**참조 문서:** PRD 3.2, SRD 2.3

**요구사항:**

1. **갤럭시 통계**
   - ✅ 기본 통계 표시 (Artists, Clusters)
   - ⚠️ **구현 필요:** 실시간 통계 업데이트 (API 연동)
   - ⚠️ **구현 필요:** 추가 통계 (기관 수, 거래 수)
   - ⚠️ **디자인 개선:** 통계 시각화 (바 차트, 링 차트)

2. **필터 UI**
   - ✅ 기본 필터 UI (Segment, Career)
   - ⚠️ **구현 필요:** 필터 상태 관리 (체크박스/라디오)
   - ⚠️ **구현 필요:** 필터 적용 버튼 및 리셋 기능
   - ⚠️ **디자인 개선:** 아코디언 메뉴 애니메이션

3. **레이아웃**
   - ✅ 미니멀 디자인 (하얀색 타이포 중심)
   - ⚠️ **개선 필요:** 패널 너비 조정 (현재 72 = 288px)
   - ⚠️ **개선 필요:** 반응형 대응 (모바일/태블릿)

#### 2.2.2 우측 패널 (Right Panel)

**참조 파일:** `features/galaxy/components/RightPanel.tsx`  
**참조 문서:** PRD 3.2, SRD 2.4

**요구사항:**

1. **작가 프로필**
   - ✅ 기본 프로필 표시 (이름, 연도, 세그먼트)
   - ⚠️ **구현 필요:** 추가 정보 (소속 기관, 협력자 TOP 5)
   - ⚠️ **구현 필요:** 외부 링크 (공식 웹사이트, Wikipedia)

2. **점수 시각화**
   - ✅ 레이더 차트 구현 (SVG)
   - ⚠️ **디자인 개선:** 레이더 차트 스타일링 (색상, 애니메이션)
   - ⚠️ **구현 필요:** 점수 메타데이터 표시 (각 점수별 상세 정보)

3. **구조주의 분석**
   - ✅ 기본 분석 텍스트
   - ⚠️ **구현 필요:** 데이터 기반 분석 문장 생성 (LLM 연동)
   - ⚠️ **구현 필요:** 구조적 위치 시각화 (필드 쿼드런트)

4. **액션 버튼**
   - ⚠️ **구현 필요:** "Full Report" 버튼 기능
   - ⚠️ **구현 필요:** "비교하기" 버튼
   - ⚠️ **구현 필요:** "다운로드" 버튼 (CSV, JSON)

---

### 2.3 F3: 레이아웃 및 반응형 디자인

**참조 파일:** `App.tsx`, `index.css`  
**참조 문서:** PRD 3.2, SRD 2.1

**요구사항:**

1. **전체 레이아웃**
   - ✅ 전체화면 캔버스 구현
   - ✅ 패널 오버레이 방식
   - ⚠️ **개선 필요:** 레이아웃 비율 조정 (PRD 3.2: 60% 캔버스, 20% 패널)

2. **반응형 디자인**
   ```
   데스크톱: 60% 캔버스, 20% 패널
   태블릿: 70% 캔버스, 15% 패널
   모바일: 90% 캔버스, 패널 토글
   ```
   - ⚠️ **구현 필요:** 태블릿/모바일 반응형 대응
   - ⚠️ **구현 필요:** 패널 토글 버튼 개선

3. **네비게이션**
   - ⚠️ **구현 필요:** 하단 메뉴 (PRD 3.2)
     - [분석] [군집] [이상치] [방법론] [비교] [프로필]

---

## 3. 사용자 경험 요구 명세 (User Experience Requirements Specification)

### 3.1 디자인 원칙 (Design Principles)

**참조 문서:** PRD 3.1

**핵심 원칙:**

1. **Data-Driven Art Design**
   - 데이터는 미학: 수치를 시각적 아름다움으로 변환
   - 상호작용은 탐구: 클릭/드래그가 새로운 인사이트 제시
   - 투명성: 모든 렌더링은 알고리즘을 반영
   - 미니멀: 불필요한 요소 제거, 갤럭시에 집중

2. **Arario Gallery 스타일**
   - 깔끔하고 세련된 미니멀 디자인
   - 하얀색 타이포 중심
   - Deep Dark Theme (#050505 배경)
   - 글래스모피즘 효과 (backdrop-blur)

### 3.2 시각적 디자인 (Visual Design)

#### 3.2.1 색상 시스템

**참조 파일:** `tailwind.config.js`, `features/galaxy/utils/colorMapping.ts`

**요구사항:**

1. **배경 색상**
   ```
   기본 배경: #050505 (거의 검정)
   패널 배경: rgba(0, 0, 0, 0.9) + backdrop-blur-lg
   ```

2. **텍스트 색상**
   ```
   Primary: #ffffff (하얀색)
   Secondary: rgba(255, 255, 255, 0.8)
   Tertiary: rgba(255, 255, 255, 0.6)
   ```

3. **입자 색상**
   ```
   데이터 기반 RGB (inst, acad, media 점수)
   최소 밝기 보장: 0.4 (가시성)
   호버 시 밝기 증가: 1.5x
   ```

#### 3.2.2 타이포그래피

**참조 파일:** `index.css`, `tailwind.config.js`

**요구사항:**

1. **폰트 패밀리**
   ```
   Sans: 'Inter', 'Noto Sans KR'
   Serif: 'Playfair Display', 'Noto Serif KR' (제목용)
   Mono: 시스템 기본 (코드/숫자용)
   ```

2. **타이포 스케일**
   ```
   H1: 3xl (30px) - 작가 이름
   H2: 2xl (24px) - 섹션 제목
   H3: sm (14px) - 필터 제목
   Body: sm (14px) - 본문
   Caption: xs (12px) - 라벨
   ```

3. **폰트 웨이트**
   ```
   Light: 300 (숫자, 통계)
   Regular: 400 (본문)
   Medium: 500 (강조)
   Bold: 700 (제목)
   ```

#### 3.2.3 간격 시스템 (Spacing)

**요구사항:**

```
기본 단위: 4px (0.25rem)
패널 패딩: 8 (32px)
섹션 간격: 12 (48px)
요소 간격: 2-4 (8-16px)
```

#### 3.2.4 애니메이션

**요구사항:**

1. **전환 시간**
   ```
   빠른 전환: 200ms (호버)
   일반 전환: 300ms (패널 토글)
   느린 전환: 500ms (카메라 이동)
   ```

2. **이징 함수**
   ```
   ease-out: 패널 슬라이드
   ease-in-out: 카메라 이동
   ease: 호버 효과
   ```

### 3.3 상호작용 디자인 (Interaction Design)

#### 3.3.1 호버 상태

**요구사항:**

1. **입자 호버**
   - 확대: 1.8x 스케일 (0.2초)
   - 색상 밝기 증가: 1.5x (0.2초)
   - 발광 강도 증가: 0.3 → 0.5 (0.2초)
   - 아우라 표시: 반경 2x (0.2초 fade-in)

2. **UI 요소 호버**
   - 버튼: opacity 0.4 → 1.0 (0.2초)
   - 필터 항목: 텍스트 밝기 증가 (0.2초)
   - 패널 토글: 배경 밝기 증가 (0.2초)

#### 3.3.2 클릭 상태

**요구사항:**

1. **입자 클릭**
   - 선택 시각화: 색상 증폭 150% (0.3초)
   - 연결선 표시: fade-in (0.3초)
   - 우측 패널 자동 열기 (모바일)
   - 카메라 포커싱 (선택적)

2. **버튼 클릭**
   - 피드백: 약간의 스케일 다운 (0.1초)
   - 상태 변경: 즉시 반영

#### 3.3.3 키보드 단축키

**참조 문서:** SRD 2.2.3

**요구사항:**

```
R: 카메라 리셋
H: 홈 위치로 이동
F: 선택된 입자 포커싱
Esc: 선택 해제, 패널 닫기
```

### 3.4 피드백 및 피드포워드 (Feedback & Feedforward)

#### 3.4.1 로딩 상태

**요구사항:**

1. **초기 로딩**
   - 스켈레톤 UI 표시
   - 진행률 표시 (선택적)
   - 최대 3초 로딩 목표 (SRD 2.1)

2. **필터 적용 중**
   - 로딩 스피너 표시
   - "업데이트 중..." 메시지

#### 3.4.2 에러 상태

**요구사항:**

1. **API 에러**
   - 에러 메시지 표시 (토스트)
   - 재시도 버튼 제공

2. **렌더링 에러**
   - 폴백 메시지 표시
   - 개발자 콘솔에 상세 에러 로그

### 3.5 접근성 (Accessibility)

**요구사항:**

1. **키보드 네비게이션**
   - Tab: UI 요소 포커스 이동
   - Enter/Space: 선택/활성화
   - 화살표 키: 필터 목록 네비게이션

2. **스크린 리더**
   - ARIA 레이블 추가
   - 의미론적 HTML 사용
   - 대체 텍스트 제공

3. **색상 대비**
   - WCAG AA 기준 준수 (4.5:1)
   - 색상만으로 정보 전달하지 않기

---

## 4. 구현 우선순위

### Phase 1: 핵심 기능 완성 (P0)

1. ✅ 입자 시스템 기본 구현
2. ⚠️ 입자 가시성 향상 (색상, 크기, 발광)
3. ⚠️ 호버/클릭 상호작용 개선
4. ⚠️ 패널 UI 완성 (필터 기능, 통계 시각화)

### Phase 2: UX 개선 (P1)

1. ⚠️ 연결선 시각화
2. ⚠️ 필터 동적 업데이트
3. ⚠️ 반응형 디자인
4. ⚠️ 애니메이션 개선

### Phase 3: 고급 기능 (P2)

1. ⚠️ LOD 최적화
2. ⚠️ 네비게이션 메뉴
3. ⚠️ 접근성 개선
4. ⚠️ 성능 모니터링

---

## 5. 검증 기준 (Acceptance Criteria)

### 5.1 기능 검증

- [ ] 입자가 명확하게 보임 (색상, 크기, 발광)
- [ ] 호버 시 즉각적인 피드백 (0.2초 이내)
- [ ] 클릭 시 선택 상태 명확히 표시
- [ ] 필터 적용 시 갤럭시 즉시 업데이트
- [ ] 패널 토글이 부드럽게 작동 (300ms)

### 5.2 성능 검증

- [ ] 60 FPS 유지 (데스크톱)
- [ ] 초기 로딩 3초 이내
- [ ] 필터 적용 응답 시간 1초 이내
- [ ] 메모리 사용량 최적화

### 5.3 디자인 검증

- [ ] Arario Gallery 스타일 일관성
- [ ] 미니멀 디자인 원칙 준수
- [ ] 색상 대비 WCAG AA 기준 준수
- [ ] 반응형 디자인 작동 확인

---

## 6. 참조 자료

### 6.1 문서 참조

- `docs/ARGO_PRD_Final.md`: 제품 요구사항 (홈화면, 갤럭시 시각화)
- `docs/ARGO_SRD_Final.md`: 소프트웨어 요구사항 (기능별 상세)
- `docs/ARGO_TSD_Final.md`: 기술 명세 (데이터 구조, API)
- `docs/ARGO_BRD_Final.md`: 비즈니스 요구사항

### 6.2 코드 참조

- `features/galaxy/components/`: 모든 갤럭시 컴포넌트
- `types/argo.ts`: 데이터 타입 정의
- `data/mockArtists.json`: 목업 데이터

### 6.3 외부 리소스

- Three.js Documentation: https://threejs.org/docs/
- React Three Fiber: https://docs.pmnd.rs/react-three-fiber/
- Tailwind CSS: https://tailwindcss.com/docs

---

## 7. 다음 단계

1. **Cline AI에게 이 문서 제공**
2. **우선순위에 따라 단계별 구현**
3. **각 단계별 검증 및 피드백**
4. **문서 업데이트 (구현 완료 시)**

---

**문서 작성자:** ARGO Development Team  
**최종 검토일:** 2025-12-08  
**다음 업데이트 예정:** 구현 진행에 따라 업데이트

---

## 변경 이력 (Changelog)

### v1.1 (2025-12-08)
- 폴더 구조 수정 (src/ 제거, 실제 구조 반영)
- 구현 상태 업데이트 (쉐이더 파일 정리 완료 반영)
- AppContext/useAppStore 재작성 완료 반영

### v1.0 (2025-12-08)
- 초안 작성

