# Pydantic 검증 로직 및 구현 위치 가이드

**작성일**: 2025-01-XX  
**목적**: Pydantic 모델 및 검증 로직의 위치와 사용 방법 정리

---

## Pydantic 모델 정의 위치

### 1. 공통 모델 (`app/models/common.py`)

**위치**: `argo-backend/app/models/common.py`

**구현된 모델**:

#### `Scores` 모델
```python
class Scores(BaseModel):
    inst_score: float = Field(ge=0, le=100)  # 0-100 범위 검증
    acad_score: float = Field(ge=0, le=100)
    media_score: float = Field(ge=0, le=100)
    network_score: float = Field(ge=0, le=100)
    composite_score: float = Field(ge=0, le=100)
    composite_confidence: Optional[float] = Field(None, ge=0, le=1)  # 0-1 범위 검증
```

**검증 로직**:
- ✅ `ge=0, le=100`: 점수는 0-100 범위
- ✅ `ge=0, le=1`: 신뢰도는 0-1 범위
- ✅ 자동 타입 검증 (float)

#### `Coordinates3D` 모델
```python
class Coordinates3D(BaseModel):
    x: float
    y: float
    z: float
    radius: float
    computed_at: Optional[str] = None
    algorithm: Optional[str] = None
```

**검증 로직**:
- ✅ 자동 타입 검증 (float, Optional[str])

#### `StructuralistAnalysis` 모델
```python
class StructuralistAnalysis(BaseModel):
    dominant_capital: str = Field(..., pattern="^(institutional|academic|media|network)$")
    capital_composition: Dict[str, float]
    structural_position: Dict[str, Any]
    algorithm_version: str
    weights_applied: Dict[str, float]
    theoretical_basis: str
```

**검증 로직**:
- ✅ `pattern="^...$"`: dominant_capital은 4가지 값만 허용
- ✅ 필수 필드 검증 (`...` 표시)
- ✅ 자동 타입 검증

---

### 2. Artist 모델 (`app/models/artist.py`)

**위치**: `argo-backend/app/models/artist.py`

**구현된 모델**:

#### `Artist` 모델
```python
class Artist(ResourceBase):
    identifier: PropertyValue
    name: str
    alternateName: Optional[str] = Field(None, alias="alternateName")
    alternativeName: Optional[str] = Field(None, alias="alternativeName")
    birthDate: Optional[str] = None
    url: Optional[str] = None
    segment_id: Optional[str] = None
    career_stage: Optional[str] = Field(None, pattern="^(early|mid|late)$")
    birth_year: Optional[int] = Field(None, alias="birth_year")
    artist_id: Optional[str] = None
    scores: Scores  # Pydantic 모델 타입
    coordinates_3d: Coordinates3D  # Pydantic 모델 타입
    structuralist_analysis: Optional[StructuralistAnalysis] = None
    collaborations: List[Collaboration] = []
    institutions: List[InstitutionLink] = []
    exhibitions: List[ExhibitionLink] = []
    collaborators: List[str] = []
```

**검증 로직**:
- ✅ `pattern="^(early|mid|late)$"`: career_stage는 3가지 값만 허용
- ✅ 중첩 모델 검증 (`Scores`, `Coordinates3D`, `StructuralistAnalysis`)
- ✅ 리스트 타입 검증 (`List[Collaboration]` 등)

#### `Collaboration` 모델
```python
class Collaboration(BaseModel):
    artist_id: str
    strength: float = Field(ge=0.0, le=1.0)  # 0.0-1.0 범위 검증
```

**검증 로직**:
- ✅ `ge=0.0, le=1.0`: strength는 0.0-1.0 범위

---

### 3. 엔티티 모델 (`app/models/entities.py`)

**위치**: `argo-backend/app/models/entities.py`

**구현된 모델**:
- `Institution`
- `Exhibition`
- `Transaction`
- `Cluster`

---

## Pydantic 검증 실행 위치

