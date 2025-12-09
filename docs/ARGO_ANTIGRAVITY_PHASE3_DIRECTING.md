# ARGO Antigravity Phase 3 세부 디렉팅 가이드
## Phase 3 Detailed Directing Guide

**작성일**: 2025-12-09  
**버전**: 1.0  
**프로젝트 ID**: artdrive1208  
**상태**: Phase 2.5 완료 검증 후 Phase 3 디렉팅

---

## 1. Phase 2.5 검증 결과 요약

### ✅ 완료된 항목

1. **타입 정제 (Phase 1.5)**
   - ✅ `alternativeName` alias 추가 (`Artist` 모델)
   - ✅ `Coordinates3D` Pydantic 모델 타입 강제
   - ✅ 에러 응답 일관성 개선 (`artists.py`)

2. **로직 구현 (Phase 2.5)**
   - ✅ Galaxy & Metadata: 실제 Cypher 쿼리로 교체
   - ✅ `get_structural_equivalents`: Jaccard Similarity 알고리즘 구현
   - ✅ `get_capital_composition`: 자본 구성 비율 계산 구현
   - ✅ `search_artists`: 고급 필터링 구현

### ⚠️ 발견된 문제점 (Critical)

#### P0: 누락된 메서드

**문제**: `get_artist_by_id` 메서드가 `ArtistService`에 없음

**위치**: `argo-backend/app/routers/artists.py:26`
```python
artist = await artist_service.get_artist_by_id(artist_id)
```

**영향**: `/v1/api/artists/{artist_id}` 엔드포인트가 작동하지 않음

**요구사항**:
- 단일 작가 조회 시 **관계 데이터 포함** (collaborations, institutions, exhibitions)
- Neo4j 쿼리에서 관계를 함께 가져와야 함
- `_map_to_artist` 메서드 활용

**예상 구현**:
```python
async def get_artist_by_id(self, artist_id: str) -> Optional[Artist]:
    """
    Get a single artist by ID with full relationship data.
    Uses correct relationship types from ARGO_Final_Schema.md:
    - COLLABORATED_WITH (Artist ↔ Artist)
    - AFFILIATED_WITH (Artist ↔ Institution)
    - PARTICIPATED_IN (Artist ↔ Exhibition)
    """
    query = """
    MATCH (a:Artist {id: $artist_id})
    
    // Get collaborations (COLLABORATED_WITH relationship)
    OPTIONAL MATCH (a)-[r1:COLLABORATED_WITH]->(collab:Artist)
    WITH a, collect({id: collab.id, strength: r1.strength}) as collaborations
    
    // Get institutions (AFFILIATED_WITH relationship)
    OPTIONAL MATCH (a)-[:AFFILIATED_WITH]->(inst:Institution)
    WITH a, collaborations, collect({
        id: inst.id, 
        name: inst.name, 
        type: inst.institution_type
    }) as institutions
    
    // Get exhibitions (PARTICIPATED_IN relationship)
    OPTIONAL MATCH (a)-[:PARTICIPATED_IN]->(exh:Exhibition)
    WITH a, collaborations, institutions, collect({
        id: exh.id, 
        name: exh.name, 
        year: exh.year
    }) as exhibitions
    
    RETURN a, collaborations, institutions, exhibitions
    """
    result = neo4j_service.find_one(query, {"artist_id": artist_id})
    
    if not result:
        return None
    
    return self._map_to_artist(result)
```

---

#### P1: 관계 타입 불일치

**문제**: `get_structural_equivalents`에서 관계 타입이 `COLLABORATED`로 사용됨

**위치**: `argo-backend/app/services/artist_service.py:120`
```python
OPTIONAL MATCH (a)-[r1:COLLABORATED]->(n)
```

**스키마 확인 완료**: `ARGO_Final_Schema.md`에서 실제 관계 타입 확인
- ✅ **정확한 관계 타입**: `COLLABORATED_WITH` (라인 724, 902, 938)
- ❌ **현재 코드 사용**: `COLLABORATED` (잘못된 타입)

**해결 방법**:
1. `get_structural_equivalents`에서 `COLLABORATED` → `COLLABORATED_WITH`로 수정
2. 모든 관계 쿼리에서 `COLLABORATED_WITH` 사용
3. `get_artist_by_id` 구현 시에도 `COLLABORATED_WITH` 사용

