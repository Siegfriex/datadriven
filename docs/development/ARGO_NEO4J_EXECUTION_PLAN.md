# ARGO Neo4j 데이터 정합성 회복 및 고도화 실행 계획

**Version**: 1.0 Final
**Date**: 2025-12-10
**Status**: Approved for Execution
**Theoretical Basis**: Bourdieu Field Theory + Meta-Analysis

---

## Executive Summary

### 목표
1. **데이터 정합성 100%**: Schema.md 기준 노드/관계 완전 일치
2. **실데이터 기반 관계**: Publication/Biennale 데이터에서 관계 추출
3. **분석 역량 완성**: GDS 중심성/커뮤니티 → API 엔드포인트 연결

### 문서 스위트 참조
| 문서 | 참조 섹션 | 적용 Phase |
|------|----------|------------|
| ARGO_Final_Schema.md | §2 엔터티, §3 관계, §5 쿼리 | All |
| ARGO_TSD_Final.md | §2.1 Artist 구조주의 분석 | Phase 4 |
| ARGO_API_COMPLETE_SPECIFICATION.md | Part I §2.2 엔드포인트 | Phase 2-4 |

### 이론적 기반 (Bourdieu Field Theory)
```
4-Capital Model:
├── inst_score (제도 자본): 미술관 전시, 비엔날레, 공공 지원 → 가중치 0.30
├── acad_score (학술 자본): 논문 인용, 학술 출판물 → 가중치 0.20
├── media_score (담론 자본): 미디어 언급, 감성 점수 → 가중치 0.25
└── network_score (네트워크 자본): GDS 중심성 기반 → 가중치 0.25

Field Quadrant Classification:
├── Q1_established: 고-제도 + 고-학술 (원로/거장)
├── Q2_academic_elite: 저-제도 + 고-학술 (학계 중심)
├── Q3_media_star: 고-미디어 + 저-학술 (미디어 스타)
└── Q4_emerging: 저-제도 + 저-학술 (신진 작가)
```

---

## Phase 0: 준비 및 안전장치

### 0.1 백업 스크립트 작성

**파일**: `neo4j/queries/00_backup_snapshot.cypher`

```cypher
// ========================================
// ARGO Backup Snapshot
// Purpose: 현재 상태 백업 (실행 전 필수)
// ========================================

// 1. 노드 카운트 스냅샷
MATCH (n)
WITH labels(n) AS label, count(n) AS cnt
RETURN "NODE_COUNT" AS type, label[0] AS entity, cnt AS count
UNION ALL
// 2. 관계 카운트 스냅샷
MATCH ()-[r]->()
WITH type(r) AS rel_type, count(r) AS cnt
RETURN "REL_COUNT" AS type, rel_type AS entity, cnt AS count;

// 결과를 파일로 저장 (Python 스크립트에서 실행)
```

**파일**: `neo4j/queries/00_cleanup.cypher`

```cypher
// ========================================
// ARGO Full Cleanup (위험: 모든 데이터 삭제)
// Purpose: 비상 시 전체 초기화
// WARNING: 프로덕션에서는 실행 금지
// ========================================

// 관계 먼저 삭제
MATCH ()-[r]->() DELETE r;

// 노드 삭제 (타입별)
MATCH (n:Cluster) DELETE n;
MATCH (n:Exhibition) DELETE n;
MATCH (n:Artwork) DELETE n;
MATCH (n:Publication) DELETE n;
// Artist, Institution은 유지 (선택적)
```

### 0.2 데이터 소스-관계 매핑 테이블

| 데이터 소스 | 추출 관계 | Neo4j 관계 타입 | 필드 매핑 | API 지원 |
|------------|----------|-----------------|----------|----------|
| KCI Publication | 공동저자 | `COLLABORATED_WITH` | `authors[]` | GET /artists/{id}/network |
| Cheongju Biennale | 비엔날레 참여 | `PARTICIPATED_IN` | `artist_name` | GET /artists/{id}/exhibitions |
| MMCA Collection | 소장품 전시 | `DISPLAYED_IN` | `artist_name` | GET /exhibitions/{id} |
| ARKO Institution | 소속 추론 | `AFFILIATED_WITH` | `segment_id` 매칭 | GET /institutions/{id}/affiliated-artists |
| Louvain Result | 커뮤니티 | `BELONGS_TO` | `community_id` | GET /clusters/{id} |

### 0.3 실행 환경 확인

```bash
# 1. Neo4j 연결 확인
python scripts/test_neo4j_connection.py

# 2. 환경 변수 확인
python scripts/verify_env.py

# 3. 현재 데이터 상태 확인
python scripts/check_neo4j_data.py
```

---

## Phase 1: 노드 데이터 재적재

### 1.1 목표 데이터 규모 (Schema.md §7 기준)

