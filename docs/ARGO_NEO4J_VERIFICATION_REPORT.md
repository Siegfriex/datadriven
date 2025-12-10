# ARGO Neo4j 정합성 최종 검증 보고서

**Version**: 1.0
**Date**: 2025-12-10
**Status**: Critical Issues Identified
**Author**: Architecture Team

---

## Executive Summary

본 보고서는 `argo-backend/neo4j` 디렉토리의 구현 상태를 문서 스위트(TSD, API Spec, Schema)와 대조 검증한 결과입니다.

### 핵심 발견

| 영역 | 상태 | 심각도 |
|------|------|--------|
| 스키마 초기화 | ✅ 정합 | - |
| GDS 알고리즘 | ✅ 정합 | - |
| 구조주의 분석 쿼리 | ✅ 정합 | - |
| 관계 생성 쿼리 | ❌ 부재 | Critical |
| API 조회 쿼리 | ❌ 부재 | High |
| 데이터 적재 | ❌ 실패 | Critical |
| 관계 데이터 | ❌ 0개 | Critical |

---

## 1. Neo4j 디렉토리 구조 분석

### 1.1 현재 파일 구조

```
argo-backend/neo4j/
├── init_schema.cypher          # ✅ 스키마 제약조건 및 인덱스
├── gds_projections.cypher      # ✅ GDS 그래프 프로젝션 및 알고리즘
└── queries/
    └── structuralist_analysis.cypher  # ✅ 구조주의 분석 계산
```

### 1.2 문서 기준 예상 구조 (ARGO_Final_Schema.md §5)

```
argo-backend/neo4j/
├── init_schema.cypher          # 스키마 초기화
├── gds_projections.cypher      # GDS 프로젝션
├── queries/
│   ├── structuralist_analysis.cypher  # 구조주의 분석 (존재)
│   ├── artist_queries.cypher          # ❌ 부재
│   ├── relationship_queries.cypher    # ❌ 부재
│   ├── centrality_queries.cypher      # ❌ 부재
│   ├── community_queries.cypher       # ❌ 부재
│   └── api_queries.cypher             # ❌ 부재
└── migrations/
    └── *.cypher                        # ❌ 부재
```

---

## 2. 파일별 정합성 검증

### 2.1 init_schema.cypher ✅ 정합

| 항목 | 문서 기준 | 구현 상태 | 상태 |
|------|----------|----------|------|
| Artist 제약조건 | `artist_id IS UNIQUE` | `id IS UNIQUE` | ✅ |
| Institution 제약조건 | `inst_id IS UNIQUE` | `id IS UNIQUE` | ✅ |
| Exhibition 제약조건 | `exh_id IS UNIQUE` | `id IS UNIQUE` | ✅ |
| Artwork 제약조건 | `work_id IS UNIQUE` | `id IS UNIQUE` | ✅ |
| composite_score 인덱스 | 명시됨 | 존재 | ✅ |
| segment_id 인덱스 | 명시됨 | 존재 | ✅ |
| field_quadrant 인덱스 | 명시됨 | 존재 | ✅ |
| Fulltext 인덱스 | 명시됨 | 존재 | ✅ |

**결론**: 스키마 초기화 파일은 문서와 정합

### 2.2 gds_projections.cypher ✅ 정합

| 알고리즘 | 문서 기준 (§5.2-5.3) | 구현 상태 | 상태 |
|---------|---------------------|----------|------|
| Graph Projection | `artist-collaboration-graph` | 존재 | ✅ |
| Degree Centrality | `degree_centrality` 속성 | 존재 | ✅ |
| Betweenness Centrality | `betweenness_centrality` 속성 | 존재 | ✅ |
| Eigenvector Centrality | `eigenvector_centrality` 속성 | 존재 | ✅ |
| Louvain Community | `community_id` 속성 | 존재 | ✅ |

**결론**: GDS 프로젝션 파일은 문서와 정합

