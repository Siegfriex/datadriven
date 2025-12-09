# ARGO Antigravity IDE 백엔드 개발 가이드라인
## Backend Development Specification for Antigravity IDE

**작성일**: 2025-12-09  
**버전**: 1.0  
**프로젝트 ID**: artdrive1208  
**상태**: 최종 확정  
**대상**: Antigravity IDE, 백엔드 개발자

---

## 📋 목차

1. [문서 개요 및 목적](#1-문서-개요-및-목적)
2. [문서 참조 관계](#2-문서-참조-관계)
3. [Antigravity IDE 사용 가이드](#3-antigravity-ide-사용-가이드)
4. [API 스키마 명시](#4-api-스키마-명시)
5. [ID 매핑 규칙](#5-id-매핑-규칙)
6. [JSON-LD 형식 명시](#6-json-ld-형식-명시)
7. [에러 응답 형식](#7-에러-응답-형식)
8. [CORS 및 인증 설정](#8-cors-및-인증-설정)
9. [타입 일치성 보장 가이드](#9-타입-일치성-보장-가이드)
10. [좌표 계산 로직](#10-좌표-계산-로직)
11. [통합 테스트 체크리스트](#11-통합-테스트-체크리스트)

---

## 1. 문서 개요 및 목적

### 1.1 문서의 목적

이 문서는 **Antigravity IDE에서 백엔드 개발을 수행할 때 필수 참조할 세부명세서**입니다. 

**주요 목적:**
- API 필드명, 타입, 스키마를 명시적으로 정의하여 프론트엔드-백엔드 간 타입 불일치 위험 제거
- ID 매핑 규칙 (`argo://` URI 형식) 명시로 일관된 식별자 사용 보장
- 다른 문서들과의 참조관계 명확히 표시하여 개발 시 올바른 문서 참조 유도
- 리스크 헷징을 위한 구체적 가이드라인 제공

### 1.2 사용 대상

- **Antigravity IDE**: 백엔드 코드 자동 생성 시 이 문서를 우선 참조
- **백엔드 개발자**: FastAPI + Python 3.10+ 개발 시 필수 참조
- **프론트엔드 개발자**: API 응답 형식 확인 시 참조

### 1.3 프로젝트 정보

- **프로젝트 이름**: ARTDRIVE
- **프로젝트 ID**: artdrive1208
- **리전**: asia-northeast3 (서울)
- **초기 API Base URL**: `https://artdrive1208-api-xxx.run.app/v1`
- **향후 커스텀 도메인**: `https://api.argo.art/v1`

---

## 2. 문서 참조 관계

이 문서는 다음 문서들과 밀접하게 연관되어 있습니다. 개발 시 반드시 함께 참조하세요.

### 2.1 참조 문서 목록

| 문서명 | 경로 | 역할 | 주요 참조 섹션 |
|--------|------|------|----------------|
| **OpenAPI 명세서** | `docs/ARGO_API_SPECIFICATION.yaml` | API 엔드포인트 정의, 요청/응답 스키마 | `components/schemas/*`, `paths/*` |
| **데이터베이스 스키마** | `docs/ARGO_Final_Schema.md` | Neo4j 노드/관계 구조, 필드 정의 | 섹션 2 (엔터티 상세 정의) |
| **기술 명세서** | `docs/ARGO_TSD_Final.md` | API 응답 형식, JSON-LD 규칙 | 섹션 3.3 (응답 스키마), 섹션 3.4 (버전 관리) |
| **소프트웨어 요구사항** | `docs/ARGO_SRD_Final.md` | 기능 명세, KPI, 성능 목표 | 섹션 6 (공개 API), 섹션 6.4 (인증) |
| **프론트엔드 타입** | `types/argo.ts` | TypeScript 타입 정의 | 모든 인터페이스 (타입 일치성 검증) |

### 2.2 문서 간 참조 흐름

```
ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md (이 문서)
    ↓
    ├─→ ARGO_API_SPECIFICATION.yaml
    │   └─→ API 엔드포인트 스키마 참조
    │
    ├─→ ARGO_Final_Schema.md
    │   └─→ Neo4j 데이터베이스 구조 참조
    │
    ├─→ ARGO_TSD_Final.md
    │   └─→ JSON-LD 형식 규칙 참조
    │
    ├─→ ARGO_SRD_Final.md
    │   └─→ 기능 명세 및 KPI 참조
    │
    └─→ types/argo.ts
        └─→ 프론트엔드 타입 일치성 검증
```

### 2.3 개발 시 참조 순서

1. **이 문서 (ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md)** - 필수 참조
2. `ARGO_API_SPECIFICATION.yaml` - API 엔드포인트 스키마 확인
3. `ARGO_Final_Schema.md` - 데이터베이스 구조 확인
4. `types/argo.ts` - 프론트엔드 타입과 일치성 검증

---

## 3. Antigravity IDE 사용 가이드

### 3.1 OpenAPI 명세서 입력

**중요**: Antigravity IDE에서 백엔드 코드를 생성할 때는 반드시 `docs/ARGO_API_SPECIFICATION.yaml` 파일을 입력으로 사용하세요.

**입력 방법:**
1. Antigravity IDE에서 새 프로젝트 생성
2. "Import OpenAPI Specification" 선택
3. `docs/ARGO_API_SPECIFICATION.yaml` 파일 업로드 또는 경로 지정
4. Pydantic 모델 자동 생성 옵션 활성화

**예상 결과:**
- FastAPI 라우터 자동 생성
- Pydantic 모델 자동 생성 (OpenAPI 스키마 기반)
- 요청/응답 검증 로직 자동 생성

### 3.2 Pydantic 모델 자동 생성 가이드

Antigravity IDE가 생성하는 Pydantic 모델은 다음 규칙을 따라야 합니다:

**필드명 규칙:**
- **snake_case 필수**: 모든 필드명은 snake_case 사용
- 예: `artist_id`, `inst_score`, `coordinates_3d`

**타입 매핑:**
- OpenAPI `string` → Python `str`
- OpenAPI `number` (format: float) → Python `float`
- OpenAPI `integer` → Python `int`
- OpenAPI `boolean` → Python `bool`
- OpenAPI `array` → Python `List[T]`
- OpenAPI `object` → Python Pydantic 모델

**필수/선택 필드:**
- OpenAPI `required` 배열에 포함된 필드 → Pydantic `Field(...)` (필수)
- 포함되지 않은 필드 → `Optional[T]` 또는 기본값 설정

### 3.3 환경변수 설정

**GCP Secret Manager 연동:**

```python
# 환경변수 로드 예제
import os
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    """GCP Secret Manager에서 시크릿 가져오기"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/artdrive1208/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# 환경변수 설정
NEO4J_URI = get_secret("neo4j-uri")
NEO4J_USER = get_secret("neo4j-user")
NEO4J_PASSWORD = get_secret("neo4j-password")
GEMINI_API_KEY = get_secret("gemini-api-key")
```

**로컬 개발 환경:**
- `.env` 파일 사용 (프로덕션에서는 Secret Manager 사용)

### 3.4 의존성 버전 관리

**requirements.txt 예제:**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
neo4j==5.14.0
py2neo==2021.2.4
redis==5.0.1
google-cloud-secret-manager==2.18.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
```

**주의사항:**
- Pydantic 2.x 사용 필수 (JSON-LD 변환 미들웨어 호환성)
- FastAPI 0.104+ 사용 (최신 기능 지원)

---

## 4. API 스키마 명시

이 섹션에서는 각 엔터티별로 상세한 스키마를 정의합니다. **모든 필드명은 정확히 일치해야 하며, 타입과 제약조건을 반드시 준수해야 합니다.**

### 4.1 Artist 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Artist`
- 프론트엔드 타입: `types/argo.ts` → `interface Artist`
- 데이터베이스 스키마: `ARGO_Final_Schema.md` → 섹션 2.1

#### 4.1.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 | 프론트엔드 매핑 |
|--------|------------|-----------|----------|--------------|------|----------------|
| `@context` | `str` | `string` | 필수 | `"https://schema.org/"` | `"https://schema.org/"` | - |
| `@type` | `str` | `string` | 필수 | `"Person"` | `"Person"` | - |
| `@id` | `str` | `string` | 필수 | `argo://artist/{artist_id}` 형식 | `"argo://artist/artist_001"` | - |
| `identifier` | `dict` | `object` | 필수 | PropertyValue 타입 | `{"@type": "PropertyValue", "propertyID": "ARGO", "value": "artist_001"}` | - |
| `name` | `str` | `string` | 필수 | - | `"작가 A"` | `artist.name` |
| `alternateName` | `Optional[str]` | `string` | 선택 | - | `"Artist A"` | `artist.alternativeName` |
| `birthDate` | `Optional[str]` | `string` | 선택 | YYYY 형식 | `"1975"` | `artist.birth_year` (변환 필요) |
| `url` | `Optional[str]` | `string` | 선택 | URI 형식 | `"https://example.com/artist_a"` | `artist.url` |
| `argo:scores` | `dict` | `object` | 필수 | - | 아래 참조 | `artist.scores` |
| `argo:inst_score` | `float` | `number` | 필수 | 0-100 | `82.5` | `artist.scores.inst_score` |
| `argo:acad_score` | `float` | `number` | 필수 | 0-100 | `68.0` | `artist.scores.acad_score` |
| `argo:media_score` | `float` | `number` | 필수 | 0-100 | `75.0` | `artist.scores.media_score` |
| `argo:network_score` | `float` | `number` | 필수 | 0-100 | `71.0` | `artist.scores.network_score` |
| `argo:composite_score` | `float` | `number` | 필수 | 0-100 | `74.15` | `artist.scores.composite_score` |
| `argo:composite_confidence` | `Optional[float]` | `number` | 선택 | 0-1 | `0.92` | - |
| `argo:structuralist_analysis` | `Optional[dict]` | `object` | 선택 | - | 아래 참조 | `artist.structuralist_analysis` |
| `argo:coordinates_3d` | `dict` | `object` | 필수 | - | 아래 참조 | `artist.coordinates_3d` |
| `argo:cluster` | `Optional[dict]` | `object` | 선택 | - | 아래 참조 | - |
| `collaborators` | `Optional[List[str]]` | `array` | 선택 | 하위 호환성 유지 | `["artist_002", "artist_003"]` | `artist.collaborators` |
| `collaborations` | `Optional[List[dict]]` | `array` | 선택 | Collaboration 객체 배열 | 아래 참조 | `artist.collaborations` |
| `institutions` | `Optional[List[dict]]` | `array` | 선택 | Institution 객체 배열 | 아래 참조 | `artist.institutions` |
| `exhibitions` | `Optional[List[dict]]` | `array` | 선택 | Exhibition 객체 배열 | 아래 참조 | `artist.exhibitions` |

**중요 사항:**
- `@context`, `@type`, `@id`는 JSON-LD 필수 필드입니다. 반드시 포함해야 합니다.
- `argo:` 네임스페이스는 ARGO 커스텀 필드에 사용됩니다.
- `birthDate`는 문자열 형식 (YYYY)이며, 프론트엔드에서는 `birth_year` (number)로 변환됩니다.
- **관계 데이터 필드**: `collaborations`, `institutions`, `exhibitions`는 프론트엔드에서 연결선 시각화에 사용됩니다.
- **하위 호환성**: `collaborators` 배열도 지원하되, `collaborations` 배열을 우선 사용합니다.

#### 4.1.2 argo:scores 객체 구조

```python
{
    "argo:inst_score": float,      # 0-100
    "argo:acad_score": float,      # 0-100
    "argo:media_score": float,     # 0-100
    "argo:network_score": float,   # 0-100
    "argo:composite_score": float, # 0-100
    "argo:composite_confidence": Optional[float]  # 0-1
}
```

#### 4.1.3 argo:structuralist_analysis 객체 구조

**참조**: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/StructuralistAnalysis`

```python
{
    "dominant_capital": str,  # enum: "institutional" | "academic" | "media" | "network"
    "capital_composition": {
        "institutional_ratio": float,  # 0-1
        "academic_ratio": float,       # 0-1
        "media_ratio": float,          # 0-1
        "network_ratio": float         # 0-1
    },
    "structural_position": {
        "field_quadrant": str,  # enum: "Q1_established" | "Q2_academic_elite" | "Q3_media_star" | "Q4_emerging"
        "position_stability": float,    # 0-1
        "mobility_potential": float     # 0-1
    },
    "algorithm_version": str,
    "weights_applied": {
        "inst": float,
        "acad": float,
        "media": float,
        "network": float
    },
    "theoretical_basis": str
}
```

#### 4.1.4 argo:coordinates_3d 객체 구조

**중요**: 이 필드는 프론트엔드에서 3D 갤럭시 렌더링에 필수입니다. 반드시 포함해야 합니다.

```python
{
    "argo:x": float,        # inst_score 정규화 (-30 ~ 30)
    "argo:y": float,        # acad_score 정규화 (-30 ~ 30)
    "argo:z": float,        # media_score 정규화 (-30 ~ 30)
    "argo:radius": float,   # network_score 기반 (10 + score/5)
    "computed_at": Optional[str],  # ISO 8601 형식
    "algorithm": Optional[str]      # "normalize_v1" 등
}
```

**계산 로직**: 섹션 10 참조

#### 4.1.5 관계 데이터 객체 구조

**중요**: 프론트엔드에서 연결선 시각화에 사용되므로, 관계 데이터는 반드시 올바른 형식으로 제공해야 합니다.

**collaborations 배열:**
```python
[
    {
        "artist_id": str,      # 협력 작가 ID
        "strength": float      # 관계 강도 (0-1 범위, 0.3 이상만 시각화됨)
    }
]
```

**institutions 배열:**
```python
[
    {
        "institution_id": str,  # 기관 ID
        "name": str,            # 기관명
        "type": Optional[str]   # 기관 타입 (예: "museum", "gallery")
    }
]
```

**exhibitions 배열:**
```python
[
    {
        "exhibition_id": str,   # 전시 ID
        "name": str,            # 전시명
        "year": Optional[int]   # 전시 연도
    }
]
```

**주의사항:**
- `collaborations` 배열의 `strength` 값이 0.3 미만인 경우 프론트엔드에서 연결선이 표시되지 않습니다.
- `collaborators` 배열은 하위 호환성을 위해 유지하되, `collaborations` 배열을 우선 사용합니다.

#### 4.1.6 Pydantic 모델 예제

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Scores(BaseModel):
    inst_score: float = Field(..., ge=0, le=100, description="제도 레이어 점수")
    acad_score: float = Field(..., ge=0, le=100, description="학술 레이어 점수")
    media_score: float = Field(..., ge=0, le=100, description="담론 레이어 점수")
    network_score: float = Field(..., ge=0, le=100, description="네트워크 레이어 점수")
    composite_score: float = Field(..., ge=0, le=100, description="복합 점수")
    composite_confidence: Optional[float] = Field(None, ge=0, le=1)

class Coordinates3D(BaseModel):
    x: float = Field(..., description="inst_score 정규화 (-30 ~ 30)")
    y: float = Field(..., description="acad_score 정규화 (-30 ~ 30)")
    z: float = Field(..., description="media_score 정규화 (-30 ~ 30)")
    radius: float = Field(..., description="network_score 기반 (10 + score/5)")
    computed_at: Optional[str] = None
    algorithm: Optional[str] = None

class StructuralistAnalysis(BaseModel):
    dominant_capital: str = Field(..., pattern="^(institutional|academic|media|network)$")
    capital_composition: dict
    structural_position: dict
    algorithm_version: str
    weights_applied: dict
    theoretical_basis: str

class Collaboration(BaseModel):
    """협력 관계 엔터티"""
    artist_id: str = Field(..., description="협력 작가 ID")
    strength: float = Field(..., ge=0, le=1, description="관계 강도 (0-1 범위, 0.3 이상만 시각화)")

class Institution(BaseModel):
    """기관 정보 엔터티 (Artist 내부 사용)"""
    institution_id: str = Field(..., description="기관 ID")
    name: str = Field(..., description="기관명")
    type: Optional[str] = Field(None, description="기관 타입 (예: 'museum', 'gallery')")

class Exhibition(BaseModel):
    """전시 정보 엔터티 (Artist 내부 사용)"""
    exhibition_id: str = Field(..., description="전시 ID")
    name: str = Field(..., description="전시명")
    year: Optional[int] = Field(None, description="전시 연도")

class Artist(BaseModel):
    # JSON-LD 필수 필드
    context: str = Field(default="https://schema.org/", alias="@context")
    type: str = Field(default="Person", alias="@type")
    id: str = Field(..., alias="@id", pattern="^argo://artist/")
    
    # Schema.org 필드
    identifier: dict
    name: str
    alternateName: Optional[str] = None
    birthDate: Optional[str] = None
    url: Optional[str] = None
    
    # ARGO 커스텀 필드
    scores: dict  # argo:scores
    structuralist_analysis: Optional[dict] = None  # argo:structuralist_analysis
    coordinates_3d: dict  # argo:coordinates_3d
    cluster: Optional[dict] = None  # argo:cluster
    
    # 관계 데이터 필드 (프론트엔드 연결선 시각화용)
    collaborators: Optional[List[str]] = None  # 하위 호환성 유지 (작가 ID 배열)
    collaborations: Optional[List[Collaboration]] = None  # 협력 관계 배열 (우선 사용)
    institutions: Optional[List[Institution]] = None  # 소속 기관 배열
    exhibitions: Optional[List[Exhibition]] = None  # 전시 참여 배열
    
    class Config:
        populate_by_name = True  # @context와 context 모두 허용
```

### 4.2 Institution 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Institution`
- 데이터베이스 스키마: `ARGO_Final_Schema.md` → 섹션 2.2

#### 4.2.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 |
|--------|------------|-----------|----------|--------------|------|
| `@context` | `str` | `string` | 필수 | `"https://schema.org/"` | `"https://schema.org/"` |
| `@type` | `str` | `string` | 필수 | `"Organization"` | `"Organization"` |
| `@id` | `str` | `string` | 필수 | `argo://institution/{inst_id}` | `"argo://institution/inst_001"` |
| `name` | `str` | `string` | 필수 | - | `"국립현대미술관"` |
| `url` | `Optional[str]` | `string` | 선택 | URI 형식 | `"https://www.mmca.go.kr"` |
| `address` | `Optional[dict]` | `object` | 선택 | PostalAddress 타입 | `{"@type": "PostalAddress", "addressLocality": "Seoul"}` |

### 4.3 Exhibition 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Exhibition`
- 데이터베이스 스키마: `ARGO_Final_Schema.md` → 섹션 2.3

#### 4.3.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 |
|--------|------------|-----------|----------|--------------|------|
| `@context` | `str` | `string` | 필수 | `"https://schema.org/"` | `"https://schema.org/"` |
| `@type` | `str` | `string` | 필수 | `"Event"` | `"Event"` |
| `@id` | `str` | `string` | 필수 | `argo://exhibition/{exh_id}` | `"argo://exhibition/exh_001"` |
| `name` | `str` | `string` | 필수 | - | `"한국 추상미술의 맥락"` |
| `startDate` | `str` | `string` | 필수 | YYYY-MM-DD 형식 | `"2024-03-15"` |
| `endDate` | `str` | `string` | 필수 | YYYY-MM-DD 형식 | `"2024-06-30"` |
| `location` | `Optional[dict]` | `object` | 선택 | Place 타입 | `{"@type": "Place", "name": "국립현대미술관"}` |

### 4.4 Transaction 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Transaction`
- 데이터베이스 스키마: `ARGO_Final_Schema.md` → 섹션 2.4

#### 4.4.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 |
|--------|------------|-----------|----------|--------------|------|
| `trans_id` | `str` | `string` | 필수 | - | `"trans_001"` |
| `artist_id` | `str` | `string` | 필수 | - | `"artist_001"` |
| `artwork_id` | `Optional[str]` | `string` | 선택 | - | `"work_001"` |
| `price_krw` | `int` | `integer` | 필수 | 양수 | `45000000` |
| `transaction_date` | `str` | `string` | 필수 | YYYY-MM-DD 형식 | `"2024-03-10"` |
| `transaction_type` | `str` | `string` | 필수 | enum | `"auction"` |
| `venue` | `Optional[str]` | `string` | 선택 | - | `"서울옥션"` |
| `market_analysis` | `Optional[dict]` | `object` | 선택 | - | `{"anomaly_score": 0.75, "is_outlier": true}` |

### 4.5 Cluster 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Cluster`
- 프론트엔드 타입: `types/argo.ts` → `interface Cluster`
- 데이터베이스 스키마: `ARGO_Final_Schema.md` → 섹션 2.6

#### 4.5.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 | 프론트엔드 매핑 |
|--------|------------|-----------|----------|--------------|------|----------------|
| `cluster_id` | `str` | `string` | 필수 | - | `"cluster_001"` | `cluster.cluster_id` |
| `cluster_type` | `str` | `string` | 필수 | enum: `"louvain"`, `"geographic"`, `"genre"` | `"louvain"` | - |
| `name` | `str` | `string` | 필수 | - | `"서울 모노크롬 화가 그룹"` | `cluster.name` |
| `member_count` | `int` | `integer` | 필수 | 양수 | `15` | - |
| `cohesion_score` | `float` | `number` | 필수 | 0-1 | `0.85` | - |
| `center` | `dict` | `object` | 필수 | - | `{"x": 2.5, "y": -1.2, "z": 0.8}` | `cluster.center` |
| `radius` | `float` | `number` | 필수 | 양수 | `12.5` | `cluster.radius` |
| `segment_ids` | `List[str]` | `array` | 선택 | - | `["segment_001", "segment_002"]` | `cluster.segment_ids` |
| `artist_ids` | `List[str]` | `array` | 선택 | - | `["artist_001", "artist_002"]` | `cluster.artist_ids` |

### 4.6 Collaboration 엔터티 (관계 데이터)

**참조 문서:**
- 프론트엔드 타입: `types/argo.ts` → `interface Collaboration`
- 사용 위치: `Artist.collaborations` 배열 내부

#### 4.6.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 | 프론트엔드 매핑 |
|--------|------------|-----------|----------|--------------|------|----------------|
| `artist_id` | `str` | `string` | 필수 | - | `"artist_002"` | `collab.artist_id` |
| `strength` | `float` | `number` | 필수 | 0-1 범위 | `0.65` | `collab.strength` |

**중요 사항:**
- `strength` 값이 0.3 미만인 경우 프론트엔드에서 연결선이 표시되지 않습니다.
- 프론트엔드 `ArtistEdges.tsx`에서 `strength >= 0.3` 조건으로 필터링됩니다.

### 4.7 Institution 엔터티 (관계 데이터)

**참조 문서:**
- 프론트엔드 타입: `types/argo.ts` → `interface Institution`
- 사용 위치: `Artist.institutions` 배열 내부

#### 4.7.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 | 프론트엔드 매핑 |
|--------|------------|-----------|----------|--------------|------|----------------|
| `institution_id` | `str` | `string` | 필수 | - | `"inst_001"` | `inst.institution_id` |
| `name` | `str` | `string` | 필수 | - | `"국립현대미술관"` | `inst.name` |
| `type` | `Optional[str]` | `string` | 선택 | - | `"museum"` | `inst.type` |

**참고**: 이 엔터티는 Artist 내부에서 관계 데이터로 사용되며, 독립적인 Institution 엔터티(섹션 4.2)와는 다른 구조입니다.

### 4.8 Exhibition 엔터티 (관계 데이터)

**참조 문서:**
- 프론트엔드 타입: `types/argo.ts` → `interface Exhibition`
- 사용 위치: `Artist.exhibitions` 배열 내부

#### 4.8.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 | 프론트엔드 매핑 |
|--------|------------|-----------|----------|--------------|------|----------------|
| `exhibition_id` | `str` | `string` | 필수 | - | `"exh_001"` | `exh.exhibition_id` |
| `name` | `str` | `string` | 필수 | - | `"한국 추상미술의 맥락"` | `exh.name` |
| `year` | `Optional[int]` | `integer` | 선택 | - | `2024` | `exh.year` |

**참고**: 이 엔터티는 Artist 내부에서 관계 데이터로 사용되며, 독립적인 Exhibition 엔터티(섹션 4.3)와는 다른 구조입니다.

### 4.9 Artwork 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/Artwork`

#### 4.9.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 |
|--------|------------|-----------|----------|--------------|------|
| `work_id` | `str` | `string` | 필수 | - | `"work_001"` |
| `title` | `str` | `string` | 필수 | - | `"무제 (1990)"` |
| `creation_year` | `Optional[int]` | `integer` | 선택 | - | `1990` |
| `medium` | `Optional[str]` | `string` | 선택 | - | `"acrylic on canvas"` |
| `dimensions` | `Optional[dict]` | `object` | 선택 | - | `{"height_cm": 200, "width_cm": 150}` |
| `estimated_value_usd` | `Optional[int]` | `integer` | 선택 | 양수 | `45000` |

### 4.10 NetworkGraph 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/NetworkGraph`

#### 4.10.1 필드 정의

```python
{
    "nodes": [
        {
            "id": str,        # artist_id 또는 inst_id
            "name": str,
            "score": float,
            "type": str       # "artist" | "institution"
        }
    ],
    "edges": [
        {
            "source": str,    # 노드 ID
            "target": str,    # 노드 ID
            "strength": float, # 0-1 범위
            "type": str       # 관계 타입 (예: "COLLABORATED_WITH")
        }
    ]
}
```

### 4.8 GalaxySnapshot 엔터티

**참조 문서:**
- OpenAPI: `ARGO_API_SPECIFICATION.yaml` → `components/schemas/GalaxySnapshot`
- 프론트엔드 타입: `types/argo.ts` → `interface GalaxySnapshot`

#### 4.8.1 필드 정의

| 필드명 | Python 타입 | JSON 타입 | 필수 여부 | 범위/제약조건 | 예제 | 프론트엔드 매핑 |
|--------|------------|-----------|----------|--------------|------|----------------|
| `snapshot_id` | `str` | `string` | 필수 | - | `"snapshot_20251208"` | `snapshot.snapshot_id` |
| `snapshot_date` | `str` | `string` | 필수 | ISO 8601 형식 | `"2025-12-08T00:00:00Z"` | `snapshot.timestamp` |
| `galaxy_statistics` | `dict` | `object` | 필수 | - | 아래 참조 | - |
| `total_artists` | `int` | `integer` | 필수 | 양수 | `100` | - |
| `total_institutions` | `int` | `integer` | 필수 | 양수 | `25` | - |
| `total_exhibitions` | `int` | `integer` | 필수 | 양수 | `180` | - |
| `total_artworks` | `int` | `integer` | 필수 | 양수 | `450` | - |
| `total_transactions` | `int` | `integer` | 필수 | 양수 | `1200` | - |
| `total_clusters` | `int` | `integer` | 필수 | 양수 | `9` | - |
| `structure_metrics` | `dict` | `object` | 필수 | - | 아래 참조 | - |
| `entropy` | `float` | `number` | 필수 | 0-1 | `0.72` | - |
| `density` | `float` | `number` | 필수 | 0-1 | `0.18` | - |
| `clustering_coefficient` | `float` | `number` | 필수 | 0-1 | `0.62` | - |
| `average_path_length` | `float` | `number` | 필수 | 양수 | `3.2` | - |
| `diameter` | `int` | `integer` | 필수 | 양수 | `6` | - |

---

## 5. ID 매핑 규칙

### 5.1 argo:// URI 형식

모든 엔터티의 `@id` 필드는 `argo://` URI 형식을 사용합니다.

**형식:**
```
argo://{entity_type}/{entity_id}
```

**예제:**
- Artist: `argo://artist/artist_001`
- Institution: `argo://institution/inst_001`
- Exhibition: `argo://exhibition/exh_001`
- Cluster: `argo://cluster/cluster_001`

### 5.2 엔터티별 ID 매핑 규칙

| 엔터티 타입 | @id 형식 | entity_id 예제 | 참조 필드 |
|------------|---------|---------------|----------|
| Artist | `argo://artist/{artist_id}` | `artist_001` | `artist_id` |
| Institution | `argo://institution/{inst_id}` | `inst_001` | `inst_id` |
| Exhibition | `argo://exhibition/{exh_id}` | `exh_001` | `exh_id` |
| Transaction | `argo://transaction/{trans_id}` | `trans_001` | `trans_id` |
| Cluster | `argo://cluster/{cluster_id}` | `cluster_001` | `cluster_id` |
| Artwork | `argo://artwork/{work_id}` | `work_001` | `work_id` |

### 5.3 ID 생성 규칙

**Neo4j 노드 ID:**
- Neo4j 노드의 `artist_id`, `inst_id` 등의 속성값을 그대로 사용
- 형식: `{entity_type}_{sequential_number}`
- 예: `artist_001`, `inst_001`, `exh_001`

**@id 필드 생성 예제:**

```python
def generate_argo_id(entity_type: str, entity_id: str) -> str:
    """ARGO URI ID 생성"""
    return f"argo://{entity_type}/{entity_id}"

# 사용 예제
artist_id = "artist_001"
argo_id = generate_argo_id("artist", artist_id)
# 결과: "argo://artist/artist_001"
```

### 5.4 JSON-LD @id 필드 사용

모든 API 응답에서 엔터티의 `@id` 필드는 위 규칙을 따라야 합니다.

**예제:**
```json
{
  "@context": "https://schema.org/",
  "@type": "Person",
  "@id": "argo://artist/artist_001",
  "name": "작가 A"
}
```

---

## 6. JSON-LD 형식 명시

### 6.1 JSON-LD 필수 필드

모든 API 응답은 JSON-LD 형식을 따라야 합니다. 다음 필드는 반드시 포함해야 합니다:

1. **@context**: `"https://schema.org/"`
2. **@type**: Schema.org 타입 (Person, Organization, Event 등)
3. **@id**: `argo://` URI 형식

### 6.2 ARGO 커스텀 필드 네임스페이스

ARGO 프로젝트의 커스텀 필드는 `argo:` 네임스페이스를 사용합니다.

**예제:**
```json
{
  "@context": "https://schema.org/",
  "@type": "Person",
  "@id": "argo://artist/artist_001",
  "name": "작가 A",
  "argo:scores": {
    "argo:inst_score": 82,
    "argo:acad_score": 68
  },
  "argo:coordinates_3d": {
    "argo:x": 2.34,
    "argo:y": -1.23,
    "argo:z": 0.67,
    "argo:radius": 15
  }
}
```

### 6.3 JSON-LD 변환 미들웨어

FastAPI에서 JSON-LD 형식으로 변환하는 미들웨어 예제:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import json

@app.middleware("http")
async def add_jsonld_context(request: Request, call_next):
    response = await call_next(request)
    
    if response.headers.get("content-type") == "application/json":
        # 응답 본문 파싱
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        data = json.loads(body.decode())
        
        # JSON-LD 필수 필드 추가 (없는 경우)
        if isinstance(data, dict):
            if "@context" not in data:
                data["@context"] = "https://schema.org/"
            if "@type" not in data:
                # 엔터티 타입에 따라 자동 설정
                if "artist_id" in data:
                    data["@type"] = "Person"
                elif "inst_id" in data:
                    data["@type"] = "Organization"
                elif "exh_id" in data:
                    data["@type"] = "Event"
            
            if "@id" not in data:
                # 엔터티 ID에 따라 자동 생성
                if "artist_id" in data:
                    data["@id"] = f"argo://artist/{data['artist_id']}"
                elif "inst_id" in data:
                    data["@id"] = f"argo://institution/{data['inst_id']}"
                elif "exh_id" in data:
                    data["@id"] = f"argo://exhibition/{data['exh_id']}"
        
        # 변환된 데이터로 응답 재생성
        return JSONResponse(content=data)
    
    return response
```

### 6.4 참조 문서

- `ARGO_TSD_Final.md` 섹션 3.3: 응답 스키마 (JSON-LD) 상세 설명
- `ARGO_API_SPECIFICATION.yaml`: JSON-LD 예제 포함

---

## 7. 에러 응답 형식

### 7.1 표준 에러 응답 스키마

모든 에러 응답은 다음 형식을 따라야 합니다:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 친화적 에러 메시지",
    "details": "상세 기술 정보 (개발자용)",
    "timestamp": "2025-12-08T18:30:00Z",
    "request_id": "req_123456789",
    "documentation": "https://artdrive1208-api-xxx.run.app/docs/errors/ERROR_CODE"
  }
}
```

### 7.2 HTTP 상태 코드 매핑

| HTTP 상태 코드 | 에러 코드 | 설명 | 예제 |
|--------------|----------|------|------|
| 400 | `INVALID_PARAMETER` | 잘못된 요청 파라미터 | 필수 파라미터 누락, 타입 불일치 |
| 401 | `UNAUTHORIZED` | 인증 실패 | API 키 없음, 만료된 토큰 |
| 403 | `FORBIDDEN` | 권한 없음 | 프리미엄 계층 필요 |
| 404 | `NOT_FOUND` | 리소스를 찾을 수 없음 | 존재하지 않는 artist_id |
| 429 | `RATE_LIMIT_EXCEEDED` | 레이트 제한 초과 | 월간 요청 한도 초과 |
| 500 | `INTERNAL_ERROR` | 내부 서버 오류 | Neo4j 쿼리 실패 |
| 503 | `SERVICE_UNAVAILABLE` | 서비스 일시 중단 | 데이터베이스 연결 실패 |

### 7.3 에러 코드 목록

**참조**: `ARGO_API_SPECIFICATION.yaml` → `components/responses/*`

주요 에러 코드:
- `INVALID_PARAMETER`: 요청 파라미터 오류
- `UNAUTHORIZED`: 인증 실패
- `FORBIDDEN`: 권한 없음
- `NOT_FOUND`: 리소스 없음
- `RATE_LIMIT_EXCEEDED`: 레이트 제한 초과
- `INTERNAL_ERROR`: 내부 서버 오류
- `SERVICE_UNAVAILABLE`: 서비스 일시 중단

### 7.4 에러 응답 구현 예제

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid

def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: str = None,
    request_id: str = None
) -> JSONResponse:
    """표준 에러 응답 생성"""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": details or "",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "request_id": request_id or str(uuid.uuid4()),
                "documentation": f"https://artdrive1208-api-xxx.run.app/docs/errors/{error_code}"
            }
        }
    )

# 사용 예제
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return create_error_response(
            status_code=404,
            error_code="NOT_FOUND",
            message="요청한 작가를 찾을 수 없습니다",
            details=f"artist_id '{request.path_params.get('artist_id')}'에 해당하는 작가가 존재하지 않습니다"
        )
    # 기타 에러 처리...
```

---

## 8. CORS 및 인증 설정

### 8.1 CORS 설정

프론트엔드 (Firebase Hosting)와 백엔드 (Cloud Run)가 다른 도메인에 있으므로 CORS 설정이 필수입니다.

**허용 Origin:**
- `https://artdrive1208.web.app` (Firebase Hosting)
- `https://argo.art` (향후 커스텀 도메인)
- `http://localhost:5173` (로컬 개발 환경)

**FastAPI CORS 설정:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://artdrive1208.web.app",
        "https://argo.art",
        "http://localhost:5173",  # 개발 환경
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

**환경변수로 관리 (권장):**

```python
import os

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://artdrive1208.web.app,https://argo.art,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

### 8.2 인증 설정

**참조**: `ARGO_SRD_Final.md` 섹션 6.4

**인증 방식:**
- JWT Bearer Token
- Header: `Authorization: Bearer <token>`
- 또는 Query: `?api_key=<api_key>` (선택사항)

**FastAPI 인증 구현:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT 토큰 검증"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# 사용 예제
@app.get("/api/artists")
async def get_artists(token: dict = Depends(verify_token)):
    # 인증된 사용자만 접근 가능
    return {"artists": []}
```

**레이트 제한:**
- 무료 계층: 월 10,000 요청 (1,000/일)
- 프리미엄 계층: 월 500,000 요청 (16,666/일)
- 기관 계층: 무제한 (커스텀)

---

## 9. 타입 일치성 보장 가이드

### 9.1 프론트엔드-백엔드 타입 매핑

프론트엔드 TypeScript 타입 (`types/argo.ts`)과 백엔드 Python Pydantic 모델이 일치해야 합니다.

#### 9.1.1 필드명 일치 규칙

**중요**: 모든 필드명은 **snake_case**를 사용합니다.

| 프론트엔드 (TypeScript) | 백엔드 (Python) | JSON 응답 |
|------------------------|----------------|-----------|
| `artist_id` | `artist_id` | `artist_id` |
| `inst_score` | `inst_score` | `argo:inst_score` |
| `coordinates_3d` | `coordinates_3d` | `argo:coordinates_3d` |
| `structuralist_analysis` | `structuralist_analysis` | `argo:structuralist_analysis` |

**주의사항:**
- 프론트엔드에서 `alternativeName` (camelCase)를 사용하지만, 백엔드에서는 `alternateName` (JSON-LD 표준)을 사용합니다.
- JSON 응답에서는 JSON-LD 표준 필드명을 사용합니다 (`alternateName`).

#### 9.1.2 타입 매핑 테이블

| TypeScript 타입 | Python 타입 | JSON 타입 | 변환 필요 여부 |
|----------------|------------|-----------|--------------|
| `string` | `str` | `string` | 없음 |
| `number` | `float` | `number` | 없음 |
| `number` (정수) | `int` | `integer` | 없음 |
| `boolean` | `bool` | `boolean` | 없음 |
| `string[]` | `List[str]` | `array` | 없음 |
| `Artist[]` | `List[Artist]` | `array` | 없음 |
| `{ x: number, y: number }` | `dict` | `object` | 없음 |

#### 9.1.3 특수 케이스

**birthDate (문자열) ↔ birth_year (숫자):**
- 백엔드 JSON 응답: `birthDate: "1975"` (문자열, YYYY 형식)
- 프론트엔드 타입: `birth_year?: number` (숫자)
- 변환: 프론트엔드에서 `birthDate`를 파싱하여 `birth_year`로 변환

**좌표 필드:**
- 백엔드 JSON 응답: `argo:coordinates_3d: { argo:x: 2.34, argo:y: -1.23, ... }`
- 프론트엔드 타입: `coordinates_3d: { x: number, y: number, ... }`
- 변환: 프론트엔드에서 `argo:` 네임스페이스 제거

### 9.2 타입 검증 방법

#### 9.2.1 백엔드 검증

Pydantic 모델을 사용하여 자동 검증:

```python
from pydantic import BaseModel, ValidationError

class Artist(BaseModel):
    artist_id: str
    name: str
    scores: dict
    
    class Config:
        # JSON-LD 필드명 허용
        populate_by_name = True

# 검증 예제
try:
    artist = Artist(**data)
except ValidationError as e:
    # 타입 불일치 에러 처리
    pass
```

#### 9.2.2 프론트엔드 검증

TypeScript 타입 체크:

```typescript
interface Artist {
  artist_id: string;
  name: string;
  scores: Scores;
}

// API 응답 타입 검증
const response = await fetch('/api/artists/artist_001');
const data: Artist = await response.json();

// 타입 검증
if (typeof data.artist_id !== 'string') {
  throw new Error('artist_id must be string');
}
```

### 9.3 자동화된 타입 검증

**API 계약 테스트:**
- Pact 또는 Contract Testing 도구 사용
- 프론트엔드와 백엔드 간 계약 검증

**참조 문서:**
- `types/argo.ts`: 프론트엔드 타입 정의
- `ARGO_API_SPECIFICATION.yaml`: OpenAPI 스키마 정의

---

## 10. 좌표 계산 로직

### 10.1 coordinates_3d 필드 필수성

**중요**: `coordinates_3d` 필드는 프론트엔드에서 3D 갤럭시 렌더링에 필수입니다. 반드시 포함해야 합니다.

### 10.2 계산 공식

좌표는 4가지 점수 (inst_score, acad_score, media_score, network_score)를 기반으로 계산됩니다.

**정규화 함수:**

```python
def normalize_score(score: float, min_score: float, max_score: float, target_min: float, target_max: float) -> float:
    """
    점수를 정규화하여 target 범위로 변환
    
    Args:
        score: 원본 점수 (0-100)
        min_score: 원본 최소값 (0)
        max_score: 원본 최대값 (100)
        target_min: 목표 최소값 (-30)
        target_max: 목표 최대값 (30)
    
    Returns:
        정규화된 점수
    """
    if max_score == min_score:
        return (target_min + target_max) / 2
    
    normalized = ((score - min_score) / (max_score - min_score)) * (target_max - target_min) + target_min
    return round(normalized, 2)
```

**좌표 계산:**

```python
def calculate_coordinates_3d(
    inst_score: float,
    acad_score: float,
    media_score: float,
    network_score: float
) -> dict:
    """
    3D 갤럭시 좌표 계산
    
    Args:
        inst_score: 제도 레이어 점수 (0-100)
        acad_score: 학술 레이어 점수 (0-100)
        media_score: 담론 레이어 점수 (0-100)
        network_score: 네트워크 레이어 점수 (0-100)
    
    Returns:
        coordinates_3d 딕셔너리
    """
    from datetime import datetime
    
    # x, y, z 좌표 계산 (-30 ~ 30 범위)
    x = normalize_score(inst_score, 0, 100, -30, 30)
    y = normalize_score(acad_score, 0, 100, -30, 30)
    z = normalize_score(media_score, 0, 100, -30, 30)
    
    # radius 계산 (10 + network_score / 5)
    radius = 10 + (network_score / 5)
    
    return {
        "argo:x": x,
        "argo:y": y,
        "argo:z": z,
        "argo:radius": round(radius, 2),
        "computed_at": datetime.utcnow().isoformat() + "Z",
        "algorithm": "normalize_v1"
    }
```

### 10.3 Pydantic 모델에 통합

```python
from pydantic import BaseModel, computed_field

class Artist(BaseModel):
    artist_id: str
    scores: dict
    
    @computed_field
    @property
    def coordinates_3d(self) -> dict:
        """좌표 자동 계산"""
        return calculate_coordinates_3d(
            inst_score=self.scores.get("inst_score", 0),
            acad_score=self.scores.get("acad_score", 0),
            media_score=self.scores.get("media_score", 0),
            network_score=self.scores.get("network_score", 0)
        )
```

### 10.4 프론트엔드 매핑

프론트엔드에서는 `argo:` 네임스페이스를 제거하여 사용합니다:

```typescript
// 백엔드 응답
{
  "argo:coordinates_3d": {
    "argo:x": 2.34,
    "argo:y": -1.23,
    "argo:z": 0.67,
    "argo:radius": 15
  }
}

// 프론트엔드 변환 후
{
  coordinates_3d: {
    x: 2.34,
    y: -1.23,
    z: 0.67,
    radius: 15
  }
}
```

**참조 문서:**
- `types/argo.ts` → `interface Coordinates3D`
- `ARGO_TSD_Final.md` 섹션 2.1.1: 좌표 계산 로직

---

## 11. 통합 테스트 체크리스트

### 11.1 API 계약 테스트

다음 항목들을 검증해야 합니다:

- [ ] 모든 엔드포인트가 OpenAPI 명세서와 일치하는가?
- [ ] 요청 파라미터 타입이 올바른가?
- [ ] 응답 스키마가 OpenAPI 명세서와 일치하는가?
- [ ] 필수 필드가 모두 포함되어 있는가?

### 11.2 타입 검증 테스트

- [ ] 프론트엔드 TypeScript 타입과 백엔드 응답이 일치하는가?
- [ ] 필드명이 snake_case로 일치하는가?
- [ ] 숫자 타입이 올바르게 변환되는가?
- [ ] 배열 타입이 올바르게 처리되는가?

### 11.3 JSON-LD 형식 검증 테스트

- [ ] 모든 응답에 `@context` 필드가 포함되어 있는가?
- [ ] 모든 응답에 `@type` 필드가 포함되어 있는가?
- [ ] 모든 응답에 `@id` 필드가 올바른 형식인가?
- [ ] ARGO 커스텀 필드가 `argo:` 네임스페이스를 사용하는가?

### 11.4 ID 매핑 검증 테스트

- [ ] 모든 엔터티의 `@id`가 `argo://` URI 형식인가?
- [ ] 엔터티 타입별 ID 형식이 올바른가?
- [ ] ID가 실제 엔터티 ID와 일치하는가?

### 11.5 좌표 계산 검증 테스트

- [ ] 모든 Artist 응답에 `coordinates_3d` 필드가 포함되어 있는가?
- [ ] 좌표 값이 올바른 범위 내에 있는가? (x, y, z: -30 ~ 30)
- [ ] radius 값이 올바르게 계산되었는가? (10 + network_score / 5)

### 11.6 CORS 검증 테스트

- [ ] 허용된 Origin에서 요청이 성공하는가?
- [ ] 허용되지 않은 Origin에서 요청이 차단되는가?
- [ ] OPTIONS 요청이 올바르게 처리되는가?

### 11.7 에러 응답 검증 테스트

- [ ] 에러 응답이 표준 형식을 따르는가?
- [ ] HTTP 상태 코드가 올바른가?
- [ ] 에러 코드가 명확한가?
- [ ] 에러 메시지가 사용자 친화적인가?

### 11.8 성능 검증 테스트

- [ ] API 응답 시간이 200ms 이하인가?
- [ ] 동시 100개 요청을 처리할 수 있는가?
- [ ] 동시 1000개 요청을 처리할 수 있는가?

### 11.9 테스트 자동화

**예제 테스트 코드:**

```python
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_artist_response_schema():
    """Artist 응답 스키마 검증"""
    response = client.get("/v1/api/artists/artist_001")
    assert response.status_code == 200
    
    data = response.json()
    
    # JSON-LD 필수 필드 검증
    assert "@context" in data
    assert "@type" in data
    assert "@id" in data
    
    # ID 형식 검증
    assert data["@id"].startswith("argo://artist/")
    
    # 좌표 필드 검증
    assert "argo:coordinates_3d" in data
    coords = data["argo:coordinates_3d"]
    assert -30 <= coords["argo:x"] <= 30
    assert -30 <= coords["argo:y"] <= 30
    assert -30 <= coords["argo:z"] <= 30
    assert coords["argo:radius"] >= 10

def test_cors_headers():
    """CORS 헤더 검증"""
    response = client.options(
        "/v1/api/artists",
        headers={"Origin": "https://artdrive1208.web.app"}
    )
    assert "access-control-allow-origin" in response.headers
```

---

## 부록 A: 빠른 참조 체크리스트

### 개발 시작 전 확인사항

- [ ] `ARGO_API_SPECIFICATION.yaml` 파일을 Antigravity IDE에 입력했는가?
- [ ] Pydantic 모델이 OpenAPI 스키마에서 자동 생성되었는가?
- [ ] 모든 필드명이 snake_case인가?
- [ ] JSON-LD 변환 미들웨어를 구현했는가?
- [ ] CORS 설정을 추가했는가?
- [ ] 좌표 계산 로직을 구현했는가?

### 배포 전 확인사항

- [ ] 모든 API 엔드포인트가 테스트되었는가?
- [ ] 타입 일치성이 검증되었는가?
- [ ] JSON-LD 형식이 올바른가?
- [ ] ID 매핑이 올바른가?
- [ ] 에러 응답이 표준 형식을 따르는가?
- [ ] 성능 목표를 달성했는가?

---

## 부록 B: 주요 참조 문서 링크

- [OpenAPI 명세서](docs/ARGO_API_SPECIFICATION.yaml)
- [데이터베이스 스키마](docs/ARGO_Final_Schema.md)
- [기술 명세서](docs/ARGO_TSD_Final.md)
- [소프트웨어 요구사항](docs/ARGO_SRD_Final.md)
- [프론트엔드 타입 정의](types/argo.ts)

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 개발팀  
**검토 상태**: 최종 확정