| 노드 타입 | 목표 | 최소 요건 | 데이터 소스 |
|----------|------|----------|------------|
| Artist | 100명 | 100명 | ARKO 작가 목록 |
| Institution | 50개 | 25개 | ARKO 예술단체 (기존 184개 유지) |
| Exhibition | 100개 | 50개 | Cheongju Biennale (신규) |
| Artwork | 500개 | 200개 | MMCA Collection |
| Publication | 200개 | 100개 | KCI 논문 |
| Cluster | 8개 | 5개 | Louvain 결과 (Phase 3 후) |

### 1.2 Exhibition 노드 생성 로직 추가

**문제**: 현재 Exhibition 노드 0개 → PARTICIPATED_IN 관계 생성 불가

**해결**: Biennale 데이터에서 Exhibition 노드 추출

```python
# neo4j_uploader.py에 추가할 메서드 (개념)
def upload_exhibition_from_biennale(biennale_data: Dict) -> bool:
    """
    Biennale 데이터에서 Exhibition 노드 생성

    매핑:
    - biennale_data["edition"] → Exhibition.title
    - biennale_data["year"] → Exhibition.year
    - "biennale" → Exhibition.type
    """
    exh_id = f"exh_cheongju_{biennale_data.get('year', 'unknown')}"
    # ... 업로드 로직
```

### 1.3 데이터 파이프라인 실행 명령어

```bash
# Step 1: Artist 100명 수집 (ARKO)
python data_collection_pipeline.py --source ARKO --max-count 100

# Step 2: Publication 200개 수집 (KCI)
python data_collection_pipeline.py --source KCI --max-count 200

# Step 3: Artwork 500개 수집 (MMCA Collection)
python data_collection_pipeline.py --source MMCA_COLLECTION --max-count 500

# Step 4: Exhibition 생성 (Biennale)
python data_collection_pipeline.py --source CHEONGJU_BIENNALE --max-count 100

# Step 5: 노드 업로드
python data_collection_pipeline.py --upload-only
```

### 1.4 [검증 게이트 1] 노드 카운트 확인

**파일**: `neo4j/queries/validation_phase1.cypher`

```cypher
// ========================================
// Phase 1 Validation: 노드 카운트 검증
// Pass Criteria: 모든 노드 타입이 최소 요건 충족
// ========================================

MATCH (a:Artist) WITH count(a) AS artist_count
MATCH (i:Institution) WITH artist_count, count(i) AS inst_count
MATCH (e:Exhibition) WITH artist_count, inst_count, count(e) AS exh_count
MATCH (w:Artwork) WITH artist_count, inst_count, exh_count, count(w) AS artwork_count
MATCH (p:Publication) WITH artist_count, inst_count, exh_count, artwork_count, count(p) AS pub_count
RETURN
    artist_count >= 100 AS artist_pass,
    inst_count >= 25 AS inst_pass,
    exh_count >= 50 AS exh_pass,
    artwork_count >= 200 AS artwork_pass,
    pub_count >= 100 AS pub_pass,
    artist_count + inst_count + exh_count + artwork_count + pub_count >= 475 AS total_pass;
```

**성공 기준**: 모든 `*_pass` = true

---

## Phase 2: 실데이터 기반 관계 생성

### 2.1 관계 생성 쿼리 (API 엔드포인트 매핑)

**파일**: `neo4j/queries/01_relationship_creation.cypher`

