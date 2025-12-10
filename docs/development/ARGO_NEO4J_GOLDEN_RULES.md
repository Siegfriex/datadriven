# ARGO Neo4j 황금률 (Golden Rules)

**Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Mandatory Reference
**Scope**: 모든 Neo4j 관련 개발 작업

---

## 문서 목적

이 문서는 ARGO 프로젝트에서 Neo4j 작업 시 **반드시 준수해야 할 규칙**을 정의합니다.
과거 발생한 문제(데이터 손실, 관계 부재, 쿼리 하드코딩)의 재발을 방지하고,
문서 스위트(TSD, Schema, API Spec)와의 정합성을 보장합니다.

---

## 1. ID 생성 규칙

### 1.1 황금률: 해시 기반 고유 ID 생성

```
❌ 금지: title만으로 ID 생성 (title이 None이면 중복 발생)
✅ 필수: 복합 필드 + 해시로 고유성 보장
```

### 1.2 ID 생성 공식

| 엔터티 | ID 패턴 | 구성 요소 |
|--------|---------|----------|
| Artist | `artist_{name}_{hash8}` | name + index |
| Artwork | `artwork_{artist}_{title}_{hash8}` | artist_name + title + install_year + building_name |
| Publication | `pub_{title}_{year}_{hash8}` | title_ko + first_author + year + issn |
| Exhibition | `exh_{title}_{year}_{hash8}` | title + year |
| Institution | `inst_{name}_{hash8}` | name |
| Cluster | `cluster_{algorithm}_{id}` | algorithm + community_id |

### 1.3 해시 생성 코드 패턴

```python
import hashlib

def generate_unique_id(entity_type: str, *components) -> str:
    """
    고유 ID 생성 (황금률 준수)

    Args:
        entity_type: 엔터티 타입 (artist, artwork, pub, etc.)
        *components: ID 구성 요소들

    Returns:
        고유 ID 문자열
    """
    # 1. 구성 요소 결합
    unique_str = "_".join(str(c) for c in components if c)

    # 2. 해시 생성 (MD5 8자리)
    unique_hash = hashlib.md5(unique_str.encode()).hexdigest()[:8]

    # 3. 클린 이름 생성
    import re
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', components[0].lower())[:20] if components else "unknown"

    return f"{entity_type}_{clean_name}_{unique_hash}"
```

### 1.4 검증 규칙

```cypher
// ID 중복 검사 (배포 전 필수 실행)
MATCH (n)
WITH n.id AS id, count(*) AS cnt
WHERE cnt > 1
RETURN id, cnt
ORDER BY cnt DESC;
```

---

## 2. 관계 생성 규칙

### 2.1 황금률: 실데이터 기반 관계 생성

```
❌ 금지: metadata 필드에 의존하는 관계 생성
❌ 금지: 존재하지 않는 필드 참조 (metadata.coauthors 등)
✅ 필수: 실제 수집된 데이터에서 관계 추출
```

### 2.2 데이터 소스-관계 매핑

| 관계 타입 | 데이터 소스 | 추출 필드 | 생성 조건 |
|----------|------------|----------|----------|
| `COLLABORATED_WITH` | Publication | `authors[]` | 공동저자 2명 이상 |
| `AFFILIATED_WITH` | Institution + Artist | `segment_id` 매칭 | 분야 일치 시 |
| `PARTICIPATED_IN` | Exhibition + Artist | `artist_name` | 이름 매칭 |
| `DISPLAYED_IN` | Artwork + Exhibition | `install_year` | 연도 매칭 |
| `BELONGS_TO` | Louvain 결과 | `community_id` | GDS 실행 후 |

### 2.3 관계 생성 전 체크리스트

```
□ 소스 노드 존재 확인
□ 타겟 노드 존재 확인
□ 매칭 필드 NULL 아님 확인
□ 중복 관계 방지 (MERGE 사용)
□ 관계 속성 기본값 설정
```

### 2.4 관계 생성 코드 패턴

