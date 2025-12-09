# ARGO 백엔드 수정 및 보완 프롬프트
## Direct Prompt for Antigravity IDE - Critical Fixes and Missing Endpoints

**작성일**: 2025-12-09  
**버전**: 1.0  
**프로젝트 ID**: artdrive1208  
**용도**: Antigravity IDE에 직접 복사하여 사용

---

## 🎯 프롬프트 시작

```
ARGO 백엔드 코드베이스를 검증한 결과, 여러 Critical 수정사항과 누락된 기능들이 발견되었습니다. 
다음 지시사항을 정확히 따라 수정 및 보완 작업을 수행해주세요.

## 현재 환경 설정 상태

**Neo4j Aura Cloud 인스턴스 생성 완료:**
- 인스턴스 ID: be57a318
- 인스턴스 이름: argo-production
- URI: neo4j+s://be57a318.databases.neo4j.io
- 사용자명: neo4j
- 비밀번호: 8a_yYS-h3jIy5jrJXYCMsg16N5LP2A00y8TckliGHRY
- 데이터베이스: neo4j

**GCP Secret Manager 설정 완료:**
- 프로젝트 ID: artdrive1208
- 저장된 시크릿:
  - NEO4J_URI: neo4j+s://be57a318.databases.neo4j.io
  - NEO4J_USER: neo4j
  - NEO4J_PASSWORD: 8a_yYS-h3jIy5jrJXYCMsg16N5LP2A00y8TckliGHRY
  - GEMINI_API_KEY: AIzaSyCPPE6RiaSXn_fzQVlva0fSdtxV8M-d5Tw
- 서비스 계정 권한 부여 완료: argo-api@artdrive1208.iam.gserviceaccount.com

**로컬 환경변수 설정 완료:**
- argo-backend/.env 파일에 모든 환경변수 설정됨

## Phase 1: Critical 수정사항 (즉시 수행)

### 1.1 Artist 모델 필드명 및 구조 수정 (P0 - Critical)

**파일**: `app/models/artist.py`

**문제점**:
1. 필드명이 문서 명세서 및 프론트엔드 타입과 불일치
2. 필수 필드 누락
3. JSON-LD 필드 구조 불일치
4. `scores`와 `coordinates_3d`가 `analysis` 내부에만 있어 프론트엔드에서 접근 불가

**수정 요구사항**:

1. **필드명 수정**:
   - `name_ko` → `alternateName` (Optional[str])
   - `birth_year` → `birthDate` (Optional[str], ISO 8601 형식: "YYYY-MM-DD")
   - `analysis` → `structuralist_analysis` (Optional[StructuralistAnalysis])

2. **필수 필드 추가** (최상위 레벨):
   - `identifier`: dict (필수) - 예: `{"@type": "PropertyValue", "value": "artist_001"}`
   - `url`: Optional[str] - 작가 공식 웹사이트
   - `segment_id`: Optional[str] - 세그먼트 분류 ID
   - `career_stage`: Optional[str] - "early", "mid", "late" 중 하나
   - `scores`: Scores (필수) - 최상위 레벨로 이동
   - `coordinates_3d`: Coordinates3D (필수) - 최상위 레벨로 이동

3. **JSON-LD 필드 구조 수정**:
   - `id` → `@id` (Field alias 사용)
   - `type` → `@type` (Field alias 사용)
   - `context` → `@context` (Field alias 사용)
   - 기본값: `@context` = "https://schema.org/", `@type` = "Person"

4. **프론트엔드 타입과 일치성 확보**:
   - `artist_id` 필드 추가 (Optional[str]) - `@id`에서 추출하거나 별도 필드
   - `scores` 최상위 레벨 (프론트엔드: `artist.scores`)
   - `coordinates_3d` 최상위 레벨 (프론트엔드: `artist.coordinates_3d`)

**수정 후 예상 구조**:

```python
class Artist(ResourceBase):
    # JSON-LD 필수 필드 (ResourceBase에서 상속)
    # @context, @type, @id
    
    # Schema.org 필드
    identifier: dict  # 필수
    name: str  # 필수
    alternateName: Optional[str] = None  # name_ko에서 변경
    birthDate: Optional[str] = None  # birth_year에서 변경, ISO 8601 형식
    url: Optional[str] = None  # 추가
    
    # ARGO 커스텀 필드 (최상위 레벨)
    segment_id: Optional[str] = None  # 추가
    career_stage: Optional[str] = Field(None, pattern="^(early|mid|late)$")  # 추가
    scores: Scores  # 필수, 최상위 레벨로 이동
    coordinates_3d: Coordinates3D  # 필수, 최상위 레벨로 이동
    structuralist_analysis: Optional[StructuralistAnalysis] = None  # analysis에서 변경
    
    # 관계 데이터 필드
    collaborations: List[Collaboration] = []
    institutions: List[InstitutionLink] = []
    exhibitions: List[ExhibitionLink] = []
    collaborators: List[str] = []  # 하위 호환성 유지
    
    # artist_id 필드 추가 (프론트엔드 호환성)
    artist_id: Optional[str] = None  # @id에서 추출하거나 별도 필드