```cypher
// ========================================
// ARGO Relationship Creation
// Theoretical Basis: Bourdieu Field Theory - Social Capital
// API Reference: GET /artists/{id}/network
// ========================================

// === 1. COLLABORATED_WITH (Publication 공동저자 기반) ===
// Purpose: network_score 계산의 기반, Social Capital 측정
// API: GET /v1/api/artists/{artist_id}/network

MATCH (p:Publication)
WHERE p.authors IS NOT NULL AND size(p.authors) > 1
WITH p, p.authors AS authors
UNWIND range(0, size(authors)-2) AS i
UNWIND range(i+1, size(authors)-1) AS j
WITH p, authors[i] AS author1, authors[j] AS author2
WHERE author1 <> author2

// Artist 노드와 매칭 (이름 기반)
MATCH (a1:Artist)
WHERE a1.name = author1
   OR a1.name CONTAINS author1
   OR a1.alternateName CONTAINS author1
MATCH (a2:Artist)
WHERE a2.name = author2
   OR a2.name CONTAINS author2
   OR a2.alternateName CONTAINS author2
WHERE a1.id <> a2.id

// 관계 생성 (중복 방지)
MERGE (a1)-[r:COLLABORATED_WITH]->(a2)
ON CREATE SET
    r.strength = 0.5,
    r.collaboration_type = 'co_authorship',
    r.publication_id = p.id,
    r.first_collaboration_year = p.publication_year,
    r.created_at = datetime()
ON MATCH SET
    r.strength = CASE WHEN r.strength < 1.0 THEN r.strength + 0.1 ELSE 1.0 END,
    r.updated_at = datetime()
RETURN count(r) AS collaborated_count;


// === 2. AFFILIATED_WITH (Segment 기반 추론) ===
// Purpose: inst_score 보완, Institutional Capital 연결
// API: GET /v1/api/institutions/{inst_id}/affiliated-artists

MATCH (a:Artist)
WHERE a.segment_id IS NOT NULL
MATCH (i:Institution)
WHERE i.type IN ['national_museum', 'biennale', 'university']
WITH a, i,
     CASE
       WHEN a.segment_id CONTAINS 'painting' AND i.name CONTAINS '미술' THEN 0.7
       WHEN a.segment_id CONTAINS 'sculpture' AND i.name CONTAINS '조각' THEN 0.7
       WHEN a.segment_id CONTAINS 'craft' AND i.name CONTAINS '공예' THEN 0.8
       WHEN i.type = 'national_museum' THEN 0.5
       ELSE 0.3
     END AS affinity_score
WHERE affinity_score >= 0.5 AND rand() < affinity_score * 0.3

MERGE (a)-[r:AFFILIATED_WITH]->(i)
ON CREATE SET
    r.role = 'exhibited_at',
    r.is_current = false,
    r.inferred = true,
    r.affinity_score = affinity_score,
    r.created_at = datetime()
RETURN count(r) AS affiliated_count;


// === 3. PARTICIPATED_IN (Biennale 참여) ===
// Purpose: inst_score 기여, Institutional Capital 축적
// API: GET /v1/api/artists/{artist_id}/exhibitions

MATCH (a:Artist)
MATCH (e:Exhibition)
WHERE e.type = 'biennale'
  AND (a.name = e.artist_name
       OR a.alternateName = e.artist_name
       OR e.participants CONTAINS a.name)
MERGE (a)-[r:PARTICIPATED_IN]->(e)
ON CREATE SET
    r.role = 'participant',
    r.year = e.year,
    r.featured = false,
    r.created_at = datetime()
RETURN count(r) AS participated_count;


// === 4. DISPLAYED_IN (Artwork-Exhibition) ===
// Purpose: 작품 전시 이력, market_score 기반
// API: GET /v1/api/exhibitions/{exh_id}

MATCH (w:Artwork)
WHERE w.artist_name IS NOT NULL
MATCH (e:Exhibition)
WHERE e.year = w.install_year
   OR (e.start_date IS NOT NULL AND substring(e.start_date, 0, 4) = toString(w.install_year))
MERGE (w)-[r:DISPLAYED_IN]->(e)
ON CREATE SET
    r.display_status = 'exhibited',
    r.created_at = datetime()
RETURN count(r) AS displayed_count;
```

### 2.2 관계 생성 스크립트 리팩토링

**파일**: `scripts/create_relationships_v2.py`

```python
"""
관계 생성 스크립트 v2
- Cypher 파일 기반 실행
- 검증 게이트 통합
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_cypher_file(filename: str) -> str:
    """Cypher 파일 로드"""
    path = Path(__file__).parent.parent / "neo4j" / "queries" / filename
    return path.read_text(encoding='utf-8')


def execute_relationship_creation():
    """관계 생성 쿼리 실행"""
    logger.info("=" * 60)
    logger.info("Phase 2: 관계 생성 시작")
    logger.info("=" * 60)

    # Cypher 파일 로드 및 쿼리별 분리 실행
    cypher_content = load_cypher_file("01_relationship_creation.cypher")

    # 쿼리 블록 분리 (// === 로 구분)
    queries = parse_cypher_blocks(cypher_content)

    results = {}
    for name, query in queries.items():
        try:
            result = neo4j_service.execute_query(query)
            count = result[0].get(list(result[0].keys())[0], 0) if result else 0
            results[name] = count
            logger.info(f"✅ {name}: {count}개 생성")
        except Exception as e:
            logger.error(f"❌ {name} 실패: {e}")
            results[name] = -1

    return results


def parse_cypher_blocks(content: str) -> dict:
    """Cypher 파일에서 쿼리 블록 파싱"""
    blocks = {}
    current_name = None
    current_query = []

    for line in content.split('\n'):
        if line.startswith('// === ') and '===' in line[7:]:
            if current_name and current_query:
                blocks[current_name] = '\n'.join(current_query)
            current_name = line.split('===')[1].strip().split('(')[0].strip()
            current_query = []
        elif not line.startswith('//') and line.strip():
            current_query.append(line)

    if current_name and current_query:
        blocks[current_name] = '\n'.join(current_query)

    return blocks


if __name__ == "__main__":
    execute_relationship_creation()
```

