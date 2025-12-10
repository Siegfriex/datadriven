# Operations Documents (운영 문서)

**위치**: `docs/operations/`

## 문서 목록

| 문서 | 역할 | 핵심 문서 참조 |
|------|------|--------------|
| **ARGO_SRD_Final.md** | 소프트웨어 요구사항 명세 | TSD 섹션 1-3 |
| **ARGO_SERVICE_ACCOUNTS.md** | IAM 서비스 계정 정의 | TSD Appendix A |
| **ARGO_GCP_INFRASTRUCTURE_SETUP.md** | GCP 인프라 설정 가이드 | TSD 섹션 5 |
| **ARGO_NEO4J_MVP_DESIGN.md** | Neo4j MVP 설계 | TSD 섹션 2 |
| **ARGO_DATA_COLLECTION_METHODOLOGY.md** | 데이터 수집 방법론 | TSD 섹션 2.1 |

## 사용 목적

- **인프라 배포/재배포** 시 참조
- **서비스 계정 권한 설정** 시 참조
- **데이터 수집 파이프라인 운영** 시 참조
- **Neo4j 연결/설정** 시 참조

## 핵심 정보

### Neo4j Aura 인스턴스
- **Instance ID**: be57a318
- **URI**: `neo4j+s://be57a318.databases.neo4j.io`

### GCP 프로젝트
- **Project ID**: artdrive1208
- **Project Number**: 55248184822
- **Region**: asia-northeast3 (서울)

---

**참조**: 모든 운영 정보는 `docs/ARGO_TSD_Final.md`의 해당 섹션과 연계됩니다.