---

#### P1: 관계 데이터 누락

**문제**: `get_all_artists`에서 관계 데이터를 가져오지 않음

**위치**: `argo-backend/app/services/artist_service.py:91-101`
```python
async def get_all_artists(self, limit: int = 20, skip: int = 0) -> List[Artist]:
    query = """
    MATCH (a:Artist)
    RETURN a
    SKIP $skip LIMIT $limit
    """
    results = neo4j_service.execute_query(query, {"skip": skip, "limit": limit})
    return [self._map_to_artist(r) for r in results]
```

**영향**: 
- 리스트 조회 시 `collaborations`, `institutions`, `exhibitions`가 빈 배열
- 프론트엔드에서 관계 데이터를 사용할 수 없음

**해결 방법**:
- **옵션 A**: 성능 우선 - 리스트 조회 시 관계 데이터 제외 (현재 상태 유지)
- **옵션 B**: 기능 우선 - 리스트 조회 시에도 관계 데이터 포함 (성능 저하 가능)

**권장**: 옵션 A 유지, `get_artist_by_id`에서만 관계 데이터 포함

---

#### P2: 에러 응답 일관성

**문제**: `clusters.py`에서 에러 응답이 일관되지 않음

**위치**: `argo-backend/app/routers/clusters.py:16`
```python
@router.get("/{cluster_id}", response_model=dict)
async def get_cluster_detail(cluster_id: str):
    return {"message": "Not implemented yet"}
```

**요구사항**: `create_error_response` 사용하여 일관된 에러 응답

**수정 예시**:
```python
from app.utils.errors import create_error_response

@router.get("/{cluster_id}", response_model=dict)
async def get_cluster_detail(cluster_id: str):
    return create_error_response(
        "NOT_IMPLEMENTED",
        "Cluster detail endpoint is not implemented yet",
        status_code=501
    )
```

---

## 2. Phase 3 작업 지시

### Phase 3.1: Critical Fixes (P0)

#### 작업 1: `get_artist_by_id` 메서드 구현

**파일**: `argo-backend/app/services/artist_service.py`

**요구사항**:
1. 단일 작가 조회
2. 관계 데이터 포함 (collaborations, institutions, exhibitions)
3. Neo4j 쿼리에서 관계를 함께 가져오기
4. `_map_to_artist` 메서드 활용
5. 작가가 없을 경우 `None` 반환

**검증 방법**:
```python
# verify_backend.py에 추가
print("\n5. Testing get_artist_by_id...")
artist = await artist_service.get_artist_by_id("test_artist_id")
if artist:
    assert artist.collaborations is not None
    assert artist.institutions is not None
    assert artist.exhibitions is not None
    print("✅ get_artist_by_id with relationships verified")
else:
    print("⚠️ get_artist_by_id returned None (expected if test_artist_id doesn't exist)")
```

---

#### 작업 2: 관계 타입 확인 및 수정

**파일**: 
- `argo-backend/app/services/artist_service.py`
- `docs/ARGO_Final_Schema.md` 참조

**단계**:
1. ✅ `ARGO_Final_Schema.md` 확인 완료 (라인 724)
2. `get_structural_equivalents`의 관계 타입 수정: `COLLABORATED` → `COLLABORATED_WITH`
3. 모든 관계 쿼리에서 일관성 확인

**정확한 관계 타입** (`ARGO_Final_Schema.md` 기준):
- `COLLABORATED_WITH` (Artist ↔ Artist) - 라인 724
- `AFFILIATED_WITH` (Artist ↔ Institution) - 라인 743
- `PARTICIPATED_IN` (Artist ↔ Exhibition) - 확인 필요
- `CREATED` (Artist → Artwork)
- `HOSTED` (Institution → Exhibition)

**수정 필요 위치**:
- `argo-backend/app/services/artist_service.py:120` - `COLLABORATED` → `COLLABORATED_WITH`
- `argo-backend/app/services/artist_service.py:125` - `COLLABORATED` → `COLLABORATED_WITH`

---

### Phase 3.2: High Priority Fixes (P1)

#### 작업 3: 에러 응답 일관성 개선

**파일**: `argo-backend/app/routers/clusters.py`