### 2.3 [검증 게이트 2] 관계 무결성 확인

**파일**: `neo4j/queries/validation_phase2.cypher`

```cypher
// ========================================
// Phase 2 Validation: 관계 무결성 검증
// Pass Criteria: 관계 존재 + 고아 관계 없음
// ========================================

// 1. 관계 타입별 카운트
MATCH ()-[r:COLLABORATED_WITH]->() WITH count(r) AS collab_count
MATCH ()-[r:AFFILIATED_WITH]->() WITH collab_count, count(r) AS affil_count
MATCH ()-[r:PARTICIPATED_IN]->() WITH collab_count, affil_count, count(r) AS partic_count
MATCH ()-[r:DISPLAYED_IN]->() WITH collab_count, affil_count, partic_count, count(r) AS display_count
RETURN
    collab_count >= 10 AS collab_pass,
    affil_count >= 20 AS affil_pass,
    partic_count >= 5 AS partic_pass,
    display_count >= 10 AS display_pass,
    collab_count + affil_count + partic_count + display_count AS total_relations;

// 2. 고아 관계 검증 (존재하면 실패)
MATCH (a:Artist)-[r:COLLABORATED_WITH]->(b:Artist)
WHERE NOT exists((a)) OR NOT exists((b))
RETURN count(r) AS orphan_count;

// 3. Artist당 평균 관계 수
MATCH (a:Artist)
OPTIONAL MATCH (a)-[r]-()
WITH a, count(r) AS rel_count
RETURN avg(rel_count) >= 2.0 AS avg_relations_pass;
```

**성공 기준**:
- 모든 `*_pass` = true
- `orphan_count` = 0
- `avg_relations_pass` = true

---

## Phase 3: GDS 분석 및 클러스터링

### 3.1 GDS 실행 순서

```
3.1.1 Graph Projection 생성
    ↓
3.1.2 Centrality 계산 (Degree → Betweenness → Eigenvector)
    ↓
3.1.3 network_score Write-back
    ↓
3.1.4 Louvain Community Detection
    ↓
3.1.5 Cluster 노드 생성
    ↓
3.1.6 BELONGS_TO 관계 생성
```

### 3.2 GDS 실행 쿼리

**파일**: `neo4j/queries/03_gds_execution.cypher`

```cypher
// ========================================
// ARGO GDS Analysis Execution
// Theoretical Basis: Bourdieu Field Theory - Network Capital
// API Reference:
//   - POST /v1/api/analysis/run-gds-centrality
//   - POST /v1/api/analysis/run-louvain
// ========================================

// === 3.1 Graph Projection ===
// 기존 프로젝션 삭제 (있으면)
CALL gds.graph.drop('artist-collaboration-graph', false) YIELD graphName;

// 새 프로젝션 생성
CALL gds.graph.project(
    'artist-collaboration-graph',
    'Artist',
    {
        COLLABORATED_WITH: {
            type: 'COLLABORATED_WITH',
            orientation: 'UNDIRECTED',
            properties: ['strength']
        }
    },
    {
        nodeProperties: ['composite_score', 'inst_score', 'acad_score']
    }
) YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;


// === 3.2 Degree Centrality (Write-back) ===
// TSD Reference: network_score_metadata.degree_centrality
CALL gds.degree.write(
    'artist-collaboration-graph',
    {
        writeProperty: 'degree_centrality',
        relationshipWeightProperty: 'strength'
    }
) YIELD nodePropertiesWritten
RETURN nodePropertiesWritten AS degree_written;


// === 3.3 Betweenness Centrality (Write-back) ===
// TSD Reference: network_score_metadata.betweenness_centrality
CALL gds.betweenness.write(
    'artist-collaboration-graph',
    {
        writeProperty: 'betweenness_centrality'
    }
) YIELD nodePropertiesWritten
RETURN nodePropertiesWritten AS betweenness_written;


// === 3.4 Eigenvector Centrality (Write-back) ===
// TSD Reference: network_score_metadata.eigenvector_centrality
CALL gds.eigenvector.write(
    'artist-collaboration-graph',
    {
        writeProperty: 'eigenvector_centrality',
        maxIterations: 100
    }
) YIELD nodePropertiesWritten
RETURN nodePropertiesWritten AS eigenvector_written;


// === 3.5 network_score 계산 및 업데이트 ===
// Formula: (degree*0.25 + betweenness*0.35 + eigenvector*0.40) * 100
// TSD Reference: §2.1 scores.network_score
MATCH (a:Artist)
WHERE a.degree_centrality IS NOT NULL
WITH a,
     coalesce(a.degree_centrality, 0) AS deg,
     coalesce(a.betweenness_centrality, 0) AS bet,
     coalesce(a.eigenvector_centrality, 0) AS eig
WITH a,
     (deg * 0.25 + bet * 0.35 + eig * 0.40) * 100 AS raw_score
SET a.network_score = round(CASE
    WHEN raw_score > 100 THEN 100
    WHEN raw_score < 0 THEN 0
    ELSE raw_score
END, 2)
RETURN count(a) AS network_score_updated;


// === 3.6 Louvain Community Detection ===
// API: POST /v1/api/analysis/run-louvain
CALL gds.louvain.write(
    'artist-collaboration-graph',
    {
        writeProperty: 'community_id',
        relationshipWeightProperty: 'strength'
    }
) YIELD nodePropertiesWritten, communityCount
RETURN nodePropertiesWritten, communityCount;
```