```

**참조 문서**:
- `docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` 섹션 4.1
- `types/argo.ts` Artist 인터페이스
- `docs/ARGO_API_SPECIFICATION.yaml` components/schemas/Artist

### 1.2 Common 모델 수정 (P0 - Critical)

**파일**: `app/models/common.py`

**수정 요구사항**:

1. **Scores 모델에 필드 추가**:
   - `composite_score`: float (필수, 0-100 범위)

2. **StructuralistAnalysis 모델 구조 수정**:
   - 현재 구조: `scores`, `coordinates_3d` 포함 (잘못됨)
   - 올바른 구조:
     ```python
     class StructuralistAnalysis(BaseModel):
         dominant_capital: str = Field(..., pattern="^(institutional|academic|media|network)$")
         capital_composition: dict  # {institutional_ratio, academic_ratio, media_ratio, network_ratio}
         structural_position: dict  # {field_quadrant, position_stability, mobility_potential, ...}
         algorithm_version: str
         weights_applied: dict  # {inst, acad, media, network}
         theoretical_basis: str
     ```
   - `scores`와 `coordinates_3d`는 Artist 모델의 최상위 레벨에 있어야 함

3. **Coordinates3D 모델 필드 추가**:
   - `computed_at`: Optional[str] = None (ISO 8601 형식)
   - `algorithm`: Optional[str] = None (예: "normalize_v1")

**참조 문서**:
- `docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` 섹션 4.1.6

### 1.3 좌표 계산 로직 수정 (P0 - Critical)

**파일**: `app/services/coordinate_service.py`

**수정 요구사항**:

1. **반환 형식 수정**:
   - 현재: `Coordinates3D` 모델 반환
   - 수정: dict 반환 (JSON-LD 형식, `argo:` 네임스페이스 포함)

2. **필드 추가**:
   - `computed_at`: 현재 시간 (ISO 8601 형식)
   - `algorithm`: "normalize_v1"

**수정 후 예상 코드**:

```python
from datetime import datetime

def calculate_coordinates(scores: Scores) -> dict:
    """
    3D 갤럭시 좌표 계산 (JSON-LD 형식 반환)
    """
    x = normalize_score(scores.inst_score, SCORE_MIN, SCORE_MAX, TARGET_MIN, TARGET_MAX)
    y = normalize_score(scores.acad_score, SCORE_MIN, SCORE_MAX, TARGET_MIN, TARGET_MAX)
    z = normalize_score(scores.media_score, SCORE_MIN, SCORE_MAX, TARGET_MIN, TARGET_MAX)
    radius = 10.0 + (scores.network_score / 5.0)
    
    return {
        "argo:x": round(x, 2),
        "argo:y": round(y, 2),
        "argo:z": round(z, 2),
        "argo:radius": round(radius, 2),
        "computed_at": datetime.utcnow().isoformat() + "Z",
        "algorithm": "normalize_v1"
    }