```cypher
// 황금률 준수 관계 생성 패턴
MATCH (source:Artist)
WHERE source.name IS NOT NULL  // 필드 존재 확인
MATCH (target:Institution)
WHERE target.name IS NOT NULL  // 필드 존재 확인
  AND (source.segment_id CONTAINS 'painting' AND target.name CONTAINS '미술')  // 실데이터 조건
MERGE (source)-[r:AFFILIATED_WITH]->(target)  // MERGE로 중복 방지
ON CREATE SET
    r.created_at = datetime(),
    r.inferred = true,  // 추론 여부 명시
    r.source = 'segment_matching'  // 생성 근거 명시
RETURN count(r);
```

---

## 3. Cypher 쿼리 관리 규칙

### 3.1 황금률: 쿼리 파일화 원칙

```
❌ 금지: Python 코드에 Cypher 쿼리 하드코딩
✅ 필수: neo4j/queries/*.cypher 파일로 관리
✅ 필수: QueryLoader를 통한 쿼리 로드
```

**이론적 근거**: TSD §1 "모든 쿼리는 Cypher 공개 (투명성 원칙)"

### 3.2 쿼리 파일 구조

```
neo4j/queries/
├── 00_backup_snapshot.cypher    # 백업/복구
├── 00_cleanup.cypher            # 초기화
├── 01_relationship_creation.cypher  # 관계 생성
├── 02_cluster_creation.cypher   # 클러스터
├── 03_gds_execution.cypher      # GDS 분석
├── 04_coordinates_update.cypher # 좌표 계산
├── structuralist_analysis.cypher    # 구조주의 분석
├── api_queries.cypher           # API용 쿼리
└── validation_*.cypher          # 검증 쿼리
```

### 3.3 쿼리 파일 헤더 표준

```cypher
// ========================================
// File: [파일명].cypher
// Purpose: [목적]
// API Reference: [관련 API 엔드포인트]
// TSD Reference: [관련 TSD 섹션]
// Prerequisite: [선행 조건]
// Author: [작성자]
// Last Updated: [날짜]
// ========================================
```

### 3.4 쿼리 블록 구분 표준

```cypher
// === [쿼리명] ===
// Purpose: [목적]
// API: [엔드포인트]
// Input: $param1, $param2
// Output: [반환 필드]

[쿼리 본문]
```

---

## 4. 검증 게이트 규칙

### 4.1 황금률: 단계별 검증 필수

```
❌ 금지: 검증 없이 다음 Phase 진행
✅ 필수: 각 Phase 완료 후 검증 게이트 통과
✅ 필수: 실패 시 이전 Phase로 롤백
```

### 4.2 검증 게이트 체계

| Phase | 검증 항목 | 성공 기준 | 실패 시 조치 |
|-------|----------|----------|------------|
| 1 | 노드 카운트 | Artist ≥ 100, Exhibition ≥ 50 | 데이터 재수집 |
| 2 | 관계 카운트 | COLLABORATED_WITH ≥ 10 | 관계 로직 수정 |
| 2 | 고아 관계 | = 0 | 관계 삭제 후 재생성 |
| 3 | network_score | ≥ 50% 보유 | GDS 재실행 |
| 3 | Cluster | ≥ 3개 | Louvain 파라미터 조정 |
| 4 | field_quadrant | ≥ 80% 보유 | 분석 쿼리 재실행 |

### 4.3 검증 쿼리 패턴

```cypher
// 검증 게이트 쿼리 패턴
WITH {
    artist_count: 100,
    relation_count: 10,
    orphan_count: 0
} AS criteria

MATCH (a:Artist) WITH criteria, count(a) AS actual_artists
MATCH ()-[r:COLLABORATED_WITH]->() WITH criteria, actual_artists, count(r) AS actual_relations

RETURN
    actual_artists >= criteria.artist_count AS artist_pass,
    actual_relations >= criteria.relation_count AS relation_pass,
    actual_artists AS actual,
    criteria.artist_count AS required;
```

---

## 5. GDS 실행 규칙

### 5.1 황금률: 순서 의존성 준수

```
Graph Projection → Centrality → Community → Cluster 노드
```

```
❌ 금지: 관계 없이 GDS 실행 (실패함)
❌ 금지: Projection 없이 알고리즘 실행
✅ 필수: 최소 관계 수 확인 후 실행 (≥ 10)
```

### 5.2 GDS 실행 전제조건