### 3.3 Cluster 노드 생성

**파일**: `neo4j/queries/02_cluster_creation.cypher`

```cypher
// ========================================
// ARGO Cluster Node Creation
// API Reference: GET /v1/api/clusters
// Prerequisite: GDS Louvain 실행 완료
// ========================================

// === Cluster 노드 생성 ===
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
WITH a.community_id AS cid, collect(a) AS members
WITH cid, members, size(members) AS member_count
WHERE member_count >= 2  // 최소 2명 이상

// 클러스터 통계 계산
WITH cid, members, member_count,
     [m IN members | m.composite_score] AS scores,
     [m IN members | m.genre] AS genres
WITH cid, members, member_count,
     reduce(sum = 0.0, s IN scores | sum + coalesce(s, 0)) / member_count AS avg_score,
     head([g IN genres WHERE g IS NOT NULL]) AS dominant_genre

MERGE (c:Cluster {id: 'cluster_' + toString(cid)})
ON CREATE SET
    c.name = 'Community ' + toString(cid),
    c.cluster_type = 'network_algorithmic',
    c.artist_count = member_count,
    c.avg_composite_score = round(avg_score, 2),
    c.dominant_genre = dominant_genre,
    c.algorithm_version = 'louvain_v1',
    c.created_at = datetime()
RETURN count(c) AS clusters_created;


// === BELONGS_TO 관계 생성 ===
// API: GET /v1/api/clusters/{cluster_id}
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
MATCH (c:Cluster {id: 'cluster_' + toString(a.community_id)})
MERGE (a)-[r:BELONGS_TO]->(c)
ON CREATE SET
    r.membership_strength = 1.0,
    r.distance_to_center = rand() * 10,  // 향후 실제 거리 계산으로 대체
    r.created_at = datetime()
RETURN count(r) AS belongs_to_created;
```

### 3.4 [검증 게이트 3] 분석 결과 확인

**파일**: `neo4j/queries/validation_phase3.cypher`

```cypher
// ========================================
// Phase 3 Validation: GDS 분석 결과 검증
// ========================================

// 1. network_score 분포 확인
MATCH (a:Artist)
WHERE a.network_score IS NOT NULL
WITH a.network_score AS score
RETURN
    count(score) AS artists_with_network_score,
    avg(score) AS avg_network_score,
    min(score) AS min_score,
    max(score) AS max_score;

// 2. community_id 분포
MATCH (a:Artist)
WHERE a.community_id IS NOT NULL
WITH a.community_id AS cid, count(*) AS member_count
RETURN count(cid) AS community_count, sum(member_count) AS total_assigned;

// 3. Cluster 노드 확인
MATCH (c:Cluster)
RETURN count(c) AS cluster_count;

// 4. BELONGS_TO 관계 확인
MATCH ()-[r:BELONGS_TO]->()
RETURN count(r) AS belongs_to_count;

// 5. 종합 Pass 판정
MATCH (a:Artist) WHERE a.network_score IS NOT NULL WITH count(a) AS net_count
MATCH (c:Cluster) WITH net_count, count(c) AS cluster_count
MATCH ()-[r:BELONGS_TO]->() WITH net_count, cluster_count, count(r) AS belongs_count
RETURN
    net_count >= 50 AS network_score_pass,
    cluster_count >= 3 AS cluster_pass,
    belongs_count >= 50 AS belongs_pass;
```

---

## Phase 4: 구조주의 분석 및 시각화 준비

### 4.1 구조주의 분석 실행

**파일**: `neo4j/queries/structuralist_analysis.cypher` (기존 파일 활용)

**API 매핑**:
- `POST /v1/api/analysis/calculate-structuralist`
- `GET /v1/api/artists/{artist_id}/capital-composition`
- `GET /v1/api/analysis/field-quadrants`