```

**참조 문서**:
- `docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` 섹션 10

### 1.4 JSON-LD 변환 로직 개선 (P0 - Critical)

**파일**: `app/utils/jsonld.py`

**수정 요구사항**:

1. **ARGO 커스텀 필드 네임스페이스 자동 추가**:
   - 필드명이 `argo:`로 시작하지 않으면 자동으로 `argo:` 네임스페이스 추가
   - 예외: 관계 데이터 필드 (`collaborations`, `institutions`, `exhibitions`)는 네임스페이스 없음

2. **관계 데이터 필드 처리**:
   - `collaborations`, `institutions`, `exhibitions` 필드는 네임스페이스 없이 일반 배열로 제공

**수정 후 예상 코드**:

```python
def to_jsonld(
    data: Any, 
    context: str = "https://schema.org/", 
    type_name: str | None = None,
    id_uri: str | None = None
) -> Dict[str, Any]:
    """
    JSON-LD 형식으로 변환 (ARGO 커스텀 필드 네임스페이스 자동 추가)
    """
    # 관계 데이터 필드 목록 (네임스페이스 없음)
    RELATIONSHIP_FIELDS = {"collaborations", "institutions", "exhibitions", "collaborators"}
    
    if isinstance(data, list):
        return {
            "@context": context,
            "@type": "Collection",
            "member": [to_jsonld(item, context, type_name) for item in data]
        }
    
    result = data.copy() if isinstance(data, dict) else data.model_dump(by_alias=True)
    
    # JSON-LD 필수 필드 추가
    if "@context" not in result:
        result["@context"] = context
    if type_name and "@type" not in result:
        result["@type"] = type_name
    if id_uri and "@id" not in result:
        result["@id"] = id_uri
    
    # ARGO 커스텀 필드에 네임스페이스 추가
    argo_fields = {}
    for key, value in list(result.items()):
        # 관계 데이터 필드는 제외
        if key in RELATIONSHIP_FIELDS:
            continue
        
        # argo:로 시작하지 않고, JSON-LD 표준 필드가 아닌 경우
        if not key.startswith("@") and not key.startswith("argo:") and key not in ["name", "alternateName", "birthDate", "url", "identifier"]:
            argo_fields[f"argo:{key}"] = value
            del result[key]
    
    result.update(argo_fields)
    
    return result
```

**참조 문서**:
- `docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` 섹션 6.4

### 1.5 Gemini API 모델명 수정 (P0 - Critical)

**파일**: `app/routers/anomalies.py`

**수정 요구사항**:
- `gemini-pro` → `gemini-3-pro-preview` 변경

**수정 후 예상 코드**:

```python
model = genai.GenerativeModel('gemini-3-pro-preview')  # gemini-pro에서 변경
```

**참조 문서**:
- `docs/ARGO_API_SPECIFICATION.yaml` info 섹션
- 환경변수: `GEMINI_API_KEY` (이미 설정됨)

### 1.6 Artist Service 수정 (P0 - Critical)

**파일**: `app/services/artist_service.py`

**수정 요구사항**:

1. **`_map_to_artist` 메서드 수정**:
   - 필드명 변경 반영 (`name_ko` → `alternateName`, `birth_year` → `birthDate`)
   - `scores`와 `coordinates_3d`를 최상위 레벨로 설정
   - `structuralist_analysis` 필드 구조 수정
   - `artist_id` 필드 추가

2. **필수 필드 추가**:
   - `identifier` dict 생성
   - `url`, `segment_id`, `career_stage` 필드 매핑

**수정 후 예상 코드 구조**:

```python
def _map_to_artist(self, data: dict) -> Artist:
    node = data.get('a', {})
    artist_id = node.get('id') or node.get('artist_id')
    
    # Scores 생성
    scores = Scores(
        inst_score=node.get('inst_score', 0.0),
        acad_score=node.get('acad_score', 0.0),
        media_score=node.get('media_score', 0.0),
        network_score=node.get('network_score', 0.0),
        composite_score=node.get('composite_score', 0.0)  # 추가
    )
    
    # 좌표 계산 (dict 반환)
    coordinates_3d = calculate_coordinates(scores)
    
    # StructuralistAnalysis 생성 (scores, coordinates_3d 제외)
    structuralist_analysis = StructuralistAnalysis(
        dominant_capital=node.get('dominant_capital', 'institutional'),
        capital_composition=node.get('capital_composition', {}),
        structural_position=node.get('structural_position', {}),
        algorithm_version=node.get('algorithm_version', 'v1.0.0'),
        weights_applied=node.get('weights_applied', {}),
        theoretical_basis=node.get('theoretical_basis', 'Bourdieu Field Theory')
    )
    
    # 관계 데이터 파싱
    collaborations = [
        Collaboration(artist_id=c['id'], strength=c['strength']) 
        for c in data.get('collaborations', [])
        if c.get('strength', 0) >= 0.3
    ]
    
    institutions = [
        InstitutionLink(institution_id=i['id'], name=i['name'], type=i.get('type'))
        for i in data.get('institutions', [])
    ]
    
    exhibitions = [
        ExhibitionLink(exhibition_id=e['id'], name=e['name'], year=e.get('year'))
        for e in data.get('exhibitions', [])
    ]
    
    full_id = f"argo://artist/{artist_id}"
    
    return Artist(
        id=full_id,  # @id
        type="Person",  # @type
        identifier={"@type": "PropertyValue", "value": artist_id},  # 추가
        name=node.get('name', 'Unknown'),
        alternateName=node.get('name_ko') or node.get('alternateName'),  # 수정
        birthDate=node.get('birthDate') or (f"{node.get('birth_year')}-01-01" if node.get('birth_year') else None),  # 수정
        url=node.get('url'),  # 추가
        segment_id=node.get('segment_id'),  # 추가
        career_stage=node.get('career_stage'),  # 추가
        scores=scores,  # 최상위 레벨
        coordinates_3d=coordinates_3d,  # 최상위 레벨 (dict)
        structuralist_analysis=structuralist_analysis,  # 수정
        collaborations=collaborations,
        institutions=institutions,
        exhibitions=exhibitions,
        collaborators=[c.artist_id for c in collaborations],
        artist_id=artist_id  # 추가 (프론트엔드 호환성)
    )
