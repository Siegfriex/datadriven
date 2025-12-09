# ARGO: 한국 미술계 구조 분석 엔진

**Version**: 1.0  
**Last Updated**: 2025-12-08  
**Status**: Development in Progress

## 프로젝트 소개

ARGO는 한국 미술계의 구조와 권력 관계를 3D 갤럭시 시각화로 드러내는 데이터 분석 플랫폼입니다.

### 핵심 기능
- **3D 갤럭시 시각화**: Three.js 기반 입자 시스템으로 작가들을 시각화
- **구조주의 분석**: 제도·학술·담론·네트워크 4개 레이어 분석
- **실시간 필터링**: 세그먼트, 경력 단계 등 다양한 필터 지원
- **작가 프로필**: 상세 정보 및 구조주의 분석 제공

## 기술 스택

- **Frontend**: React 19, TypeScript, Vite
- **3D 렌더링**: Three.js r181, React Three Fiber, @react-three/drei
- **카메라 제어**: camera-controls
- **스타일링**: Tailwind CSS 4.1
- **상태 관리**: React Hooks, Context API

## 설치 및 실행

### Prerequisites
- Node.js 18+
- npm 또는 yarn

### 설치
```bash
npm install
```

### 개발 서버 실행
```bash
npm run dev
```

### 프로덕션 빌드
```bash
npm run build
npm run preview
```

## 프로젝트 구조

```
C:\DATADRIVEN\
├── App.tsx                    # 메인 앱 컴포넌트
├── index.tsx                  # 진입점
├── index.css                  # 전역 스타일
├── index.html                 # HTML 템플릿
│
├── features/
│   └── galaxy/                # 3D 갤럭시 기능
│       ├── components/       # 갤럭시 컴포넌트
│       │   ├── GalaxyScene.tsx
│       │   ├── ArtistParticles.tsx
│       │   ├── GalaxyControls.tsx
│       │   ├── HoverLabel.tsx
│       │   ├── LeftPanel.tsx
│       │   └── RightPanel.tsx
│       ├── hooks/             # 커스텀 훅
│       │   └── useGalaxy.ts
│       └── utils/             # 유틸리티 함수
│           ├── colorMapping.ts
│           └── coordinateTransform.ts
│
├── types/
│   └── argo.ts                # TypeScript 타입 정의
│
├── data/
│   └── mockArtists.json       # 목업 데이터 (100명)
│
├── context/
│   └── AppContext.tsx         # ARGO 전용 앱 컨텍스트
│
├── hooks/
│   └── useAppStore.ts         # ARGO 전용 앱 스토어
│
├── config.ts                  # ARGO 전용 설정
├── tailwind.config.js         # Tailwind CSS 설정
├── tsconfig.json              # TypeScript 설정
├── vite.config.ts             # Vite 설정
└── package.json               # 의존성 관리
```

## 주요 컴포넌트

### GalaxyScene
메인 3D 씬 설정 및 Canvas 구성. Three.js 렌더러 초기화 및 조명 설정.

### ArtistParticles
InstancedMesh 기반 입자 시스템. 100명의 작가를 효율적으로 렌더링하며, 데이터 기반 색상 매핑 적용.

### GalaxyControls
카메라 제어 시스템. camera-controls를 사용한 부드러운 카메라 조작 및 키보드 단축키 지원.

### LeftPanel
좌측 필터 및 통계 패널. 미니멀 디자인으로 갤럭시 통계와 필터 옵션 제공.

### RightPanel
우측 작가 정보 패널. 선택된 작가의 프로필, 점수 시각화(레이더 차트), 구조주의 분석 표시.

## 데이터 구조

### Artist 타입
```typescript
interface Artist {
  artist_id: string;
  name: string;
  alternativeName?: string;
  birth_year?: number;
  segment_id?: string;
  career_stage?: 'early' | 'mid' | 'late';
  scores: {
    inst_score: number;      // 제도 레이어 (0-100)
    acad_score: number;      // 학술 레이어 (0-100)
    media_score: number;     // 담론 레이어 (0-100)
    network_score: number;   // 네트워크 레이어 (0-100)
    composite_score: number; // 복합 점수 (0-100)
  };
  coordinates_3d: {
    x: number;               // inst_score 정규화
    y: number;               // acad_score 정규화
    z: number;               // media_score 정규화
    radius: number;          // network_score 기반
  };
}
```

## 문서

자세한 내용은 `docs/` 폴더의 문서를 참조하세요:

- **ARGO_PRD_Final.md**: 제품 요구사항 문서
- **ARGO_SRD_Final.md**: 소프트웨어 요구사항 명세서
- **ARGO_TSD_Final.md**: 기술 명세서
- **ARGO_BRD_Final.md**: 비즈니스 요구사항 문서
- **ARGO_DESIGN_DEVELOPMENT_SPEC.md**: 디자인 개발 명세서

## 개발 상태

### 완료된 기능
- ✅ 기본 3D 갤럭시 구조 완성
- ✅ InstancedMesh 기반 입자 시스템 구현
- ✅ 미니멀 패널 UI (LeftPanel, RightPanel)
- ✅ 기본 상호작용 (호버, 클릭)
- ✅ 쉐이더 관련 파일 정리 완료
- ✅ AppContext/useAppStore ARGO 전용으로 재작성 완료

### 진행 중
- ⚠️ 디자인 디테일 및 UX 개선
- ⚠️ 필터 동적 업데이트 기능
- ⚠️ 연결선 시각화

## 라이선스

SPDX-License-Identifier: Apache-2.0

## 기여

프로젝트에 기여하고 싶으시다면, 먼저 이슈를 생성하거나 문서를 검토해주세요.

---

**프로젝트**: ARGO  
**버전**: 1.0  
**최종 업데이트**: 2025-12-08