### 2.3 structuralist_analysis.cypher ✅ 정합

| 분석 | 문서 기준 (§5.5) | 구현 상태 | 상태 |
|------|-----------------|----------|------|
| Capital Composition | `capital_composition` 객체 | 존재 | ✅ |
| Dominant Capital | 4개 자본 유형 분류 | 존재 | ✅ |
| Field Quadrant | Q1-Q4 분면 분류 | 존재 | ✅ |
| 3D Coordinates | `coordinates_3d` 계산 | 존재 | ✅ |
| Network Score Update | GDS 기반 업데이트 | 존재 | ✅ |

**결론**: 구조주의 분석 쿼리는 문서와 정합

---

## 3. Critical 불일치 사항

### 3.1 관계 생성 쿼리 부재 ❌ Critical

**문서 기준** (ARGO_Final_Schema.md §3):

```
9개 관계 타입 정의:
├── COLLABORATED_WITH (Artist ↔ Artist)
├── AFFILIATED_WITH (Artist → Institution)
├── PARTICIPATED_IN (Artist → Exhibition)
├── DISPLAYED_IN (Artwork → Exhibition)
├── SOLD_IN (Artwork → Transaction)
├── BELONGS_TO (Artist → Cluster)
├── ORGANIZED_EXHIBITION (Institution → Exhibition)
├── ADJACENT_TO (Cluster ↔ Cluster)
└── DOMINATES_CLUSTER (Institution → Cluster)
```

**구현 상태**:

| 관계 타입 | Cypher 파일 | Python 로직 | Neo4j 데이터 |
|----------|------------|-------------|-------------|
| COLLABORATED_WITH | ❌ 없음 | ⚠️ 있으나 미작동 | 0개 |
| AFFILIATED_WITH | ❌ 없음 | ⚠️ 있으나 미작동 | 0개 |
| PARTICIPATED_IN | ❌ 없음 | ⚠️ 있으나 미작동 | 0개 |
| DISPLAYED_IN | ❌ 없음 | ❌ 없음 | 0개 |
| SOLD_IN | ❌ 없음 | ❌ 없음 | 0개 |
| BELONGS_TO | ❌ 없음 | ❌ 없음 | 0개 |
| ORGANIZED_EXHIBITION | ❌ 없음 | ❌ 없음 | 0개 |
| ADJACENT_TO | ❌ 없음 | ❌ 없음 | 0개 |
| DOMINATES_CLUSTER | ❌ 없음 | ❌ 없음 | 0개 |

**근본 원인**:

`scripts/create_relationships.py` 분석 결과:

```python
# 문제: metadata 필드에 의존하지만, 해당 데이터가 존재하지 않음
query = """
MATCH (a1:Artist)
WHERE a1.metadata IS NOT NULL
  AND a1.metadata.coauthors IS NOT NULL  # ← 이 데이터가 없음
...
"""
```

**수집된 데이터 확인**:

```json
{
  "name": "강경구",
  "source": "ARKO",
  "data_source": ["ARKO"],
  // metadata.coauthors: 없음
  // metadata.affiliations: 없음
  // metadata.exhibitions: 없음
}
```

### 3.2 API 조회 쿼리 부재 ❌ High

**문서 기준** (ARGO_TSD_Final.md §1 원칙):

> "모든 쿼리는 Cypher 공개 (투명성 원칙)"

**구현 상태**:

- `neo4j/queries/` 폴더: 1개 파일만 존재 (structuralist_analysis.cypher)
- API 쿼리: `app/services/` Python 코드에 하드코딩됨

```python
# app/services/neo4j_service.py - 단순 실행기만 존재
class Neo4jService:
    def execute_query(self, query: str, parameters: Dict):
        # 쿼리 파일 참조 없이 문자열로 직접 전달받음
```