### 1. API 라우터에서의 검증

**위치**: `app/routers/artists.py` 등

**방법**: FastAPI가 자동으로 Pydantic 모델 검증 수행

```python
@router.get("/artists/{artist_id}", response_model=Artist)
async def get_artist_detail(artist_id: str):
    # FastAPI가 response_model=Artist로 자동 검증
    artist = await artist_service.get_artist_by_id(artist_id)
    return to_jsonld(artist.model_dump(by_alias=True))
```

---

### 2. 서비스 레이어에서의 검증

**위치**: `app/services/artist_service.py`

**메서드**: `_map_to_artist()`

**검증 실행 시점**:
```python
def _map_to_artist(self, data: dict) -> Artist:
    # 1. Scores 모델 인스턴스화 (자동 검증)
    scores = Scores(
        inst_score=node.get('inst_score', 0.0),
        acad_score=node.get('acad_score', 0.0),
        # ... 검증 자동 수행
    )
    
    # 2. Coordinates3D 모델 인스턴스화 (자동 검증)
    coordinates_3d=Coordinates3D(**coords)
    
    # 3. StructuralistAnalysis 모델 인스턴스화 (자동 검증)
    structuralist_analysis = StructuralistAnalysis(...)
    
    # 4. Artist 모델 인스턴스화 (자동 검증)
    return Artist(
        scores=scores,
        coordinates_3d=coordinates_3d,
        structuralist_analysis=structuralist_analysis,
        # ... 모든 필드 검증 자동 수행
    )
```

**검증 내용**:
- ✅ 필수 필드 존재 여부
- ✅ 타입 일치 여부
- ✅ 범위 검증 (ge, le)
- ✅ 패턴 검증 (pattern)
- ✅ 중첩 모델 검증

---

### 3. 데이터 수집 파이프라인에서의 검증

**위치**: `data_collection_pipeline.py`

**사용**: `app/validators/data_validator.py` (일반 검증 로직)

**차이점**:
- `DataValidator`: Pydantic이 아닌 일반 Python 검증 로직
- 데이터 수집 단계에서 사용 (Pydantic 모델 생성 전)
- Pydantic 모델: API 응답 및 서비스 레이어에서 사용

---

## 검증 로직 종류

### 1. Field 제약조건 검증 (자동)

**위치**: `app/models/common.py`, `app/models/artist.py`

**예시**:
```python
# 범위 검증
inst_score: float = Field(ge=0, le=100)

# 패턴 검증
dominant_capital: str = Field(..., pattern="^(institutional|academic|media|network)$")
career_stage: Optional[str] = Field(None, pattern="^(early|mid|late)$")

# 필수 필드
name: str  # 필수 (기본값 없음)
composite_confidence: Optional[float] = Field(None, ...)  # 선택적
```

### 2. 타입 검증 (자동)

**Pydantic이 자동으로 수행**:
- `float` 타입 검증
- `str` 타입 검증
- `int` 타입 검증
- `List[...]` 타입 검증
- `Optional[...]` 타입 검증
- 중첩 모델 타입 검증

### 3. 커스텀 검증 로직 (현재 없음)

**현재 상태**: 커스텀 `@field_validator` 또는 `@model_validator` 없음

**필요 시 추가 가능**:
```python
from pydantic import field_validator, model_validator

class Scores(BaseModel):
    inst_score: float = Field(ge=0, le=100)
    
    @field_validator('inst_score')
    @classmethod
    def validate_inst_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('inst_score must be between 0 and 100')
        return v
```

---

## 검증 실행 흐름

### 1. API 요청 → 응답 흐름

```
1. FastAPI 라우터
   ↓
2. ArtistService.get_artist_by_id()
   ↓
3. _map_to_artist() 메서드
   ↓
4. Pydantic 모델 인스턴스화 (자동 검증)
   - Scores(...) → 검증 수행
   - Coordinates3D(...) → 검증 수행
   - StructuralistAnalysis(...) → 검증 수행
   - Artist(...) → 검증 수행
   ↓
5. to_jsonld() 변환
   ↓
6. FastAPI response_model 검증 (추가 검증)
   ↓
7. JSON 응답 반환
```

