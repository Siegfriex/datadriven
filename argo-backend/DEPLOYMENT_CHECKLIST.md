# Neo4j MVP 배포 체크리스트

## 목표
모든 테스트가 통과되면 프로덕션 Neo4j에 배포할 수 있도록 준비합니다.

## Phase별 체크리스트

### Phase 1: 환경 준비 및 연결 검증
- [ ] Neo4j 연결 테스트 통과 (`scripts/test_neo4j_connection.py`)
- [ ] 환경변수 검증 통과 (`scripts/verify_env.py`)
- [ ] 필수 환경변수 모두 설정됨 (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

### Phase 2: 스키마 초기화 및 검증
- [ ] 스키마 초기화 실행 완료 (`scripts/init_neo4j_schema.py`)
- [ ] 제약조건 6개 모두 생성됨
- [ ] 인덱스 8개 모두 생성됨
- [ ] Fulltext 인덱스 3개 모두 생성됨
- [ ] 스키마 무결성 검증 통과 (`scripts/verify_schema_integrity.py`)

### Phase 3: 데이터 업로드 검증
- [ ] 소규모 데이터 업로드 테스트 통과 (10명)
- [ ] 중규모 데이터 업로드 테스트 통과 (50명)
- [ ] 모든 Artist에 `coordinates_3d` 존재
- [ ] 모든 Artist에 점수 존재
- [ ] 데이터 품질 검증 통과 (`scripts/verify_data_quality.py`)

### Phase 4: 관계 생성 검증
- [ ] COLLABORATED_WITH 관계 생성 완료
- [ ] AFFILIATED_WITH 관계 생성 완료
- [ ] PARTICIPATED_IN 관계 생성 완료
- [ ] 관계 무결성 검증 통과 (고아 관계 없음)

### Phase 5: GDS 분석 실행 및 검증
- [ ] GDS 프로젝션 생성 성공
- [ ] Degree Centrality 계산 완료
- [ ] Betweenness Centrality 계산 완료
- [ ] Eigenvector Centrality 계산 완료
- [ ] 모든 Artist에 중심성 값 존재
- [ ] Louvain 커뮤니티 탐지 실행 완료
- [ ] 모든 Artist에 `community_id` 존재
- [ ] Cluster 노드 생성됨
- [ ] BELONGS_TO 관계 생성됨

### Phase 6: 구조주의 분석 필드 계산 검증
- [ ] Capital Composition 계산 완료
- [ ] Dominant Capital 결정 완료
- [ ] Field Quadrant 분류 완료
- [ ] Network Score 업데이트 완료 (GDS 기반)
- [ ] 모든 필드가 계산되어 저장됨
- [ ] Capital Composition 합계 = 1.0 (오차 0.01 이내)

### Phase 7: API 엔드포인트 통합 테스트
- [ ] API 서버 정상 시작
- [ ] Health check 엔드포인트 응답
- [ ] 모든 핵심 엔드포인트 테스트 통과 (`scripts/test_api_endpoints.py`)
  - [ ] GET /health
  - [ ] GET /v1/api/galaxy-snapshot
  - [ ] GET /v1/api/artists
  - [ ] GET /v1/api/artists/{id}
  - [ ] GET /v1/api/artists/{id}/structural-equivalents
  - [ ] GET /v1/api/artists/{id}/capital-composition
  - [ ] POST /v1/api/analysis/centrality
  - [ ] POST /v1/api/analysis/community-detection
  - [ ] GET /v1/api/analysis/field-quadrants
  - [ ] POST /v1/api/analysis/run-gds-centrality
  - [ ] POST /v1/api/analysis/run-louvain
  - [ ] POST /v1/api/analysis/calculate-structuralist
- [ ] 모든 응답이 JSON-LD 형식 준수
- [ ] 구조주의 필드 포함 여부 확인
- [ ] 좌표 데이터 형식 정확성 확인

### Phase 8: 성능 및 스트레스 테스트
- [ ] 작가 목록 조회 성능 < 500ms (`scripts/test_query_performance.py`)
- [ ] 작가 상세 조회 성능 < 500ms
- [ ] 구조적 등가성 계산 성능 < 2초
- [ ] Galaxy snapshot 조회 성능 < 1초
- [ ] 동시성 테스트 통과 (동시 10개 요청 모두 성공)

### Phase 9: 최종 통합 검증
- [ ] 전체 시스템 검증 통과 (`scripts/verify_neo4j_mvp.py`)
- [ ] 제약조건 및 인덱스 확인
- [ ] 노드 타입별 카운트 확인
- [ ] 관계 타입별 카운트 확인
- [ ] 구조주의 분석 필드 확인
- [ ] GDS 분석 필드 확인
- [ ] 샘플 데이터 확인
- [ ] 데이터 일관성 검증 통과

### Phase 10: 프로덕션 배포 준비
- [ ] 배포 체크리스트 작성 완료 (이 문서)
- [ ] 롤백 계획 수립 완료 (`scripts/rollback_schema.py`)
- [ ] 모든 Phase 통과 확인
- [ ] 검증 스크립트 모두 성공 확인
- [ ] API 엔드포인트 모두 정상 작동 확인
- [ ] 성능 기준 충족 확인

## Go/No-Go 결정 기준

### Go (프로덕션 배포 가능)
- ✅ 모든 Phase 통과
- ✅ 검증 스크립트 모두 성공
- ✅ API 엔드포인트 모두 정상 작동
- ✅ 성능 기준 충족

### No-Go (재검토 필요)
- ❌ Phase 1-2 실패: 환경/스키마 문제
- ❌ Phase 3-4 실패: 데이터/관계 문제
- ❌ Phase 5-6 실패: 분석 알고리즘 문제
- ❌ Phase 7-8 실패: API/성능 문제

## 배포 전 최종 확인사항

1. **환경 설정**
   - [ ] 프로덕션 Neo4j 인스턴스 연결 정보 확인
   - [ ] Secret Manager에 모든 환경변수 설정됨
   - [ ] Cloud Run 서비스 계정 권한 확인

2. **데이터 백업**
   - [ ] 현재 Neo4j 데이터 백업 완료
   - [ ] 롤백 스크립트 테스트 완료

3. **모니터링**
   - [ ] Cloud Monitoring 알림 설정
   - [ ] Cloud Logging 설정 확인
   - [ ] 에러 알림 설정 확인

4. **문서화**
   - [ ] 배포 절차 문서화 완료
   - [ ] 롤백 절차 문서화 완료
   - [ ] 운영 가이드 작성 완료

## 배포 후 확인사항

1. **즉시 확인 (배포 직후)**
   - [ ] API 서버 정상 시작 확인
   - [ ] Health check 엔드포인트 응답 확인
   - [ ] 핵심 엔드포인트 1-2개 수동 테스트

2. **1시간 후 확인**
   - [ ] 에러 로그 확인
   - [ ] 성능 메트릭 확인
   - [ ] Neo4j 연결 상태 확인

3. **24시간 후 확인**
   - [ ] 전체 시스템 안정성 확인
   - [ ] 성능 메트릭 분석
   - [ ] 사용자 피드백 수집

## 롤백 절차

1. **스키마 롤백**
   ```bash
   python scripts/rollback_schema.py
   ```

2. **데이터 롤백**
   - Neo4j 백업에서 복원

3. **관계 롤백**
   - 관계 삭제 스크립트 실행

## 연락처 및 참조

- **설계 문서**: `docs/ARGO_NEO4J_MVP_DESIGN.md`
- **스키마 정의**: `docs/ARGO_Final_Schema.md`
- **검증 스크립트**: `argo-backend/scripts/verify_neo4j_mvp.py`

## 체크리스트 업데이트 이력

- 2025-01-XX: 초기 작성