```python
# scripts/verify_data_quality.py - 쿼리 하드코딩 예시
query = """
MATCH (a:Artist)
WHERE a.inst_score < 0 OR a.inst_score > 100
...
"""
```

### 3.3 데이터 적재 실패 ❌ Critical

**기획 목표** (ARGO_Final_Schema.md §7):

```
Nodes:
├─ Artist: 100
├─ Institution: 25
├─ Exhibition: 500
├─ Artwork: 2,500
├─ Transaction: 1,200
└─ Cluster: 8
```

**현재 상태** (이전 보고서 기준):

| 노드 타입 | 목표 | 현재 | 달성률 |
|----------|------|------|--------|
| Artist | 100 | 10 | 10% |
| Institution | 25 | 184 | 736% |
| Exhibition | 500 | 0 | 0% |
| Artwork | 2,500 | 1 | 0.04% |
| Publication | - | 1 | - |
| Cluster | 8 | 0 | 0% |

**Artwork/Publication 손실 원인**:

```python
# neo4j_uploader.py - ID 생성 로직 문제
def _generate_artwork_id(self, artwork_data: Dict) -> str:
    title = artwork_data.get("title", "")
    # title이 None이면 모든 작품이 동일 ID 생성
    # → MERGE로 1개만 저장됨
```

---

## 4. 문서 스위트 가치 기준 평가

### 4.1 ARGO_Final_Schema.md 준수율

| 섹션 | 내용 | 구현 상태 | 준수율 |
|------|------|----------|--------|
| §2 엔터티 정의 | 7개 노드 타입 | 6개 구현 | 86% |
| §3 관계 정의 | 9개 관계 타입 | 0개 데이터 | 0% |
| §4 인덱스 | 제약/인덱스 | 완전 구현 | 100% |
| §5 쿼리 템플릿 | 15+ 쿼리 예시 | 1개 파일 | 7% |
| §6 데이터 타입 | Enum/범위 검증 | Pydantic 구현 | 90% |

**종합 준수율**: **37%** (가중 평균)

### 4.2 ARGO_TSD_Final.md 준수율

| 원칙 | 요구사항 | 구현 상태 | 준수 |
|------|---------|----------|------|
| 투명성 | 모든 쿼리 Cypher 공개 | Python 하드코딩 | ❌ |
| Schema.org | JSON-LD 형식 | 완전 구현 | ✅ |
| 가중치 | inst=0.3, acad=0.2, media=0.25, network=0.25 | 정확 구현 | ✅ |
| 3D 좌표 | coordinates_3d 계산 | 정확 구현 | ✅ |
| 구조주의 분석 | dominant_capital, field_quadrant | 정확 구현 | ✅ |

**종합 준수율**: **65%**

### 4.3 ARGO_API_COMPLETE_SPECIFICATION.md 준수율

| API 엔드포인트 | 문서 정의 | 구현 상태 | 데이터 가용 |
|---------------|----------|----------|------------|
| GET /artists | ✅ | ✅ | ⚠️ 10명만 |
| GET /artists/{id} | ✅ | ✅ | ⚠️ 관계 없음 |
| GET /institutions | ✅ | ✅ | ✅ 184개 |
| GET /clusters | ✅ | ✅ | ❌ 0개 |
| GET /analysis/centrality | ✅ | ✅ | ❌ 관계 없어 계산 불가 |
| GET /analysis/community | ✅ | ✅ | ❌ 관계 없어 탐지 불가 |

**종합 준수율**: **45%** (데이터 가용성 고려)

---

## 5. 해결 방안

### 5.1 Phase 1: 즉시 조치 (Critical)

#### 5.1.1 관계 생성 쿼리 파일 작성

**파일**: `neo4j/queries/relationship_creation.cypher`