**요구사항**:
- `create_error_response` 사용
- 일관된 에러 코드 및 메시지
- 적절한 HTTP 상태 코드 (501: Not Implemented)

---

### Phase 3.3: Medium Priority Improvements (P2)

#### 작업 4: Analysis API 로직 구현

**파일**: `argo-backend/app/routers/analysis.py`

**현재 상태**: 모든 엔드포인트가 "Not implemented yet"

**구현 필요 엔드포인트**:
1. `/v1/api/analysis/centrality` - 중심성 분석
2. `/v1/api/analysis/community-detection` - 커뮤니티 탐지
3. `/v1/api/analysis/correlation` - 상관관계 분석
4. `/v1/api/analysis/compare` - 작가 비교
5. `/v1/api/analysis/field-quadrants` - 필드 사분면 분석

**참조 문서**:
- `ARGO_API_SPECIFICATION.yaml` 섹션 `/v1/api/analysis/*`
- `ARGO_STRUCTURALIST_ALGORITHM_DESIGN.md`

---

#### 작업 5: Institution 및 Cluster 상세 엔드포인트 구현

**파일**:
- `argo-backend/app/routers/institutions.py`
- `argo-backend/app/routers/clusters.py`

**요구사항**:
- `/v1/api/institutions/{inst_id}` 상세 정보
- `/v1/api/clusters/{cluster_id}` 상세 정보
- 관계 데이터 포함

---

## 3. 검증 체크리스트

### Phase 3.1 검증 (Critical)

- [ ] `get_artist_by_id` 메서드 구현 확인
- [ ] 단일 작가 조회 시 관계 데이터 포함 확인
- [ ] 관계 타입 일치성 확인
- [ ] `verify_backend.py` 테스트 통과

### Phase 3.2 검증 (High Priority)

- [ ] `clusters.py` 에러 응답 일관성 확인
- [ ] 모든 라우터에서 `create_error_response` 사용 확인

### Phase 3.3 검증 (Medium Priority)

- [ ] Analysis API 엔드포인트 구현 확인
- [ ] Institution 상세 엔드포인트 구현 확인
- [ ] Cluster 상세 엔드포인트 구현 확인

---

## 4. 코드 품질 기준

### 타입 안정성
- 모든 반환 타입 명시
- Pydantic 모델 사용
- `Optional` 타입 적절히 사용

### 에러 처리
- `create_error_response` 사용
- 적절한 HTTP 상태 코드
- 일관된 에러 메시지 형식

### Neo4j 쿼리
- 파라미터화된 쿼리 사용 (`$param`)
- 관계 타입 일치성 확인
- 성능 최적화 (필요 시)

### 테스트
- `verify_backend.py` 테스트 통과
- 각 메서드별 단위 테스트 고려

---

## 5. 참조 문서

### 필수 참조
- `ARGO_API_SPECIFICATION.yaml`: API 엔드포인트 명세
- `ARGO_Final_Schema.md`: Neo4j 스키마 및 관계 타입
- `ARGO_ANTIGRAVITY_BACKEND_SPECIFICATION.md`: 백엔드 개발 명세서

### 선택 참조
- `ARGO_STRUCTURALIST_ALGORITHM_DESIGN.md`: 알고리즘 설계
- `types/argo.ts`: 프론트엔드 타입 정의

---

## 6. 예상 작업 시간

- **Phase 3.1 (Critical)**: 2-3시간
  - `get_artist_by_id` 구현: 1시간
  - 관계 타입 확인 및 수정: 30분
  - 검증: 30분

- **Phase 3.2 (High Priority)**: 30분
  - 에러 응답 일관성: 15분
  - 검증: 15분

- **Phase 3.3 (Medium Priority)**: 4-6시간
  - Analysis API 구현: 3-4시간
  - Institution/Cluster 상세: 1-2시간

**총 예상 시간**: 7-10시간

---

## 7. 다음 단계 (Phase 4)

Phase 3 완료 후:
1. 전체 API 엔드포인트 통합 테스트
2. 성능 최적화 (필요 시)
3. 문서화 업데이트
4. 프론트엔드 연동 테스트

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025-12-09  
**작성자**: ARGO 개발팀  
**다음 검토 예정일**: Phase 3 완료 후