### 2. 데이터 수집 파이프라인 흐름

```
1. 데이터 수집 (ARKO API 등)
   ↓
2. DataValidator.validate_artist() (일반 검증)
   ↓
3. 데이터 정규화
   ↓
4. 점수 계산
   ↓
5. Neo4j 업로드 (Pydantic 모델 사용 안 함)
```

---

## 검증 오류 처리

### Pydantic ValidationError 발생 시

**위치**: `app/services/artist_service.py`의 `_map_to_artist()` 메서드

**현재 상태**: try-except 블록 없음 (검증 오류 시 예외 발생)

**권장 개선**:
```python
from pydantic import ValidationError

def _map_to_artist(self, data: dict) -> Optional[Artist]:
    try:
        scores = Scores(...)
        coordinates_3d = Coordinates3D(**coords)
        return Artist(...)
    except ValidationError as e:
        logger.error(f"Pydantic 검증 실패: {e}")
        return None
```

---

## 현재 구현 상태 요약

### ✅ 구현된 검증

1. **Field 제약조건 검증**
   - 범위 검증: `ge=0, le=100`, `ge=0, le=1`
   - 패턴 검증: `pattern="^...$"`
   - 필수 필드 검증: `...` 표시

2. **타입 검증**
   - 자동 타입 변환 및 검증
   - 중첩 모델 검증

3. **모델 인스턴스화 시점 검증**
   - `Scores(...)`, `Coordinates3D(...)`, `Artist(...)` 생성 시 자동 검증

### ⚠️ 미구현된 검증

1. **커스텀 Validator 함수**
   - `@field_validator` 없음
   - `@model_validator` 없음

2. **검증 오류 처리**
   - `ValidationError` 예외 처리 없음
   - 검증 실패 시 로깅 없음

---

## 파일 위치 요약

| 파일 | 내용 | 검증 타입 |
|------|------|----------|
| `app/models/common.py` | Scores, Coordinates3D, StructuralistAnalysis | Field 제약조건 |
| `app/models/artist.py` | Artist, Collaboration, InstitutionLink, ExhibitionLink | Field 제약조건, 패턴 검증 |
| `app/models/entities.py` | Institution, Exhibition, Transaction, Cluster | 기본 타입 검증 |
| `app/services/artist_service.py` | 모델 인스턴스화 (검증 실행) | 자동 검증 |
| `app/validators/data_validator.py` | 일반 검증 로직 (Pydantic 아님) | 수동 검증 |

---

## 검증 로직 확인 방법

### 1. 모델 정의 확인
```bash
# 공통 모델
cat app/models/common.py

# Artist 모델
cat app/models/artist.py

# 엔티티 모델
cat app/models/entities.py
```

### 2. 검증 실행 위치 확인
```bash
# 서비스 레이어에서 모델 인스턴스화
grep -n "Scores\|Coordinates3D\|Artist\|StructuralistAnalysis" app/services/artist_service.py
```

### 3. 검증 오류 테스트
```python
# 잘못된 데이터로 모델 생성 시도
from app.models.common import Scores

try:
    scores = Scores(inst_score=150)  # 범위 초과
except ValidationError as e:
    print(e)  # 검증 오류 확인
```

---

## 결론

**Pydantic 검증 로직 위치**:
1. ✅ **모델 정의**: `app/models/` 디렉토리
2. ✅ **검증 실행**: `app/services/artist_service.py`의 `_map_to_artist()` 메서드
3. ✅ **검증 타입**: Field 제약조건 (ge, le, pattern)
4. ⚠️ **커스텀 Validator**: 없음 (필요 시 추가 가능)

**검증은 자동으로 수행되며**, 모델 인스턴스화 시점에 Pydantic이 자동으로 검증합니다.


