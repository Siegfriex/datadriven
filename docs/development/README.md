# Development Documents (개발 문서)

**위치**: `docs/development/`

## 문서 목록

| 문서 | 역할 | 핵심 문서 참조 |
|------|------|--------------|
| **ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md** | 백엔드 개발 세부 명세 | TSD 섹션 3 |
| **ARGO_DESIGN_DEVELOPMENT_SPEC.md** | 프론트엔드 디자인 명세 | TSD 섹션 4 |
| **ARGO_API_SPECIFICATION.yaml** | OpenAPI 3.0 명세서 | API_COMPLETE_SPECIFICATION |

## 사용 목적

- **백엔드 API 개발** 시 스키마/규칙 참조
- **프론트엔드 개발** 시 디자인 명세 참조
- **Swagger UI/코드 생성** 시 YAML 사용
- **타입 일치성 검증** 시 참조

## 핵심 개발 규칙

### API 스키마
- JSON-LD 형식 필수
- ID 형식: `argo://{entity_type}/{entity_id}`
- 모든 Artist 응답에 `coordinates_3d` 필수

### 프론트엔드
- React 18 + TypeScript + Vite
- Three.js r181 + React Three Fiber
- 60 FPS 렌더링 목표

---

**참조**: 모든 개발 정보는 `docs/ARGO_TSD_Final.md` 및 `docs/ARGO_API_COMPLETE_SPECIFICATION.md`와 연계됩니다.