```

**참조 문서**:
- `docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` 섹션 4.1.6
- `types/argo.ts` Artist 인터페이스

### 1.7 에러 처리 개선 (P0 - Critical)

**파일**: `app/utils/errors.py`

**수정 요구사항**:

1. **`create_error_response` 함수 수정**:
   - 현재: `HTTPException` 반환
   - 수정: `JSONResponse` 반환 (표준 에러 응답 형식)

2. **에러 코드 매핑 테이블 추가**:
   - HTTP 상태 코드별 에러 코드 매핑

**수정 후 예상 코드**:

```python
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid

# 에러 코드 매핑 테이블
ERROR_CODE_MAP = {
    400: "INVALID_PARAMETER",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_ERROR",
    503: "SERVICE_UNAVAILABLE"
}

def create_error_response(
    code: str, 
    message: str, 
    status_code: int = 400, 
    details: Optional[str] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    표준 에러 응답 생성 (JSONResponse 반환)
    """
    error_code = ERROR_CODE_MAP.get(status_code, code)
    
    error_content = ErrorResponse(
        error=ErrorDetail(
            code=error_code,
            message=message,
            details=details,
            timestamp=datetime.utcnow(),
            request_id=request_id or str(uuid.uuid4()),
            documentation=f"https://artdrive1208-api-xxx.run.app/docs/errors/{error_code}"
        )
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_content.model_dump()
    )
```

**참조 문서**:
- `docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md` 섹션 7

### 1.8 라우터 에러 처리 수정 (P0 - Critical)

**파일**: `app/routers/*.py`

**수정 요구사항**:
- 빈 객체 반환 (`return {}`) 대신 `create_error_response` 사용
- 모든 엔드포인트에서 일관된 에러 처리

**예시 수정** (`app/routers/institutions.py`):

```python
from app.utils.errors import create_error_response

@router.get("/{inst_id}", response_model=dict)
async def get_institution_detail(inst_id: str):
    query = "MATCH (i:Institution {id: $id}) RETURN i"
    result = neo4j_service.find_one(query, {"id": inst_id})
    if not result:
        raise create_error_response(
            "NOT_FOUND",
            f"Institution with ID {inst_id} not found",
            404
        )
    return to_jsonld(result['i'], type_name="Organization", id_uri=f"argo://institution/{inst_id}")
```

## Phase 2: 누락된 엔드포인트 구현 (High Priority)

### 2.1 갤럭시 및 메타데이터 API 라우터 생성 (P1)

**작업 내용**:
1. `app/routers/galaxy.py` 파일 생성
2. 다음 엔드포인트 구현:

**GET `/v1/api/galaxy-snapshot`**:
- 목적: 현재 갤럭시 스냅샷 조회 (모든 작가 데이터 포함)
- 응답 형식: JSON-LD
- 포함 데이터:
  - 모든 Artist 목록 (페이지네이션 가능)
  - Cluster 목록 (선택사항)
  - 메타데이터 (생성 시간, 버전 등)

**GET `/v1/api/metadata/sources`**:
- 목적: 데이터 출처 정보 조회
- 응답 형식: JSON-LD
- 포함 데이터:
  - 데이터 소스 목록 (ARKO, KCI, web_crawl 등)
  - 각 소스별 데이터 개수
  - 최종 업데이트 시간

3. `app/main.py`에 라우터 등록:
```python
from app.routers import galaxy

app.include_router(galaxy.router)
```

**참조 문서**:
- `docs/ARGO_API_SPECIFICATION.yaml` paths 섹션
- `docs/ARGO_GCP_INFRASTRUCTURE_SETUP.md` 섹션 1.9

### 2.2 작가 API 누락 엔드포인트 구현 (P1)

**파일**: `app/routers/artists.py`

**추가할 엔드포인트**:

1. **GET `/v1/api/artists/{artist_id}/artworks`**:
   - 작가의 작품 목록 조회
   - Neo4j 쿼리: `MATCH (a:Artist {id: $artist_id})-[:CREATED]->(w:Artwork) RETURN w`
   - 응답 형식: JSON-LD Collection

2. **GET `/v1/api/artists/{artist_id}/structural-equivalents`**:
   - 구조적 등가성 작가 조회 (임계값 0.15)
   - Neo4j 쿼리: 구조적 등가성 알고리즘 사용
   - 응답 형식: JSON-LD Collection

3. **GET `/v1/api/artists/{artist_id}/capital-composition`**:
   - 자본 구성 분석 조회
   - `structuralist_analysis.capital_composition` 데이터 반환
   - 응답 형식: JSON-LD

4. **GET `/v1/api/artists/{artist_id}/market`**:
   - 작가 시장 정보 조회 (거래 이력, 가격 추이)
   - Neo4j 쿼리: `MATCH (a:Artist {id: $artist_id})<-[:SOLD_IN]-(t:Transaction) RETURN t ORDER BY t.transaction_date DESC`
   - 응답 형식: JSON-LD

5. **POST `/v1/api/artists/search`**:
   - 작가 전문 검색 (이름, 기관, 세그먼트 등)
   - 요청 본문: `{"query": "검색어", "filters": {...}}`
   - Neo4j 쿼리: Full-text search 또는 MATCH 쿼리
   - 응답 형식: JSON-LD Collection

**참조 문서**:
- `docs/ARGO_API_SPECIFICATION.yaml` paths 섹션
- `docs/ARGO_Final_Schema.md` Cypher 쿼리 예제

### 2.3 기관 API 누락 엔드포인트 구현 (P1)

**파일**: `app/routers/institutions.py`

**추가할 엔드포인트**:

1. **GET `/v1/api/institutions/{inst_id}/affiliated-artists`**:
   - 기관 소속 미술가 목록 조회
   - Neo4j 쿼리: `MATCH (i:Institution {id: $inst_id})<-[:AFFILIATED_WITH]-(a:Artist) RETURN a`
   - 응답 형식: JSON-LD Collection

2. **GET `/v1/api/institutions/{inst_id}/exhibitions`**:
   - 기관 전시 목록 조회
   - Neo4j 쿼리: `MATCH (i:Institution {id: $inst_id})-[:ORGANIZED_EXHIBITION]->(e:Exhibition) RETURN e`
   - 응답 형식: JSON-LD Collection

3. **GET `/v1/api/institutions/{inst_id}/benchmarking`**:
   - 기관 벤치마킹 조회
   - 다른 기관과의 비교 데이터 반환
   - 응답 형식: JSON-LD

**참조 문서**:
- `docs/ARGO_API_SPECIFICATION.yaml` paths 섹션

### 2.4 거래 API 누락 엔드포인트 구현 (P1)

**파일**: `app/routers/transactions.py`

**수정 및 추가할 엔드포인트**:

1. **GET `/v1/api/transactions/{trans_id}` (TODO 해결)**:
   - 거래 상세 정보 조회
   - Neo4j 쿼리: `MATCH (t:Transaction {id: $trans_id}) RETURN t`
   - 응답 형식: JSON-LD

2. **GET `/v1/api/transactions/price-history/{artist_id}` (새로 추가)**:
   - 작가 거래 가격 히스토리 조회
   - Neo4j 쿼리: `MATCH (a:Artist {id: $artist_id})<-[:SOLD_IN]-(t:Transaction) RETURN t ORDER BY t.transaction_date ASC`
   - 응답 형식: JSON-LD Collection

**참조 문서**:
- `docs/ARGO_API_SPECIFICATION.yaml` paths 섹션

## Phase 3: TODO 엔드포인트 구현 (Medium Priority)

### 3.1 작가 API TODO 해결 (P2)

**파일**: `app/routers/artists.py`

**구현할 엔드포인트**:

1. **GET `/v1/api/artists/{artist_id}/network`**:
   - 작가 네트워크 그래프 조회 (1홉/2홉)
   - 파라미터: `depth` (1 또는 2, 기본값: 1)
   - Neo4j 쿼리: `MATCH path = (a:Artist {id: $artist_id})-[*1..2]-(connected:Artist) RETURN path`
   - 응답 형식: NetworkGraph (nodes, edges)

2. **GET `/v1/api/artists/{artist_id}/exhibitions` (TODO 해결)**:
   - 작가 전시 목록 조회 (상세 정보 포함)
   - Neo4j 쿼리: `MATCH (a:Artist {id: $artist_id})-[:PARTICIPATED_IN]->(e:Exhibition) RETURN e, e.role, e.artworks_count`
   - 응답 형식: JSON-LD Collection

**참조 문서**:
- `docs/ARGO_API_SPECIFICATION.yaml` paths 섹션
- `docs/ARGO_Final_Schema.md` 관계 타입 정의

### 3.2 분석 API 구현 (P2)

**파일**: `app/routers/analysis.py`

**구현할 엔드포인트** (현재 모두 "Not implemented yet"):

1. **POST `/v1/api/analysis/centrality`**:
   - 중심성 계산 (Degree, Betweenness, Eigenvector)
   - 요청 본문: `{"artist_ids": ["artist_001", "artist_002"], "metrics": ["degree", "betweenness", "eigenvector"]}`
   - Neo4j 쿼리: GDS 라이브러리 사용 또는 Cypher 쿼리
   - 응답 형식: JSON-LD

2. **POST `/v1/api/analysis/community-detection`**:
   - 커뮤니티 탐지 (Louvain 알고리즘)
   - 요청 본문: `{"resolution": 1.0}`
   - Neo4j 쿼리: GDS 라이브러리 사용
   - 응답 형식: JSON-LD Collection

3. **GET `/v1/api/analysis/correlation`**:
   - 상관관계 분석
   - 쿼리 파라미터: `metric1`, `metric2` (예: inst_score, acad_score)
   - Neo4j 쿼리: 통계 계산
   - 응답 형식: JSON-LD

4. **POST `/v1/api/analysis/compare`**:
   - 작가 비교 분석
   - 요청 본문: `{"artist_ids": ["artist_001", "artist_002"]}`
   - Neo4j 쿼리: 두 작가의 데이터 비교
   - 응답 형식: JSON-LD

5. **GET `/v1/api/analysis/field-quadrants`**:
   - 필드 분면 분류 조회
   - 모든 작가의 field_quadrant 분포 반환
   - Neo4j 쿼리: `MATCH (a:Artist) RETURN a.structuralist_analysis.structural_position.field_quadrant, count(a)`
   - 응답 형식: JSON-LD

**참조 문서**:
- `docs/ARGO_API_SPECIFICATION.yaml` paths 섹션
- `docs/ARGO_Final_Schema.md` 분석 쿼리 예제

### 3.3 군집 API TODO 해결 (P2)

**파일**: `app/routers/clusters.py`

**구현할 엔드포인트**:

1. **GET `/v1/api/clusters/{cluster_id}` (TODO 해결)**:
   - 군집 상세 정보 조회
   - Neo4j 쿼리: `MATCH (c:Cluster {id: $cluster_id}) RETURN c`
   - 포함된 작가 목록도 함께 반환
   - 응답 형식: JSON-LD

**참조 문서**:
- `docs/ARGO_API_SPECIFICATION.yaml` paths 섹션

## Phase 4: 개선 및 최적화 (Low Priority)

### 4.1 필터 파라미터 추가 (P3)

**파일**: `app/routers/artists.py`

**수정 요구사항**:
- GET `/v1/api/artists` 엔드포인트에 필터 파라미터 추가:
  - `segment_id`: Optional[str]
  - `career_stage`: Optional[str] (enum: early, mid, late)
  - `min_score`: Optional[float] (0-100)
- 페이지네이션 파라미터 수정:
  - `skip` → `page` (1부터 시작, 기본값: 1)
  - `limit` 유지 (기본값: 20, 최대: 100)

**수정 후 예상 코드**:

```python
@router.get("", response_model=dict)
async def get_artists(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    segment_id: Optional[str] = Query(None, description="Filter by segment ID"),
    career_stage: Optional[str] = Query(None, pattern="^(early|mid|late)$", description="Filter by career stage"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum composite score")
):
    skip = (page - 1) * limit
    artists = await artist_service.get_all_artists(limit, skip, segment_id, career_stage, min_score)
    return to_jsonld([a.model_dump(by_alias=True) for a in artists])
```

### 4.2 Neo4j 쿼리 최적화 (P3)

**파일**: `app/services/neo4j_service.py`

**개선 요구사항**:
1. 에러 처리 강화
2. 연결 풀 관리 개선
3. 쿼리 타임아웃 설정

## 검증 체크리스트

수정 완료 후 다음 항목들을 검증하세요:

### 필수 검증 항목
- [ ] Artist 모델 필드명이 문서 명세서와 일치하는가?
- [ ] Artist 모델 필드명이 프론트엔드 타입(`types/argo.ts`)과 일치하는가?
- [ ] `scores`와 `coordinates_3d`가 최상위 레벨에 있는가?
- [ ] 모든 응답에 JSON-LD 필수 필드(`@context`, `@type`, `@id`)가 포함되는가?
- [ ] ARGO 커스텀 필드에 `argo:` 네임스페이스가 자동 추가되는가?
- [ ] 관계 데이터 필드(`collaborations`, `institutions`, `exhibitions`)는 네임스페이스 없이 제공되는가?
- [ ] 좌표 계산 결과에 `computed_at`, `algorithm` 필드가 포함되는가?
- [ ] Gemini API 모델명이 `gemini-3-pro-preview`인가?
- [ ] 모든 엔드포인트에서 일관된 에러 처리가 사용되는가?
- [ ] 누락된 11개 엔드포인트가 모두 구현되었는가?

### 성능 검증 항목
- [ ] API 응답 시간이 200ms 이하인가?
- [ ] 페이지네이션이 올바르게 작동하는가?

## 참조 문서

수정 시 다음 문서를 참조하세요:

1. **`docs/ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md`**
   - 섹션 4: API 스키마 명시
   - 섹션 6: JSON-LD 형식 명시
   - 섹션 7: 에러 응답 형식
   - 섹션 10: 좌표 계산 로직

2. **`docs/ARGO_API_SPECIFICATION.yaml`**
   - 모든 엔드포인트의 상세 스키마 정의
   - 요청/응답 예제

3. **`types/argo.ts`**
   - 프론트엔드 TypeScript 타입 정의
   - 타입 일치성 검증용

4. **`docs/ARGO_Final_Schema.md`**
   - Neo4j 데이터베이스 스키마
   - Cypher 쿼리 예제

## 환경 설정 확인

**Neo4j 연결 테스트**:
수정 후 다음 명령어로 연결을 테스트하세요:

```python
from app.database import db
from app.services.neo4j_service import neo4j_service

# 연결 테스트
result = neo4j_service.execute_query("RETURN 1 as test")
print(f"Neo4j 연결 성공: {result}")
```

**GCP Secret Manager 확인**:
프로덕션 환경에서는 다음 코드로 Secret Manager에서 환경변수를 읽어야 합니다:

```python
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/artdrive1208/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

## 작업 완료 후 확인사항

1. 모든 수정사항이 적용되었는지 확인
2. `verify_backend.py` 스크립트 실행하여 기본 검증
3. 로컬 환경에서 FastAPI 서버 실행 테스트
4. Swagger UI (`http://localhost:8000/docs`)에서 모든 엔드포인트 확인
5. 프론트엔드와 연동 테스트 (가능한 경우)

---

**중요**: 이 프롬프트의 모든 수정사항을 정확히 따라주세요. 특히 Phase 1 (Critical) 수정사항은 프론트엔드 연동에 필수적입니다.
```

---

## 사용 방법

이 프롬프트를 Antigravity IDE에 복사하여 붙여넣고 실행하세요. Antigravity IDE가 코드베이스를 분석하고 위의 수정사항을 순차적으로 적용할 것입니다.

**예상 작업 시간**:
- Phase 1 (Critical): 3-4시간
- Phase 2 (High): 1-2일
- Phase 3 (Medium): 1주
- Phase 4 (Low): 1주

**우선순위**: Phase 1부터 순차적으로 진행하세요.

