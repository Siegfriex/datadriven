# 데이터 소스-관계 매핑 명세 (Data Source to Relationship Mapping)

## 개요
이 문서는 ARGO 프로젝트에서 수집된 원본 데이터(Source Data)가 Neo4j 그래프 데이터베이스의 관계(Relationship)로 변환되는 로직을 정의합니다.

## 관계 매핑 테이블

| 관계 타입 (Type) | 소스 데이터 (Source) | 매칭 로직 (Logic) | 비고 (Note) |
| :--- | :--- | :--- | :--- |
| `COLLABORATED_WITH` | KCI Publication | `authors` 배열 내 2인 조합 생성 (nC2) | 공동저자 관계, 가중치=논문수 |
| `AFFILIATED_WITH` | KCI Paper / ARKO | `publisher` (논문 발행기관) ↔ `Institution.name` | Fuzzy Matching (유사도 > 0.8) |
| `PARTICIPATED_IN` | Cheongju Biennale | `participants` (참여작가) ↔ `Exhibition` | 연도별 비엔날레 전시와 매칭 |
| `DISPLAYED_IN` | MMCA Collection | `artist` ↔ `Exhibition` (소장품 전시 이력) | (추후 확장 예정) |
| `BELONGS_TO` | Analysis Result | Louvain Community ID ↔ `Cluster` | GDS 분석 결과 기반 생성 |

## 세부 구현 전략

### 1. COLLABORATED_WITH (공동저자)
- **Source**: `Publication` 노드의 `authors` 속성 (List<String>)
- **Logic**: APOC 라이브러리의 `apoc.coll.combinations(authors, 2)` 함수 사용하여 저자 쌍 생성
- **Query**:
  ```cypher
  MATCH (p:Publication)
  UNWIND apoc.coll.combinations(p.authors, 2) AS pair
  MATCH (a1:Artist {name: pair[0]}), (a2:Artist {name: pair[1]})
  MERGE (a1)-[r:COLLABORATED_WITH]-(a2)
  ...
  ```

### 2. AFFILIATED_WITH (소속)
- **Source**: `Publication.publisher` 또는 Artist Metadata의 `affiliations`
- **Logic**: 텍스트 유사도 매칭 (`apoc.text.sorensenDiceSimilarity`)
- **Threshold**: 유사도 0.8 이상일 경우 관계 생성

### 3. PARTICIPATED_IN (전시 참여)
- **Source**: Biennale API 응답 데이터
- **Logic**: 작가명 정확히 일치 시 관계 생성