| 알고리즘 | 전제조건 |
|---------|---------|
| `gds.graph.project` | COLLABORATED_WITH 관계 ≥ 10 |
| `gds.degree.write` | Graph Projection 완료 |
| `gds.betweenness.write` | Graph Projection 완료 |
| `gds.eigenvector.write` | Graph Projection 완료, 연결 그래프 |
| `gds.louvain.write` | Graph Projection 완료 |

### 5.3 GDS 실패 대응

```cypher
// GDS 실행 전 검증
MATCH ()-[r:COLLABORATED_WITH]->()
WITH count(r) AS rel_count
RETURN
    rel_count AS total_relations,
    CASE WHEN rel_count >= 10 THEN 'GDS_READY' ELSE 'INSUFFICIENT_RELATIONS' END AS status;
```

### 5.4 Projection 정리

```cypher
// 기존 Projection 삭제 (재실행 전 필수)
CALL gds.graph.drop('artist-collaboration-graph', false) YIELD graphName;
```

---

## 6. 구조주의 분석 규칙 (Bourdieu Field Theory)

### 6.1 황금률: 이론적 기반 명시

```
✅ 필수: 모든 분석 필드에 이론적 근거 주석
✅ 필수: 가중치 적용 시 출처 명시
✅ 필수: 알고리즘 버전 기록
```

### 6.2 4-Capital 모델 가중치

| 자본 유형 | 필드 | 가중치 | 이론적 근거 |
|----------|------|--------|------------|
| Institutional | `inst_score` | 0.30 | 제도적 인정 (미술관, 비엔날레) |
| Academic | `acad_score` | 0.20 | 학술적 정당화 (논문, 인용) |
| Media | `media_score` | 0.25 | 담론적 가시성 (미디어 언급) |
| Network | `network_score` | 0.25 | 사회적 연결 (GDS 중심성) |

**출처**: Bourdieu, P. (1984). Distinction. / Bourdieu, P. (1993). The Field of Cultural Production.

### 6.3 Field Quadrant 분류

```
              High Academic
                   │
    Q2             │            Q1
 Academic Elite    │         Established
                   │
 ──────────────────┼────────────────────── High Institutional
                   │
    Q4             │            Q3
   Emerging        │         Media Star
                   │
              Low Academic
```

### 6.4 분석 필드 계산 순서

```
1. composite_score 계산 (가중 평균)
    ↓
2. capital_*_ratio 계산 (정규화)
    ↓
3. dominant_capital 결정 (최대 비율)
    ↓
4. field_quadrant 분류 (중앙값 기준)
    ↓
5. coordinates_3d 계산 (시각화용)
```

---

## 7. 스키마 준수 규칙

### 7.1 황금률: Schema.org + ARGO 확장

```
✅ 필수: 기본 필드는 Schema.org 표준 준수
✅ 필수: 확장 필드는 'argo:' 네임스페이스 사용
✅ 필수: JSON-LD 형식 응답
```

### 7.2 필수 필드 체크리스트

| 노드 | 필수 필드 | 검증 |
|------|----------|------|
| Artist | `id`, `name`, `composite_score` | NOT NULL |
| Artist | `inst_score`, `acad_score`, `media_score`, `network_score` | 0-100 범위 |
| Artist | `coord_x`, `coord_y`, `coord_z`, `coord_radius` | 숫자 타입 |
| Institution | `id`, `name`, `type` | NOT NULL |
| Exhibition | `id`, `title`, `year` | NOT NULL |

### 7.3 점수 범위 규칙

| 필드 | 범위 | 검증 쿼리 |
|------|------|----------|
| `*_score` | 0-100 | `WHERE score < 0 OR score > 100` |
| `*_ratio` | 0-1 | `WHERE ratio < 0 OR ratio > 1` |
| `composite_confidence` | 0-1 | `WHERE conf < 0 OR conf > 1` |
| `coord_x/y/z` | -30 ~ +30 | `WHERE abs(coord) > 30` |

---

## 8. 성능 최적화 규칙

### 8.1 황금률: 인덱스 선행 생성

```
❌ 금지: 인덱스 없이 대량 쿼리 실행
✅ 필수: 자주 사용하는 필드에 인덱스 생성
✅ 필수: 고유 제약조건으로 중복 방지
```