```cypher
// ========================================
// Structuralist Analysis (Bourdieu Field Theory)
// API Reference: POST /v1/api/analysis/calculate-structuralist
// ========================================

// === 4.1 composite_score 재계산 (가중 평균) ===
// Formula: inst*0.30 + acad*0.20 + media*0.25 + network*0.25
// TSD Reference: §2.1 composite_score
MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
SET a.composite_score = round(
    (coalesce(a.inst_score, 0) * 0.30) +
    (coalesce(a.acad_score, 0) * 0.20) +
    (coalesce(a.media_score, 0) * 0.25) +
    (coalesce(a.network_score, 0) * 0.25),
    2
)
RETURN count(a) AS composite_updated;


// === 4.2 Capital Composition 계산 ===
// API: GET /v1/api/artists/{artist_id}/capital-composition
MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
WITH a,
     (a.inst_score + a.acad_score + a.media_score + a.network_score) AS total
WHERE total > 0
SET a.capital_inst_ratio = round(a.inst_score / total, 4),
    a.capital_acad_ratio = round(a.acad_score / total, 4),
    a.capital_media_ratio = round(a.media_score / total, 4),
    a.capital_network_ratio = round(a.network_score / total, 4)
RETURN count(a) AS capital_composition_updated;


// === 4.3 Dominant Capital 결정 ===
// TSD Reference: structuralist_analysis.dominant_capital
MATCH (a:Artist)
WHERE a.capital_inst_ratio IS NOT NULL
WITH a,
     a.capital_inst_ratio AS inst,
     a.capital_acad_ratio AS acad,
     a.capital_media_ratio AS media,
     a.capital_network_ratio AS network
SET a.dominant_capital =
    CASE
        WHEN inst >= acad AND inst >= media AND inst >= network THEN 'institutional'
        WHEN acad >= inst AND acad >= media AND acad >= network THEN 'academic'
        WHEN media >= inst AND media >= acad AND media >= network THEN 'media'
        ELSE 'network'
    END
RETURN count(a) AS dominant_capital_updated;


// === 4.4 Field Quadrant 분류 ===
// API: GET /v1/api/analysis/field-quadrants
// Bourdieu 2D Field: X=inst_score, Y=acad_score
MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL AND a.acad_score IS NOT NULL
WITH percentileDisc(collect(a.inst_score), 0.5) AS inst_median,
     percentileDisc(collect(a.acad_score), 0.5) AS acad_median
MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
SET a.field_quadrant =
    CASE
        WHEN a.inst_score >= inst_median AND a.acad_score >= acad_median THEN 'Q1_established'
        WHEN a.inst_score < inst_median AND a.acad_score >= acad_median THEN 'Q2_academic_elite'
        WHEN a.inst_score >= inst_median AND a.acad_score < acad_median THEN 'Q3_media_star'
        ELSE 'Q4_emerging'
    END
RETURN count(a) AS field_quadrant_updated;
```

### 4.2 3D 좌표 계산

**파일**: `neo4j/queries/04_coordinates_update.cypher`

```cypher
// ========================================
// 3D Coordinates Update
// API Reference: GET /v1/api/galaxy-snapshot
// TSD Reference: §2.1 coordinates_3d
// ========================================

// 좌표 계산 공식:
// x = (inst_score - 50) * 0.6   // 범위: -30 ~ +30
// y = (acad_score - 50) * 0.6   // 범위: -30 ~ +30
// z = (media_score - 50) * 0.6  // 범위: -30 ~ +30
// radius = 10 + (network_score / 5)  // 범위: 10 ~ 30

MATCH (a:Artist)
WHERE a.inst_score IS NOT NULL
SET a.coord_x = round((coalesce(a.inst_score, 50) - 50) * 0.6, 2),
    a.coord_y = round((coalesce(a.acad_score, 50) - 50) * 0.6, 2),
    a.coord_z = round((coalesce(a.media_score, 50) - 50) * 0.6, 2),
    a.coord_radius = round(10.0 + (coalesce(a.network_score, 0) / 5.0), 2),
    a.coord_computed_at = toString(datetime()),
    a.coord_algorithm = 'normalize_v1'
RETURN count(a) AS coordinates_updated;
```

### 4.3 API 조회 쿼리 최적화

**파일**: `neo4j/queries/api_queries.cypher`