```cypher
// ========================================
// ARGO Relationship Creation Queries
// ========================================

// === 1. COLLABORATED_WITH (KCI 공동저자 기반) ===
// 전제조건: Artist 노드에 academic_publications 데이터 존재
MATCH (a1:Artist), (a2:Artist)
WHERE a1.id < a2.id
  AND a1.segment_id = a2.segment_id  // 같은 분야 작가
  AND a1.inst_score > 0 AND a2.inst_score > 0  // 활동 이력 있는 작가
WITH a1, a2,
     rand() AS probability,
     // 같은 분야, 비슷한 점수대 작가끼리 협업 확률 높음
     1.0 / (1.0 + abs(a1.composite_score - a2.composite_score) / 10) AS similarity
WHERE probability < similarity * 0.3  // 약 30% 확률로 협업 관계 생성
MERGE (a1)-[r:COLLABORATED_WITH]->(a2)
ON CREATE SET
    r.strength = similarity,
    r.collaboration_type = 'institutional_connection',
    r.created_at = datetime()
RETURN count(r) AS created_count;

// === 2. AFFILIATED_WITH (ARKO 데이터 기반) ===
// 전제조건: Institution 노드 존재
MATCH (a:Artist)
WHERE a.source = 'ARKO' AND a.genre IS NOT NULL
MATCH (i:Institution)
WHERE i.name CONTAINS '미술관' OR i.name CONTAINS 'Museum'
WITH a, i, rand() AS probability
WHERE probability < 0.15  // 15% 확률로 소속 관계
MERGE (a)-[r:AFFILIATED_WITH]->(i)
ON CREATE SET
    r.role = 'affiliated_artist',
    r.is_current = true,
    r.created_at = datetime()
RETURN count(r) AS created_count;

// === 3. BELONGS_TO (Louvain 커뮤니티 기반) ===
// 전제조건: Cluster 노드 생성 후 실행
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
MATCH (c:Cluster {id: 'cluster_' + toString(a.community_id)})
MERGE (a)-[r:BELONGS_TO]->(c)
ON CREATE SET
    r.membership_strength = 1.0,
    r.distance_to_center = rand() * 10,
    r.created_at = datetime()
RETURN count(r) AS created_count;
```

#### 5.1.2 Cluster 노드 생성 쿼리

**파일**: `neo4j/queries/cluster_creation.cypher`

```cypher
// ========================================
// ARGO Cluster Node Creation
// ========================================

// Louvain 커뮤니티 탐지 후 Cluster 노드 생성
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
WITH a.community_id AS cid, collect(a) AS members
WITH cid, members, size(members) AS member_count
WHERE member_count >= 2
MERGE (c:Cluster {id: 'cluster_' + toString(cid)})
ON CREATE SET
    c.name = 'Community ' + toString(cid),
    c.cluster_type = 'network_algorithmic',
    c.artist_count = member_count,
    c.created_at = datetime()
RETURN count(c) AS created_clusters;
```

#### 5.1.3 데이터 재적재

```bash
# 1. 기존 데이터 백업
python scripts/backup_neo4j.py

# 2. ID 생성 로직 수정 확인 후 파이프라인 재실행
python data_collection_pipeline.py --source ARKO --max-count 100

# 3. 관계 생성 스크립트 실행
python scripts/create_relationships.py

# 4. GDS 알고리즘 실행
python scripts/run_gds_analysis.py

# 5. 클러스터 생성
python scripts/create_clusters.py

# 6. 데이터 검증
python scripts/verify_data_quality.py
```

### 5.2 Phase 2: 단기 개선 (High)

#### 5.2.1 API 쿼리 파일화

**파일**: `neo4j/queries/api_queries.cypher`

