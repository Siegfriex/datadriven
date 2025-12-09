# ARGO Antigravity IDE 백엔드 개발 지시 가이드
## Step-by-Step Directing Guide for Antigravity IDE

**작성일**: 2025-12-09  
**버전**: 1.0  
**프로젝트 ID**: artdrive1208  
**대상**: Antigravity IDE 사용자, 백엔드 개발자

---

## 📋 목차

1. [개요](#1-개요)
2. [Antigravity IDE에 제공할 파일 목록](#2-antigravity-ide에-제공할-파일-목록)
3. [단계별 지시 방법](#3-단계별-지시-방법)
4. [기대할 수 있는 최종 결과물](#4-기대할-수-있는-최종-결과물)
5. [검증 방법](#5-검증-방법)
6. [주의사항 및 트러블슈팅](#6-주의사항-및-트러블슈팅)
7. [Antigravity IDE에 제공할 최종 지시문](#7-antigravity-ide에-제공할-최종-지시문)

---

## 1. 개요

이 가이드는 **Antigravity IDE를 사용하여 ARGO 프로젝트의 백엔드 API를 개발**할 때 따라야 할 단계별 지시 방법을 제공합니다.

### 1.1 목적

- Antigravity IDE에 코드베이스를 제공하는 방법 명시
- 단계별 지시 방법 제공
- 기대할 수 있는 최종 결과물 구조 정의
- 검증 방법 및 체크리스트 제공

### 1.2 프로젝트 정보

- **프로젝트 이름**: ARTDRIVE
- **프로젝트 ID**: artdrive1208
- **리전**: asia-northeast3 (서울)
- **백엔드 프레임워크**: FastAPI + Python 3.10+
- **데이터베이스**: Neo4j Aura Cloud
- **배포 플랫폼**: Google Cloud Run

---

## 2. Antigravity IDE에 제공할 파일 목록

### 2.1 필수 제공 파일 (우선순위 순)

#### 1순위: 핵심 명세서 파일

| 파일명 | 경로 | 용도 | 필수 여부 |
|--------|------|------|----------|
| **ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md** | `docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` | 백엔드 개발 가이드라인 (최우선 참조) | ✅ 필수 |
| **ARGO_API_SPECIFICATION.yaml** | `docs/ARGO_API_SPECIFICATION.yaml` | OpenAPI 3.0 명세서 (API 스키마 정의) | ✅ 필수 |
| **ARGO_Final_Schema.md** | `docs/ARGO_Final_Schema.md` | Neo4j 데이터베이스 스키마 정의 | ✅ 필수 |

#### 2순위: 참조 문서 파일

| 파일명 | 경로 | 용도 | 필수 여부 |
|--------|------|------|----------|
| **ARGO_TSD_Final.md** | `docs/ARGO_TSD_Final.md` | 기술 명세서 (JSON-LD 형식, API 응답 규칙) | ⚠️ 권장 |
| **ARGO_SRD_Final.md** | `docs/ARGO_SRD_Final.md` | 소프트웨어 요구사항 (기능 명세, KPI) | ⚠️ 권장 |
| **types/argo.ts** | `types/argo.ts` | 프론트엔드 TypeScript 타입 정의 (타입 일치성 검증) | ⚠️ 권장 |

#### 3순위: 인프라 및 설정 파일

| 파일명 | 경로 | 용도 | 필수 여부 |
|--------|------|------|----------|
| **ARGO_GCP_INFRASTRUCTURE_SETUP.md** | `docs/ARGO_GCP_INFRASTRUCTURE_SETUP.md` | GCP 인프라 설정 가이드 | ⚠️ 참고용 |
| **ARGO_SERVICE_ACCOUNTS.md** | `docs/ARGO_SERVICE_ACCOUNTS.md` | 서비스 계정 및 IAM 역할 정의 | ⚠️ 참고용 |

### 2.2 파일 제공 방법

**옵션 1: 전체 코드베이스 업로드 (권장)**
- Antigravity IDE에 전체 프로젝트 디렉토리 업로드
- 모든 문서와 타입 정의 파일 포함

**옵션 2: 필수 파일만 선택 업로드**
- `docs/` 폴더 전체 업로드
- `types/argo.ts` 파일 업로드

---

## 3. 단계별 지시 방법

### 3.1 Phase 1: 프로젝트 초기화 및 설정

#### Step 1.1: Antigravity IDE 프로젝트 생성

**지시 내용:**
```
새로운 FastAPI 백엔드 프로젝트를 생성하세요.

프로젝트 설정:
- 프로젝트 이름: argo-backend
- Python 버전: 3.10 이상
- 프레임워크: FastAPI
- 패키지 관리자: pip (requirements.txt 사용)
```

#### Step 1.2: OpenAPI 명세서 입력

**지시 내용:**
```
OpenAPI 3.0 명세서 파일을 입력으로 사용하여 API 스키마를 생성하세요.

파일 경로: docs/ARGO_API_SPECIFICATION.yaml

요구사항:
1. OpenAPI 명세서를 파싱하여 모든 엔드포인트를 인식하세요
2. Pydantic 모델을 OpenAPI 스키마에서 자동 생성하세요
3. FastAPI 라우터를 자동 생성하세요
4. 요청/응답 검증 로직을 자동 생성하세요
```

**예상 결과:**
- `app/main.py`: FastAPI 애플리케이션 진입점
- `app/models/`: Pydantic 모델 디렉토리
- `app/routers/`: API 라우터 디렉토리
- `app/schemas/`: 요청/응답 스키마 디렉토리

#### Step 1.3: 핵심 가이드라인 문서 참조

**지시 내용:**
```
다음 문서를 참조하여 개발 규칙을 준수하세요:

1. docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md (최우선 참조)
   - 이 문서의 모든 섹션을 읽고 이해하세요
   - 특히 다음 섹션을 중점적으로 참조:
     * 섹션 4: API 스키마 명시 (필드명, 타입, 필수/선택)
     * 섹션 5: ID 매핑 규칙 (argo:// URI 형식)
     * 섹션 6: JSON-LD 형식 명시
     * 섹션 9: 타입 일치성 보장 가이드
     * 섹션 10: 좌표 계산 로직

2. docs/ARGO_Final_Schema.md
   - Neo4j 데이터베이스 스키마 구조 확인
   - 엔터티 및 관계 타입 정의 확인

3. types/argo.ts
   - 프론트엔드 TypeScript 타입 정의 확인
   - 백엔드 응답이 프론트엔드 타입과 일치하는지 검증
```

### 3.2 Phase 2: 핵심 기능 구현

#### Step 2.1: 프로젝트 구조 생성

**지시 내용:**
```
다음 디렉토리 구조를 생성하세요:

argo-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── config.py               # 설정 관리 (환경변수, GCP Secret Manager)
│   ├── database.py             # Neo4j 연결 관리
│   ├── middleware.py           # JSON-LD 변환, CORS, 에러 처리 미들웨어
│   ├── models/                 # Pydantic 모델
│   │   ├── __init__.py
│   │   ├── artist.py
│   │   ├── institution.py
│   │   ├── exhibition.py
│   │   ├── transaction.py
│   │   ├── cluster.py
│   │   └── common.py           # 공통 모델 (Scores, Coordinates3D 등)
│   ├── routers/                # API 라우터
│   │   ├── __init__.py
│   │   ├── artists.py
│   │   ├── institutions.py
│   │   ├── exhibitions.py
│   │   ├── transactions.py
│   │   ├── clusters.py
│   │   ├── analysis.py
│   │   ├── anomalies.py
│   │   └── search.py
│   ├── services/               # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── artist_service.py
│   │   ├── neo4j_service.py
│   │   └── coordinate_service.py  # 좌표 계산 로직
│   └── utils/                  # 유틸리티 함수
│       ├── __init__.py
│       ├── jsonld.py           # JSON-LD 변환 유틸리티
│       └── errors.py           # 에러 응답 생성 유틸리티
├── requirements.txt            # Python 의존성
├── .env.example                # 환경변수 예제
├── Dockerfile                  # Cloud Run 배포용 (선택사항)
└── README.md                   # 프로젝트 설명
```

#### Step 2.2: 의존성 설정

**지시 내용:**
```
requirements.txt 파일을 생성하고 다음 의존성을 추가하세요:

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
google-generativeai==0.3.0  # Gemini API (이상치 탐지용)
```

#### Step 2.3: 설정 관리 구현

**지시 내용:**
```
app/config.py 파일을 생성하고 다음 설정을 구현하세요:

1. 환경변수 로드 (로컬: .env 파일, 프로덕션: GCP Secret Manager)
2. Neo4j 연결 정보 (URI, 사용자명, 비밀번호)
3. Gemini API 키 (GEMINI_API_KEY)
4. CORS 허용 Origin 목록
5. API 버전 관리 (현재: v1)

참조: docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 3.3
```

**예제 코드:**
```python
# app/config.py
import os
from pydantic_settings import BaseSettings
from google.cloud import secretmanager

class Settings(BaseSettings):
    # 프로젝트 정보
    project_id: str = "artdrive1208"
    region: str = "asia-northeast3"
    
    # Neo4j 설정
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    # Gemini API 설정
    gemini_api_key: str
    
    # CORS 설정
    allowed_origins: list = [
        "https://artdrive1208.web.app",
        "https://argo.art",
        "http://localhost:5173"
    ]
    
    # API 버전
    api_version: str = "v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_secret(secret_id: str) -> str:
    """GCP Secret Manager에서 시크릿 가져오기"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/artdrive1208/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# 설정 인스턴스 생성
settings = Settings()
```

#### Step 2.4: Neo4j 데이터베이스 연결 구현

**지시 내용:**
```
app/database.py 파일을 생성하고 Neo4j 연결을 구현하세요.

요구사항:
1. Neo4j Aura Cloud 연결 (py2neo 또는 neo4j 드라이버 사용)
2. 연결 풀 관리
3. 연결 해제 처리
4. 쿼리 실행 헬퍼 함수

참조: docs/ARGO_Final_Schema.md (데이터베이스 스키마)
```

**예제 코드:**
```python
# app/database.py
from neo4j import GraphDatabase
from app.config import settings

class Neo4jDatabase:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query: str, parameters: dict = None):
        """Cypher 쿼리 실행"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

# 전역 데이터베이스 인스턴스
db = Neo4jDatabase()
```

### 3.3 Phase 3: Pydantic 모델 구현

#### Step 3.1: 공통 모델 구현

**지시 내용:**
```
app/models/common.py 파일을 생성하고 다음 공통 모델을 구현하세요:

1. Scores 모델 (inst_score, acad_score, media_score, network_score, composite_score)
2. Coordinates3D 모델 (x, y, z, radius, computed_at, algorithm)
3. StructuralistAnalysis 모델 (dominant_capital, capital_composition, structural_position 등)
4. Collaboration 모델 (artist_id, strength)
5. Institution 모델 (institution_id, name, type) - Artist 내부 사용용
6. Exhibition 모델 (exhibition_id, name, year) - Artist 내부 사용용

중요: 
- 모든 필드명은 snake_case 사용
- 타입과 제약조건을 정확히 준수
- docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 4.1 참조
```

#### Step 3.2: Artist 모델 구현

**지시 내용:**
```
app/models/artist.py 파일을 생성하고 Artist 모델을 구현하세요.

요구사항:
1. JSON-LD 필수 필드 포함 (@context, @type, @id)
2. Schema.org 필드 포함 (name, alternateName, birthDate 등)
3. ARGO 커스텀 필드 포함 (scores, structuralist_analysis, coordinates_3d)
4. 관계 데이터 필드 포함 (collaborations, institutions, exhibitions)
5. 하위 호환성 필드 포함 (collaborators)

중요:
- coordinates_3d 필드는 필수이며, 자동 계산 로직 구현 필요
- docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 4.1.6 참조
```

#### Step 3.3: 기타 엔터티 모델 구현

**지시 내용:**
```
다음 엔터티 모델을 구현하세요:

1. app/models/institution.py: Institution 모델
2. app/models/exhibition.py: Exhibition 모델
3. app/models/transaction.py: Transaction 모델
4. app/models/cluster.py: Cluster 모델

각 모델은 OpenAPI 명세서의 스키마를 정확히 따르세요.
참조: docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 4.2-4.11
```

### 3.4 Phase 4: JSON-LD 변환 미들웨어 구현

#### Step 4.1: JSON-LD 변환 유틸리티 구현

**지시 내용:**
```
app/utils/jsonld.py 파일을 생성하고 JSON-LD 변환 함수를 구현하세요.

요구사항:
1. 모든 응답에 @context, @type, @id 필드 자동 추가
2. ARGO 커스텀 필드에 argo: 네임스페이스 추가
3. 관계 데이터는 네임스페이스 없이 일반 배열로 제공

참조: docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 6.4
```

**예제 코드:**
```python
# app/utils/jsonld.py
def add_jsonld_context(data: dict, entity_type: str, entity_id: str) -> dict:
    """JSON-LD 컨텍스트 추가"""
    if isinstance(data, dict):
        if "@context" not in data:
            data["@context"] = "https://schema.org/"
        if "@type" not in data:
            # 엔터티 타입에 따라 자동 설정
            type_mapping = {
                "artist": "Person",
                "institution": "Organization",
                "exhibition": "Event"
            }
            data["@type"] = type_mapping.get(entity_type.lower(), "Thing")
        if "@id" not in data:
            data["@id"] = f"argo://{entity_type.lower()}/{entity_id}"
    return data
```

#### Step 4.2: FastAPI 미들웨어 구현

**지시 내용:**
```
app/middleware.py 파일을 생성하고 다음 미들웨어를 구현하세요:

1. JSON-LD 변환 미들웨어 (모든 응답에 JSON-LD 필드 추가)
2. CORS 미들웨어 (허용된 Origin에서만 요청 허용)
3. 에러 처리 미들웨어 (표준 에러 응답 형식)

참조: docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 6.4, 8.1
```

### 3.5 Phase 5: 좌표 계산 로직 구현

#### Step 5.1: 좌표 계산 서비스 구현

**지시 내용:**
```
app/services/coordinate_service.py 파일을 생성하고 좌표 계산 로직을 구현하세요.

요구사항:
1. normalize_score 함수 구현 (점수를 -30 ~ 30 범위로 정규화)
2. calculate_coordinates_3d 함수 구현 (4가지 점수 기반 좌표 계산)
3. 모든 Artist 응답에 coordinates_3d 필드 자동 포함

계산 공식:
- x = normalize_score(inst_score, 0, 100, -30, 30)
- y = normalize_score(acad_score, 0, 100, -30, 30)
- z = normalize_score(media_score, 0, 100, -30, 30)
- radius = 10 + (network_score / 5)

참조: docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 10
```

**예제 코드:**
```python
# app/services/coordinate_service.py
from datetime import datetime
from typing import Dict

def normalize_score(
    score: float,
    min_score: float,
    max_score: float,
    target_min: float,
    target_max: float
) -> float:
    """점수를 정규화하여 target 범위로 변환"""
    if max_score == min_score:
        return (target_min + target_max) / 2
    
    normalized = ((score - min_score) / (max_score - min_score)) * (target_max - target_min) + target_min
    return round(normalized, 2)

def calculate_coordinates_3d(
    inst_score: float,
    acad_score: float,
    media_score: float,
    network_score: float
) -> Dict:
    """3D 갤럭시 좌표 계산"""
    x = normalize_score(inst_score, 0, 100, -30, 30)
    y = normalize_score(acad_score, 0, 100, -30, 30)
    z = normalize_score(media_score, 0, 100, -30, 30)
    radius = round(10 + (network_score / 5), 2)
    
    return {
        "argo:x": x,
        "argo:y": y,
        "argo:z": z,
        "argo:radius": radius,
        "computed_at": datetime.utcnow().isoformat() + "Z",
        "algorithm": "normalize_v1"
    }
```

### 3.6 Phase 6: API 라우터 구현

#### Step 6.1: Artist API 라우터 구현

**지시 내용:**
```
app/routers/artists.py 파일을 생성하고 다음 엔드포인트를 구현하세요:

1. GET /v1/api/artists
   - 페이지네이션 지원 (page, limit)
   - 필터 지원 (segment_id, career_stage, min_score)
   - Neo4j 쿼리로 작가 목록 조회
   - 각 작가에 coordinates_3d 자동 계산하여 포함
   - 관계 데이터 포함 (collaborations, institutions, exhibitions)
   - JSON-LD 형식으로 응답

2. GET /v1/api/artists/{artist_id}
   - 특정 작가 상세 정보 조회
   - 모든 관계 데이터 포함 (collaborations, institutions, exhibitions)
   - coordinates_3d 필수 포함
   - JSON-LD 형식으로 응답

3. GET /v1/api/artists/{artist_id}/network
   - 작가의 1홉/2홉 네트워크 그래프 조회
   - depth 파라미터 지원 (1 또는 2)
   - NetworkGraph 형식으로 응답

4. GET /v1/api/artists/{artist_id}/exhibitions
   - 작가가 참여한 전시 목록 조회

5. GET /v1/api/artists/{artist_id}/artworks
   - 작가의 작품 목록 조회

6. GET /v1/api/artists/{artist_id}/structural-equivalents
   - 구조적 등가성 작가 조회 (임계값 0.15)

7. GET /v1/api/artists/{artist_id}/capital-composition
   - 자본 구성 분석 조회

8. GET /v1/api/artists/{artist_id}/market
   - 작가 시장 정보 조회 (거래 이력, 가격 추이)

9. POST /v1/api/artists/search
   - 작가 전문 검색 (이름, 기관, 세그먼트 등)

중요:
- 모든 응답은 JSON-LD 형식
- coordinates_3d 필드 필수 포함
- 관계 데이터 필드 포함 (collaborations, institutions, exhibitions)
- OpenAPI 명세서의 스키마를 정확히 따름
- docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 4.1 참조
```

**예제 코드 구조:**
```python
# app/routers/artists.py
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional, List
from app.models.artist import Artist
from app.services.artist_service import ArtistService
from app.services.coordinate_service import calculate_coordinates_3d
from app.utils.jsonld import add_jsonld_context

router = APIRouter()
artist_service = ArtistService()

@router.get("/artists", response_model=dict)
async def get_artists(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    segment_id: Optional[str] = None,
    career_stage: Optional[str] = None,
    min_score: Optional[float] = None
):
    """모든 작가 조회"""
    # Neo4j 쿼리 실행
    artists_data = artist_service.get_artists(
        page=page,
        limit=limit,
        segment_id=segment_id,
        career_stage=career_stage,
        min_score=min_score
    )
    
    # 각 작가에 coordinates_3d 추가
    for artist in artists_data["artists"]:
        if "scores" in artist:
            artist["argo:coordinates_3d"] = calculate_coordinates_3d(
                inst_score=artist["scores"]["argo:inst_score"],
                acad_score=artist["scores"]["argo:acad_score"],
                media_score=artist["scores"]["argo:media_score"],
                network_score=artist["scores"]["argo:network_score"]
            )
        
        # JSON-LD 필드 추가
        artist = add_jsonld_context(
            artist,
            entity_type="artist",
            entity_id=artist["artist_id"]
        )
    
    return artists_data

@router.get("/artists/{artist_id}", response_model=dict)
async def get_artist(artist_id: str = Path(...)):
    """작가 상세 정보 조회"""
    artist = artist_service.get_artist_by_id(artist_id)
    
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    # coordinates_3d 추가
    if "scores" in artist:
        artist["argo:coordinates_3d"] = calculate_coordinates_3d(
            inst_score=artist["scores"]["argo:inst_score"],
            acad_score=artist["scores"]["argo:acad_score"],
            media_score=artist["scores"]["argo:media_score"],
            network_score=artist["scores"]["argo:network_score"]
        )
    
    # 관계 데이터 조회
    artist["collaborations"] = artist_service.get_collaborations(artist_id)
    artist["institutions"] = artist_service.get_institutions(artist_id)
    artist["exhibitions"] = artist_service.get_exhibitions(artist_id)
    
    # JSON-LD 필드 추가
    artist = add_jsonld_context(artist, "artist", artist_id)
    
    return artist
```

#### Step 6.2: 기타 API 라우터 구현

**지시 내용:**
```
다음 API 라우터를 구현하세요:

1. app/routers/institutions.py (5개 엔드포인트)
2. app/routers/exhibitions.py (2개 엔드포인트)
3. app/routers/transactions.py (3개 엔드포인트)
4. app/routers/clusters.py (2개 엔드포인트)
5. app/routers/analysis.py (5개 엔드포인트)
6. app/routers/anomalies.py (2개 엔드포인트, Gemini 3 Pro Preview 사용)
7. app/routers/search.py (1개 엔드포인트)
8. app/routers/galaxy.py 또는 main.py에 포함 (2개 엔드포인트)

참조: docs/ARGO_API_SPECIFICATION.yaml (모든 엔드포인트 정의)
```

### 3.7 Phase 7: 비즈니스 로직 구현

#### Step 7.1: Neo4j 서비스 구현

**지시 내용:**
```
app/services/neo4j_service.py 파일을 생성하고 Neo4j 쿼리 실행 로직을 구현하세요.

요구사항:
1. 작가 조회 쿼리 (필터, 페이지네이션 지원)
2. 작가 상세 조회 쿼리 (모든 관계 포함)
3. 네트워크 그래프 쿼리 (1홉/2홉)
4. 구조적 등가성 계산 쿼리
5. 커뮤니티 탐지 쿼리 (Louvain 알고리즘)
6. 중심성 계산 쿼리 (Degree, Betweenness, Eigenvector)

참조: docs/ARGO_Final_Schema.md (Cypher 쿼리 예제)
```

**예제 쿼리:**
```cypher
# 작가 목록 조회 (필터, 페이지네이션)
MATCH (a:Artist)
WHERE ($segment_id IS NULL OR a.segment_id = $segment_id)
  AND ($career_stage IS NULL OR a.career_stage = $career_stage)
  AND ($min_score IS NULL OR a.composite_score >= $min_score)
RETURN a
SKIP $skip
LIMIT $limit

# 작가 상세 조회 (관계 포함)
MATCH (a:Artist {artist_id: $artist_id})
OPTIONAL MATCH (a)-[r:COLLABORATED_WITH]->(collab:Artist)
OPTIONAL MATCH (a)-[:AFFILIATED_WITH]->(inst:Institution)
OPTIONAL MATCH (a)-[:PARTICIPATED_IN]->(exh:Exhibition)
RETURN a, collect(DISTINCT collab) as collaborators, 
       collect(DISTINCT inst) as institutions,
       collect(DISTINCT exh) as exhibitions
```

#### Step 7.2: 관계 데이터 조회 로직 구현

**지시 내용:**
```
작가 조회 시 관계 데이터를 포함하는 로직을 구현하세요.

요구사항:
1. collaborations 배열 생성
   - COLLABORATED_WITH 관계 조회
   - strength 값 계산 (관계 강도, 0-1 범위)
   - strength >= 0.3인 관계만 포함 (프론트엔드 필터링용)

2. institutions 배열 생성
   - AFFILIATED_WITH 관계 조회
   - 기관 정보 포함

3. exhibitions 배열 생성
   - PARTICIPATED_IN 관계 조회
   - 전시 정보 포함

4. 하위 호환성 유지
   - collaborators 배열도 생성 (작가 ID만 포함)
```

**예제 코드:**
```python
# app/services/artist_service.py
def get_collaborations(artist_id: str) -> List[Dict]:
    """협력 관계 조회"""
    query = """
    MATCH (a:Artist {artist_id: $artist_id})-[r:COLLABORATED_WITH]->(collab:Artist)
    RETURN collab.artist_id as artist_id, 
           COALESCE(r.strength, 0.5) as strength
    ORDER BY strength DESC
    """
    results = db.execute_query(query, {"artist_id": artist_id})
    return [
        {
            "artist_id": r["artist_id"],
            "strength": float(r["strength"])
        }
        for r in results
        if float(r["strength"]) >= 0.3  # 프론트엔드 필터링 조건
    ]
```

### 3.8 Phase 8: 에러 처리 및 검증

#### Step 8.1: 에러 응답 구현

**지시 내용:**
```
app/utils/errors.py 파일을 생성하고 표준 에러 응답 함수를 구현하세요.

요구사항:
1. create_error_response 함수 구현
2. HTTP 상태 코드별 에러 코드 매핑
3. 에러 메시지 사용자 친화적 작성
4. request_id 자동 생성

참조: docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 7
```

**예제 코드:**
```python
# app/utils/errors.py
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
```

#### Step 8.2: 입력 검증 구현

**지시 내용:**
```
모든 API 엔드포인트에 입력 검증을 구현하세요.

요구사항:
1. Pydantic 모델을 사용한 자동 검증
2. 쿼리 파라미터 범위 검증 (page >= 1, limit 1-100 등)
3. 경로 파라미터 형식 검증 (artist_id 형식 등)
4. 표준 에러 응답 반환 (400 Bad Request)

참조: docs/ARGO_API_SPECIFICATION.yaml (파라미터 정의)
```

### 3.9 Phase 9: 메인 애플리케이션 구성

#### Step 9.1: FastAPI 애플리케이션 초기화

**지시 내용:**
```
app/main.py 파일을 생성하고 FastAPI 애플리케이션을 구성하세요.

요구사항:
1. FastAPI 인스턴스 생성
2. 모든 라우터 등록 (/v1 경로 포함)
3. 미들웨어 등록 (CORS, JSON-LD 변환, 에러 처리)
4. 라이프사이클 이벤트 처리 (startup: Neo4j 연결, shutdown: 연결 해제)
5. OpenAPI 문서 자동 생성 (/docs 엔드포인트)

구조:
- Base URL: /v1
- 모든 API는 /v1/api/* 경로 사용
- 예: /v1/api/artists, /v1/api/institutions
```

**예제 코드:**
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db
from app.routers import artists, institutions, exhibitions, transactions, clusters, analysis, anomalies, search
from app.middleware import add_jsonld_middleware, error_handler_middleware

app = FastAPI(
    title="ARGO API",
    version="1.0.0",
    description="ARGO (Art-world Real-time Galaxy Observatory) API"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# JSON-LD 변환 미들웨어
app.middleware("http")(add_jsonld_middleware)

# 에러 처리 미들웨어
app.middleware("http")(error_handler_middleware)

# 라우터 등록
app.include_router(artists.router, prefix=f"/{settings.api_version}/api", tags=["Artists"])
app.include_router(institutions.router, prefix=f"/{settings.api_version}/api", tags=["Institutions"])
app.include_router(exhibitions.router, prefix=f"/{settings.api_version}/api", tags=["Exhibitions"])
app.include_router(transactions.router, prefix=f"/{settings.api_version}/api", tags=["Transactions"])
app.include_router(clusters.router, prefix=f"/{settings.api_version}/api", tags=["Clusters"])
app.include_router(analysis.router, prefix=f"/{settings.api_version}/api", tags=["Analysis"])
app.include_router(anomalies.router, prefix=f"/{settings.api_version}/api", tags=["Anomalies"])
app.include_router(search.router, prefix=f"/{settings.api_version}/api", tags=["Search"])

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    # Neo4j 연결 확인
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    db.close()

@app.get("/")
async def root():
    return {"message": "ARGO API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 4. 기대할 수 있는 최종 결과물

### 4.1 프로젝트 구조

```
argo-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 애플리케이션 진입점
│   ├── config.py                    # 설정 관리
│   ├── database.py                  # Neo4j 연결 관리
│   ├── middleware.py                # 미들웨어 (JSON-LD, CORS, 에러 처리)
│   ├── models/                      # Pydantic 모델
│   │   ├── __init__.py
│   │   ├── artist.py                # Artist 모델 (관계 데이터 포함)
│   │   ├── institution.py
│   │   ├── exhibition.py
│   │   ├── transaction.py
│   │   ├── cluster.py
│   │   └── common.py                # 공통 모델 (Scores, Coordinates3D 등)
│   ├── routers/                      # API 라우터
│   │   ├── __init__.py
│   │   ├── artists.py                # 9개 엔드포인트
│   │   ├── institutions.py          # 5개 엔드포인트
│   │   ├── exhibitions.py           # 2개 엔드포인트
│   │   ├── transactions.py          # 3개 엔드포인트
│   │   ├── clusters.py              # 2개 엔드포인트
│   │   ├── analysis.py              # 5개 엔드포인트
│   │   ├── anomalies.py             # 2개 엔드포인트 (Gemini API 사용)
│   │   └── search.py                 # 1개 엔드포인트
│   ├── services/                     # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── artist_service.py        # 작가 관련 비즈니스 로직
│   │   ├── neo4j_service.py          # Neo4j 쿼리 실행
│   │   └── coordinate_service.py    # 좌표 계산 로직
│   └── utils/                       # 유틸리티 함수
│       ├── __init__.py
│       ├── jsonld.py                # JSON-LD 변환
│       └── errors.py                # 에러 응답 생성
├── requirements.txt                 # Python 의존성
├── .env.example                     # 환경변수 예제
├── .gitignore
├── Dockerfile                       # Cloud Run 배포용 (선택사항)
└── README.md                        # 프로젝트 설명
```

### 4.2 구현된 기능

#### 4.2.1 API 엔드포인트 (31개)

**작가 API (9개):**
- ✅ GET `/v1/api/artists` - 모든 작가 조회 (페이지네이션, 필터)
- ✅ GET `/v1/api/artists/{artist_id}` - 작가 상세 정보 조회
- ✅ GET `/v1/api/artists/{artist_id}/network` - 네트워크 그래프 조회
- ✅ GET `/v1/api/artists/{artist_id}/exhibitions` - 전시 목록 조회
- ✅ GET `/v1/api/artists/{artist_id}/artworks` - 작품 목록 조회
- ✅ GET `/v1/api/artists/{artist_id}/structural-equivalents` - 구조적 등가성 조회
- ✅ GET `/v1/api/artists/{artist_id}/capital-composition` - 자본 구성 분석 조회
- ✅ GET `/v1/api/artists/{artist_id}/market` - 시장 정보 조회
- ✅ POST `/v1/api/artists/search` - 전문 검색

**기관 API (5개):**
- ✅ GET `/v1/api/institutions` - 모든 기관 조회
- ✅ GET `/v1/api/institutions/{inst_id}` - 기관 상세 정보 조회
- ✅ GET `/v1/api/institutions/{inst_id}/affiliated-artists` - 소속 미술가 목록 조회
- ✅ GET `/v1/api/institutions/{inst_id}/exhibitions` - 전시 목록 조회
- ✅ GET `/v1/api/institutions/{inst_id}/benchmarking` - 벤치마킹 조회

**전시 API (2개):**
- ✅ GET `/v1/api/exhibitions` - 모든 전시 조회
- ✅ GET `/v1/api/exhibitions/{exh_id}` - 전시 상세 정보 조회

**거래 API (3개):**
- ✅ GET `/v1/api/transactions` - 모든 거래 조회
- ✅ GET `/v1/api/transactions/{trans_id}` - 거래 상세 정보 조회
- ✅ GET `/v1/api/transactions/price-history/{artist_id}` - 가격 히스토리 조회

**군집 API (2개):**
- ✅ GET `/v1/api/clusters` - 모든 군집 조회
- ✅ GET `/v1/api/clusters/{cluster_id}` - 군집 상세 정보 조회

**분석 API (5개):**
- ✅ POST `/v1/api/analysis/centrality` - 중심성 계산
- ✅ POST `/v1/api/analysis/community-detection` - 커뮤니티 탐지
- ✅ GET `/v1/api/analysis/correlation` - 상관관계 분석
- ✅ POST `/v1/api/analysis/compare` - 작가 비교 분석
- ✅ GET `/v1/api/analysis/field-quadrants` - 필드 분면 분류 조회

**이상치 탐지 API (2개):**
- ✅ GET `/v1/api/anomalies` - 이상치 목록 조회 (Gemini 3 Pro Preview)
- ✅ POST `/v1/api/anomalies/analyze` - 이상치 재분석 (Gemini 3 Pro Preview)

**검색 API (1개):**
- ✅ GET `/v1/api/search` - 통합 검색

**갤럭시 및 메타데이터 API (2개):**
- ✅ GET `/v1/api/galaxy-snapshot` - 갤럭시 스냅샷 조회
- ✅ GET `/v1/api/metadata/sources` - 데이터 출처 조회

#### 4.2.2 핵심 기능

1. **JSON-LD 형식 응답**
   - 모든 응답에 `@context`, `@type`, `@id` 필드 포함
   - ARGO 커스텀 필드는 `argo:` 네임스페이스 사용
   - Schema.org 표준 준수

2. **좌표 자동 계산**
   - 모든 Artist 응답에 `coordinates_3d` 필드 포함
   - 4가지 점수 기반 자동 계산
   - 프론트엔드 3D 갤럭시 렌더링 지원

3. **관계 데이터 포함**
   - `collaborations` 배열 (strength 포함)
   - `institutions` 배열
   - `exhibitions` 배열
   - 프론트엔드 연결선 시각화 지원

4. **에러 처리**
   - 표준 에러 응답 형식
   - HTTP 상태 코드 매핑
   - 사용자 친화적 에러 메시지

5. **CORS 설정**
   - 허용된 Origin에서만 요청 허용
   - Firebase Hosting 도메인 포함

### 4.3 코드 품질 기준

1. **타입 안정성**
   - 모든 함수에 타입 힌트 포함
   - Pydantic 모델을 사용한 자동 검증

2. **에러 처리**
   - 모든 예외 상황 처리
   - 표준 에러 응답 형식 준수

3. **성능**
   - Neo4j 쿼리 최적화
   - 페이지네이션 강제 (limit 최대 100)
   - 좌표 계산 결과 캐싱 (선택사항)

4. **문서화**
   - 모든 함수에 docstring 포함
   - OpenAPI 문서 자동 생성

---

## 5. 검증 방법

### 5.1 단위 테스트

**지시 내용:**
```
각 모듈별로 단위 테스트를 작성하세요.

테스트 항목:
1. Pydantic 모델 검증 테스트
2. 좌표 계산 로직 테스트
3. JSON-LD 변환 로직 테스트
4. 에러 응답 생성 테스트

테스트 프레임워크: pytest
```

### 5.2 통합 테스트

**지시 내용:**
```
API 엔드포인트별로 통합 테스트를 작성하세요.

테스트 항목:
1. 모든 엔드포인트 응답 형식 검증
2. JSON-LD 스키마 검증
3. 타입 일치성 검증 (프론트엔드 타입과 비교)
4. 에러 응답 검증
5. CORS 헤더 검증

테스트 프레임워크: pytest + httpx
```

### 5.3 검증 체크리스트

**다음 항목들을 검증하세요:**

#### 필수 검증 항목

- [ ] 모든 API 엔드포인트가 OpenAPI 명세서와 일치하는가?
- [ ] 모든 응답에 JSON-LD 필수 필드(`@context`, `@type`, `@id`)가 포함되어 있는가?
- [ ] 모든 Artist 응답에 `coordinates_3d` 필드가 포함되어 있는가?
- [ ] 좌표 값이 올바른 범위 내에 있는가? (x, y, z: -30 ~ 30)
- [ ] 관계 데이터 필드(`collaborations`, `institutions`, `exhibitions`)가 올바른 형식인가?
- [ ] `collaborations` 배열의 `strength` 값이 0-1 범위 내에 있는가?
- [ ] 모든 필드명이 snake_case인가?
- [ ] 프론트엔드 TypeScript 타입과 일치하는가?
- [ ] CORS 설정이 올바른가?
- [ ] 에러 응답이 표준 형식을 따르는가?

#### 성능 검증 항목

- [ ] API 응답 시간이 200ms 이하인가?
- [ ] 페이지네이션이 올바르게 작동하는가?
- [ ] 동시 요청 처리가 가능한가?

---

## 6. 주의사항 및 트러블슈팅

### 6.1 주의사항

#### 6.1.1 필드명 일치성

**문제**: 프론트엔드와 백엔드 간 필드명 불일치

**해결책**:
- 모든 필드명은 snake_case 사용
- JSON 응답에서는 JSON-LD 표준 필드명 사용 (`alternateName` 등)
- 프론트엔드에서 변환 처리

#### 6.1.2 좌표 계산 누락

**문제**: `coordinates_3d` 필드가 누락되면 프론트엔드 렌더링 실패

**해결책**:
- 모든 Artist 조회 시 좌표 자동 계산
- Pydantic 모델에 `@computed_field` 사용
- 또는 서비스 레이어에서 계산 후 포함

#### 6.1.3 관계 데이터 형식

**문제**: `collaborations` 배열의 `strength` 값이 올바르지 않음

**해결책**:
- Neo4j 관계 속성에서 `strength` 값 조회
- 없으면 기본값 0.5 설정
- 0-1 범위로 정규화

### 6.2 트러블슈팅

#### 문제 1: JSON-LD 필드가 응답에 포함되지 않음

**원인**: 미들웨어가 제대로 작동하지 않음

**해결책**:
1. 미들웨어 등록 순서 확인
2. 응답 본문 파싱 로직 확인
3. JSON-LD 변환 함수 테스트

#### 문제 2: CORS 에러 발생

**원인**: CORS 미들웨어 설정 오류

**해결책**:
1. `allowed_origins` 목록 확인
2. `allow_credentials=True` 설정 확인
3. OPTIONS 요청 처리 확인

#### 문제 3: Neo4j 쿼리 성능 저하

**원인**: 인덱스 미설정 또는 비효율적인 쿼리

**해결책**:
1. Neo4j 인덱스 확인 (`artist_id`, `inst_id` 등)
2. 쿼리 최적화 (PROFILE 사용)
3. 페이지네이션 강제

#### 문제 4: 좌표 계산 오류

**원인**: 점수 값이 범위를 벗어남 또는 None 값

**해결책**:
1. 점수 값 검증 (0-100 범위)
2. None 값 처리 (기본값 0 사용)
3. 계산 결과 검증

---

## 7. Antigravity IDE에 제공할 최종 지시문

### 7.1 전체 지시문 (한 번에 제공)

```
ARGO 프로젝트의 백엔드 API를 FastAPI + Python 3.10+로 구현하세요.

**제공된 파일:**
1. docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md (최우선 참조)
2. docs/ARGO_API_SPECIFICATION.yaml (OpenAPI 명세서)
3. docs/ARGO_Final_Schema.md (Neo4j 스키마)
4. types/argo.ts (프론트엔드 타입 정의)

**핵심 요구사항:**

1. OpenAPI 명세서 기반 코드 생성
   - ARGO_API_SPECIFICATION.yaml 파일을 입력으로 사용
   - 모든 31개 엔드포인트 구현
   - Pydantic 모델 자동 생성

2. 필수 기능 구현
   - JSON-LD 형식 응답 (모든 응답에 @context, @type, @id 포함)
   - 좌표 자동 계산 (모든 Artist 응답에 coordinates_3d 필수 포함)
   - 관계 데이터 포함 (collaborations, institutions, exhibitions)
   - CORS 설정 (허용 Origin: https://artdrive1208.web.app)
   - 표준 에러 응답 형식

3. 데이터베이스 연동
   - Neo4j Aura Cloud 연결
   - Cypher 쿼리 실행
   - 관계 데이터 조회

4. 타입 일치성 보장
   - 프론트엔드 TypeScript 타입과 일치
   - 모든 필드명 snake_case 사용
   - types/argo.ts 파일 참조

**중요 규칙:**
- 모든 필드명은 정확히 일치해야 함 (docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 4 참조)
- ID 매핑 규칙 준수 (argo:// URI 형식, 섹션 5 참조)
- JSON-LD 형식 필수 (섹션 6 참조)
- 좌표 계산 로직 필수 (섹션 10 참조)

**기대 결과물:**
- 완전한 FastAPI 백엔드 애플리케이션
- 모든 31개 API 엔드포인트 구현
- 프론트엔드와 호환되는 응답 형식
- Cloud Run 배포 가능한 상태

**검증 방법:**
- docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md 섹션 11 참조
- 통합 테스트 작성
- 프론트엔드와 연동 테스트
```

### 7.2 단계별 지시문 (단계별로 제공)

**Phase 1: 프로젝트 초기화**
```
1. FastAPI 프로젝트 생성
2. OpenAPI 명세서 입력 (ARGO_API_SPECIFICATION.yaml)
3. 기본 프로젝트 구조 생성
4. 의존성 설치 (requirements.txt)
```

**Phase 2: 핵심 모델 구현**
```
1. 공통 모델 구현 (Scores, Coordinates3D, StructuralistAnalysis)
2. 관계 데이터 모델 구현 (Collaboration, Institution, Exhibition)
3. Artist 모델 구현 (모든 필드 포함)
4. 기타 엔터티 모델 구현
```

**Phase 3: 핵심 기능 구현**
```
1. JSON-LD 변환 미들웨어 구현
2. 좌표 계산 로직 구현
3. Neo4j 연결 및 쿼리 실행 구현
4. CORS 미들웨어 구현
5. 에러 처리 미들웨어 구현
```

**Phase 4: API 라우터 구현**
```
1. Artist API 라우터 구현 (9개 엔드포인트)
2. 기타 API 라우터 구현 (22개 엔드포인트)
3. 관계 데이터 조회 로직 구현
4. 입력 검증 구현
```

**Phase 5: 통합 및 검증**
```
1. 메인 애플리케이션 구성
2. 모든 라우터 등록
3. 통합 테스트 작성
4. 프론트엔드와 연동 테스트
```

---

## 8. 추가 리소스

### 8.1 참조 문서

- `docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md`: 상세 개발 가이드라인
- `docs/ARGO_API_SPECIFICATION.yaml`: OpenAPI 명세서
- `docs/ARGO_Final_Schema.md`: 데이터베이스 스키마
- `docs/ARGO_TSD_Final.md`: 기술 명세서
- `docs/ARGO_SRD_Final.md`: 소프트웨어 요구사항

### 8.2 외부 리소스

- FastAPI 공식 문서: https://fastapi.tiangolo.com/
- Neo4j Python 드라이버: https://neo4j.com/docs/python-manual/current/
- Pydantic 문서: https://docs.pydantic.dev/
- JSON-LD 스펙: https://json-ld.org/

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 개발팀  
**검토 상태**: 최종 확정