### 8.2 필수 인덱스 목록

```cypher
// 고유 제약조건
CREATE CONSTRAINT artist_id_unique IF NOT EXISTS FOR (a:Artist) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT institution_id_unique IF NOT EXISTS FOR (i:Institution) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT exhibition_id_unique IF NOT EXISTS FOR (e:Exhibition) REQUIRE e.id IS UNIQUE;

// 성능 인덱스
CREATE INDEX artist_composite_score IF NOT EXISTS FOR (a:Artist) ON (a.composite_score);
CREATE INDEX artist_segment IF NOT EXISTS FOR (a:Artist) ON (a.segment_id);
CREATE INDEX artist_field_quadrant IF NOT EXISTS FOR (a:Artist) ON (a.field_quadrant);

// 풀텍스트 인덱스
CREATE FULLTEXT INDEX artist_name_search IF NOT EXISTS FOR (a:Artist) ON EACH [a.name, a.alternateName];
```

### 8.3 배치 처리 규칙

```
✅ 권장: 1000개 단위 배치 처리
✅ 권장: APOC apoc.periodic.iterate 사용
❌ 금지: 단일 트랜잭션에 10만 건 이상
```

```cypher
// 대량 업데이트 배치 패턴
CALL apoc.periodic.iterate(
    "MATCH (a:Artist) WHERE a.composite_score IS NULL RETURN a",
    "SET a.composite_score = 0.0",
    {batchSize: 1000, parallel: false}
) YIELD batches, total
RETURN batches, total;
```

---

## 9. 백업/복구 규칙

### 9.1 황금률: 변경 전 백업 필수

```
❌ 금지: 백업 없이 대량 수정/삭제
✅ 필수: 변경 전 스냅샷 저장
✅ 필수: 롤백 스크립트 준비
```

### 9.2 백업 체크리스트

```
□ 노드 카운트 스냅샷 저장
□ 관계 카운트 스냅샷 저장
□ 롤백 스크립트 준비 완료
□ 테스트 환경에서 검증 완료
```

### 9.3 롤백 우선순위

```
1. 관계 삭제 (가장 먼저)
2. 신규 노드 삭제
3. 수정된 속성 복원
4. 인덱스/제약조건 복원
```

---

## 10. 문서 참조 규칙

### 10.1 문서-코드 동기화

| 변경 유형 | 업데이트 필요 문서 |
|----------|-------------------|
| 스키마 변경 | ARGO_Final_Schema.md |
| API 변경 | ARGO_API_COMPLETE_SPECIFICATION.md |
| 가중치 변경 | ARGO_TSD_Final.md §2.1 |
| 쿼리 추가 | neo4j/queries/*.cypher |
| 규칙 추가 | 이 문서 (Golden Rules) |

### 10.2 코드 주석 필수 포함 사항

```python
"""
[함수/클래스 설명]

TSD Reference: §X.X
Schema Reference: §X.X
API Reference: [엔드포인트]
Golden Rule: [해당 규칙 번호]
"""
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│              ARGO Neo4j 황금률 요약                      │
├─────────────────────────────────────────────────────────┤
│ 1. ID는 해시 기반으로 생성하라                           │
│ 2. 관계는 실데이터에서 추출하라                          │
│ 3. 쿼리는 파일로 관리하라                               │
│ 4. 단계별 검증 게이트를 통과하라                         │
│ 5. GDS는 순서대로 실행하라                              │
│ 6. Bourdieu 이론 기반을 명시하라                         │
│ 7. Schema.org 표준을 준수하라                            │
│ 8. 인덱스를 먼저 생성하라                               │
│ 9. 변경 전 백업하라                                     │
│ 10. 문서와 코드를 동기화하라                             │
└─────────────────────────────────────────────────────────┘

가중치: inst=0.30, acad=0.20, media=0.25, network=0.25
점수 범위: 0-100 | 비율 범위: 0-1 | 좌표 범위: -30~+30
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2025-12-10 | 초기 작성 | Architecture Team |

---

**이 문서는 ARGO 프로젝트의 모든 Neo4j 관련 개발 작업에서 필수 참조 문서입니다.**