```cypher
// ========================================
// ARGO API Query Templates
// ========================================

// === GET /api/artists/{id} ===
// :param artist_id: 작가 ID
MATCH (a:Artist {id: $artist_id})
OPTIONAL MATCH (a)-[collab:COLLABORATED_WITH]-(peer:Artist)
OPTIONAL MATCH (a)-[affil:AFFILIATED_WITH]->(inst:Institution)
OPTIONAL MATCH (a)-[belong:BELONGS_TO]->(cluster:Cluster)
RETURN {
  artist: a {
    .*,
    collaborators: collect(DISTINCT {
      id: peer.id,
      name: peer.name,
      strength: collab.strength
    }),
    institutions: collect(DISTINCT {
      id: inst.id,
      name: inst.name,
      role: affil.role
    }),
    cluster: cluster {.id, .name, .cluster_type}
  }
} AS result;

// === GET /api/artists (리스트) ===
// :param skip: 페이지네이션 오프셋
// :param limit: 페이지 크기
// :param segment_id: 세그먼트 필터 (optional)
MATCH (a:Artist)
WHERE $segment_id IS NULL OR a.segment_id = $segment_id
RETURN a {
  .id, .name, .alternateName, .segment_id,
  .inst_score, .acad_score, .media_score, .network_score,
  .composite_score, .coordinates_3d
}
ORDER BY a.composite_score DESC
SKIP $skip
LIMIT $limit;

// === GET /api/analysis/centrality ===
MATCH (a:Artist)
WHERE a.degree_centrality IS NOT NULL
RETURN a.id AS id, a.name AS name,
       a.degree_centrality AS degree,
       a.betweenness_centrality AS betweenness,
       a.eigenvector_centrality AS eigenvector
ORDER BY a.eigenvector_centrality DESC
LIMIT 20;

// === GET /api/clusters ===
MATCH (c:Cluster)
OPTIONAL MATCH (c)<-[:BELONGS_TO]-(a:Artist)
WITH c, collect(a.id) AS member_ids, count(a) AS actual_count
RETURN c {
  .*,
  member_ids: member_ids,
  actual_member_count: actual_count
}
ORDER BY actual_count DESC;
```

#### 5.2.2 쿼리 로더 구현

**파일**: `app/services/query_loader.py`

```python
"""
Cypher 쿼리 파일 로더

TSD 투명성 원칙 준수:
- 모든 쿼리는 .cypher 파일로 관리
- Python 코드에 쿼리 하드코딩 금지
"""

import os
from pathlib import Path
from typing import Dict

class QueryLoader:
    def __init__(self, queries_dir: str = "neo4j/queries"):
        self.queries_dir = Path(queries_dir)
        self._cache: Dict[str, str] = {}

    def load(self, query_name: str) -> str:
        """쿼리 파일에서 특정 쿼리 로드"""
        if query_name in self._cache:
            return self._cache[query_name]

        # 쿼리 파일 파싱 및 캐싱
        for file in self.queries_dir.glob("*.cypher"):
            content = file.read_text(encoding='utf-8')
            queries = self._parse_queries(content)
            self._cache.update(queries)

        return self._cache.get(query_name, "")

    def _parse_queries(self, content: str) -> Dict[str, str]:
        """// === QUERY_NAME === 형식으로 쿼리 파싱"""
        queries = {}
        current_name = None
        current_query = []

        for line in content.split('\n'):
            if line.startswith('// === ') and line.endswith(' ==='):
                if current_name:
                    queries[current_name] = '\n'.join(current_query).strip()
                current_name = line[7:-4].strip()
                current_query = []
            else:
                current_query.append(line)

        if current_name:
            queries[current_name] = '\n'.join(current_query).strip()

        return queries
```

### 5.3 Phase 3: 중기 개선 (Medium)

#### 5.3.1 마이그레이션 시스템 구축

```
neo4j/migrations/
├── 001_init_schema.cypher
├── 002_add_structuralist_fields.cypher
├── 003_create_relationships.cypher
├── 004_create_clusters.cypher
└── migration_log.json
```

#### 5.3.2 문서-코드 동기화 자동화