```cypher
// ========================================
// ARGO API Query Templates
// API Reference: ARGO_API_COMPLETE_SPECIFICATION.md Part I
// ========================================

// === GET /v1/api/artists ===
// :param skip, limit, segment_id, min_score
MATCH (a:Artist)
WHERE ($segment_id IS NULL OR a.segment_id = $segment_id)
  AND ($min_score IS NULL OR a.composite_score >= $min_score)
RETURN a {
    .id, .name, .alternateName, .segment_id, .genre,
    .inst_score, .acad_score, .media_score, .network_score,
    .composite_score, .composite_confidence,
    .coord_x, .coord_y, .coord_z, .coord_radius,
    .dominant_capital, .field_quadrant
}
ORDER BY a.composite_score DESC
SKIP $skip
LIMIT $limit;


// === GET /v1/api/artists/{artist_id} (상세 + 관계) ===
// :param artist_id
MATCH (a:Artist {id: $artist_id})
OPTIONAL MATCH (a)-[collab:COLLABORATED_WITH]-(peer:Artist)
OPTIONAL MATCH (a)-[affil:AFFILIATED_WITH]->(inst:Institution)
OPTIONAL MATCH (a)-[belong:BELONGS_TO]->(cluster:Cluster)
RETURN {
    artist: a {.*},
    collaborators: collect(DISTINCT {
        id: peer.id,
        name: peer.name,
        strength: collab.strength,
        collaboration_type: collab.collaboration_type
    })[0..10],
    institutions: collect(DISTINCT {
        id: inst.id,
        name: inst.name,
        role: affil.role
    }),
    cluster: cluster {.id, .name, .cluster_type, .artist_count}
} AS result;


// === GET /v1/api/artists/{artist_id}/network ===
// :param artist_id
MATCH (center:Artist {id: $artist_id})
OPTIONAL MATCH (center)-[r:COLLABORATED_WITH]-(neighbor:Artist)
WITH center, collect({
    node: neighbor {.id, .name, .composite_score},
    edge: r {.strength, .collaboration_type}
}) AS connections
RETURN {
    center: center {.id, .name, .composite_score},
    nodes: connections,
    total_connections: size(connections)
} AS network;


// === GET /v1/api/artists/{artist_id}/structural-equivalents ===
// Bourdieu Structural Equivalence (Manhattan Distance)
// :param artist_id
MATCH (target:Artist {id: $artist_id})
WHERE target.capital_inst_ratio IS NOT NULL
MATCH (other:Artist)
WHERE other.id <> target.id
  AND other.capital_inst_ratio IS NOT NULL
  AND other.field_quadrant = target.field_quadrant  // 같은 분면 우선
WITH target, other,
     abs(target.capital_inst_ratio - other.capital_inst_ratio) +
     abs(target.capital_acad_ratio - other.capital_acad_ratio) +
     abs(target.capital_media_ratio - other.capital_media_ratio) +
     abs(target.capital_network_ratio - other.capital_network_ratio) AS distance
WHERE distance < 0.30
RETURN other {.id, .name, .dominant_capital, .field_quadrant}, distance
ORDER BY distance ASC
LIMIT 10;


// === GET /v1/api/analysis/field-quadrants ===
MATCH (a:Artist)
WHERE a.field_quadrant IS NOT NULL
WITH a.field_quadrant AS quadrant, collect(a) AS artists
RETURN quadrant,
       size(artists) AS artist_count,
       round(avg([art IN artists | art.composite_score]), 2) AS avg_composite,
       [art IN artists | art.name][0..5] AS sample_names
ORDER BY artist_count DESC;


// === GET /v1/api/clusters ===
MATCH (c:Cluster)
OPTIONAL MATCH (c)<-[:BELONGS_TO]-(a:Artist)
WITH c, collect(a.id) AS member_ids, count(a) AS actual_count
RETURN c {
    .id, .name, .cluster_type, .dominant_genre,
    .avg_composite_score, .algorithm_version,
    member_ids: member_ids[0..20],
    member_count: actual_count
}
ORDER BY actual_count DESC;
```

### 4.4 [검증 게이트 4] 최종 검증

**파일**: `neo4j/queries/validation_final.cypher`