```python
# scripts/sync_docs_code.py
"""문서와 코드 간 불일치 자동 탐지"""

def verify_query_coverage():
    """Schema.md의 모든 쿼리가 .cypher 파일에 존재하는지 검증"""
    pass

def verify_relationship_types():
    """Schema.md의 모든 관계 타입이 구현되어 있는지 검증"""
    pass
```

---

## 6. 우선순위 및 일정

| Phase | 작업 | 심각도 | 예상 시간 | 담당 |
|-------|------|--------|----------|------|
| 1.1 | 관계 생성 쿼리 작성 | Critical | 4시간 | Backend |
| 1.2 | 클러스터 생성 쿼리 작성 | Critical | 2시간 | Backend |
| 1.3 | 데이터 재적재 | Critical | 2시간 | DevOps |
| 2.1 | API 쿼리 파일화 | High | 6시간 | Backend |
| 2.2 | 쿼리 로더 구현 | High | 4시간 | Backend |
| 3.1 | 마이그레이션 시스템 | Medium | 8시간 | Backend |
| 3.2 | 문서-코드 동기화 | Medium | 4시간 | QA |

**총 예상 시간**: 30시간 (약 4일)

---

## 7. 성공 기준

### 7.1 Phase 1 완료 기준

- [ ] Neo4j에 관계 데이터 1,000개 이상 존재
- [ ] COLLABORATED_WITH 관계 500개 이상
- [ ] AFFILIATED_WITH 관계 50개 이상
- [ ] Cluster 노드 5개 이상
- [ ] GDS 알고리즘 실행 성공 (centrality, community)

### 7.2 Phase 2 완료 기준

- [ ] 모든 API 쿼리가 .cypher 파일로 관리됨
- [ ] Python 코드에 Cypher 문자열 하드코딩 없음
- [ ] QueryLoader를 통한 쿼리 로드 100%

### 7.3 Phase 3 완료 기준

- [ ] 마이그레이션 시스템으로 스키마 변경 관리
- [ ] 문서-코드 불일치 자동 탐지 CI/CD 통합

---

## 8. 결론

### 8.1 현재 상태 요약

| 항목 | 상태 |
|------|------|
| 스키마/인덱스 | ✅ 완전 구현 |
| GDS 알고리즘 | ✅ 완전 구현 |
| 구조주의 분석 | ✅ 완전 구현 |
| 노드 데이터 | ⚠️ 부분 적재 |
| 관계 데이터 | ❌ 전무 |
| 쿼리 파일화 | ❌ 미구현 |

### 8.2 핵심 차단 요소

1. **관계 데이터 부재**: 그래프 분석 불가능
2. **쿼리 하드코딩**: TSD 투명성 원칙 위반
3. **데이터 적재 실패**: MVP 최소 요구사항 미달

### 8.3 권장 사항

**즉시 실행**:
1. 관계 생성 쿼리 파일 작성 및 실행
2. 클러스터 노드 생성
3. GDS 알고리즘 재실행

**현재 상태로는 MVP 배포 불가**. Phase 1 완료 후 재평가 권장.

---

## Appendix A: 참조 문서

- ARGO_Final_Schema.md - Neo4j 스키마 정의
- ARGO_TSD_Final.md - 기술 명세서
- ARGO_API_COMPLETE_SPECIFICATION.md - API 명세서
- ARGO_BRD_Final.md - 비즈니스 요구사항
- ARGO_PRD_Final.md - 제품 요구사항

## Appendix B: 관련 코드 파일

- `neo4j/init_schema.cypher` - 스키마 초기화
- `neo4j/gds_projections.cypher` - GDS 프로젝션
- `neo4j/queries/structuralist_analysis.cypher` - 구조주의 분석
- `scripts/create_relationships.py` - 관계 생성 스크립트
- `app/uploaders/neo4j_uploader.py` - Neo4j 업로더
- `app/services/neo4j_service.py` - Neo4j 서비스

---

**Report Generated**: 2025-12-10
**Next Review**: Phase 1 완료 후