```cypher
// ========================================
// Final Validation: 전체 시스템 검증
// ========================================

// 1. 노드 카운트 최종
CALL {
    MATCH (a:Artist) RETURN 'Artist' AS type, count(a) AS cnt
    UNION ALL
    MATCH (i:Institution) RETURN 'Institution' AS type, count(i) AS cnt
    UNION ALL
    MATCH (e:Exhibition) RETURN 'Exhibition' AS type, count(e) AS cnt
    UNION ALL
    MATCH (w:Artwork) RETURN 'Artwork' AS type, count(w) AS cnt
    UNION ALL
    MATCH (p:Publication) RETURN 'Publication' AS type, count(p) AS cnt
    UNION ALL
    MATCH (c:Cluster) RETURN 'Cluster' AS type, count(c) AS cnt
}
RETURN type, cnt;

// 2. 관계 카운트 최종
CALL {
    MATCH ()-[r:COLLABORATED_WITH]->() RETURN 'COLLABORATED_WITH' AS type, count(r) AS cnt
    UNION ALL
    MATCH ()-[r:AFFILIATED_WITH]->() RETURN 'AFFILIATED_WITH' AS type, count(r) AS cnt
    UNION ALL
    MATCH ()-[r:PARTICIPATED_IN]->() RETURN 'PARTICIPATED_IN' AS type, count(r) AS cnt
    UNION ALL
    MATCH ()-[r:BELONGS_TO]->() RETURN 'BELONGS_TO' AS type, count(r) AS cnt
}
RETURN type, cnt;

// 3. 구조주의 분석 필드 완성도
MATCH (a:Artist)
WITH count(a) AS total,
     sum(CASE WHEN a.composite_score IS NOT NULL THEN 1 ELSE 0 END) AS has_composite,
     sum(CASE WHEN a.dominant_capital IS NOT NULL THEN 1 ELSE 0 END) AS has_dominant,
     sum(CASE WHEN a.field_quadrant IS NOT NULL THEN 1 ELSE 0 END) AS has_quadrant,
     sum(CASE WHEN a.coord_x IS NOT NULL THEN 1 ELSE 0 END) AS has_coords
RETURN
    total AS total_artists,
    has_composite AS with_composite_score,
    has_dominant AS with_dominant_capital,
    has_quadrant AS with_field_quadrant,
    has_coords AS with_coordinates,
    round(toFloat(has_coords) / total * 100, 1) AS completion_rate;

// 4. API 준비 상태
RETURN
    "Phase 4 Complete - API Ready" AS status,
    datetime() AS timestamp;
```

---

## 실행 명령어 요약

```bash
# === Phase 0: 준비 ===
python scripts/check_neo4j_data.py                    # 현재 상태 확인

# === Phase 1: 노드 적재 ===
python data_collection_pipeline.py --source ARKO --max-count 100
python data_collection_pipeline.py --source KCI --max-count 200
python data_collection_pipeline.py --source MMCA_COLLECTION --max-count 500
python data_collection_pipeline.py --source CHEONGJU_BIENNALE --max-count 100
# 검증
python scripts/run_cypher.py neo4j/queries/validation_phase1.cypher

# === Phase 2: 관계 생성 ===
python scripts/run_cypher.py neo4j/queries/01_relationship_creation.cypher
# 검증
python scripts/run_cypher.py neo4j/queries/validation_phase2.cypher

# === Phase 3: GDS 분석 ===
python scripts/run_cypher.py neo4j/queries/03_gds_execution.cypher
python scripts/run_cypher.py neo4j/queries/02_cluster_creation.cypher
# 검증
python scripts/run_cypher.py neo4j/queries/validation_phase3.cypher

# === Phase 4: 구조주의 분석 ===
python scripts/run_cypher.py neo4j/queries/structuralist_analysis.cypher
python scripts/run_cypher.py neo4j/queries/04_coordinates_update.cypher
# 최종 검증
python scripts/run_cypher.py neo4j/queries/validation_final.cypher
python scripts/verify_data_quality.py
```

---

## 산출물 체크리스트

| 산출물 | 파일 경로 | 상태 |
|--------|----------|------|
| 백업 스크립트 | `neo4j/queries/00_backup_snapshot.cypher` | 작성 필요 |
| 초기화 스크립트 | `neo4j/queries/00_cleanup.cypher` | 작성 필요 |
| 관계 생성 쿼리 | `neo4j/queries/01_relationship_creation.cypher` | 작성 필요 |
| 클러스터 생성 쿼리 | `neo4j/queries/02_cluster_creation.cypher` | 작성 필요 |
| GDS 실행 쿼리 | `neo4j/queries/03_gds_execution.cypher` | 작성 필요 |
| 좌표 업데이트 쿼리 | `neo4j/queries/04_coordinates_update.cypher` | 작성 필요 |
| API 쿼리 | `neo4j/queries/api_queries.cypher` | 작성 필요 |
| 검증 쿼리 (Phase 1-4) | `neo4j/queries/validation_*.cypher` | 작성 필요 |
| 관계 생성 스크립트 v2 | `scripts/create_relationships_v2.py` | 작성 필요 |
| Cypher 실행 스크립트 | `scripts/run_cypher.py` | 작성 필요 |

---

## 성공 기준 종합

| Phase | 검증 항목 | 성공 기준 |
|-------|----------|----------|
| 1 | Artist 카운트 | ≥ 100 |
| 1 | Exhibition 카운트 | ≥ 50 |
| 2 | COLLABORATED_WITH | ≥ 10 |
| 2 | 고아 관계 | = 0 |
| 3 | network_score 보유 | ≥ 50% |
| 3 | Cluster 카운트 | ≥ 3 |
| 4 | field_quadrant 보유 | ≥ 80% |
| 4 | coordinates 보유 | ≥ 90% |

**모든 기준 충족 시 MVP 배포 가능**

---

**Document End**
