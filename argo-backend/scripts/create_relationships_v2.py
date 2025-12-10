"""
관계 생성 스크립트 v2
- Cypher 파일 기반 실행
- 검증 게이트 통합
- 실데이터 기반 관계 생성

Usage:
    python scripts/create_relationships_v2.py
    python scripts/create_relationships_v2.py --phase 2
    python scripts/create_relationships_v2.py --validate-only
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# Cypher 쿼리 정의 (파일 대신 인라인)
# ============================================================

RELATIONSHIP_QUERIES = {
    "COLLABORATED_WITH": """
        // Publication 공동저자 기반 협업 관계
        MATCH (p:Publication)
        WHERE p.authors IS NOT NULL AND size(p.authors) > 1
        WITH p, p.authors AS authors
        UNWIND range(0, size(authors)-2) AS i
        UNWIND range(i+1, size(authors)-1) AS j
        WITH p, authors[i] AS author1, authors[j] AS author2
        WHERE author1 <> author2

        MATCH (a1:Artist)
        WHERE a1.name = author1 OR a1.name CONTAINS author1
        MATCH (a2:Artist)
        WHERE a2.name = author2 OR a2.name CONTAINS author2
        WHERE a1.id <> a2.id

        MERGE (a1)-[r:COLLABORATED_WITH]->(a2)
        ON CREATE SET
            r.strength = 0.5,
            r.collaboration_type = 'co_authorship',
            r.publication_id = p.id,
            r.created_at = datetime()
        ON MATCH SET
            r.strength = CASE WHEN r.strength < 1.0 THEN r.strength + 0.1 ELSE 1.0 END,
            r.updated_at = datetime()
        RETURN count(r) AS count
    """,

    "AFFILIATED_WITH": """
        // Segment 기반 소속 추론
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
        RETURN count(r) AS count
    """,

    "PARTICIPATED_IN": """
        // Biennale 참여 관계
        MATCH (a:Artist)
        MATCH (e:Exhibition)
        WHERE e.type = 'biennale'
          AND (a.name = e.artist_name OR e.participants CONTAINS a.name)
        MERGE (a)-[r:PARTICIPATED_IN]->(e)
        ON CREATE SET
            r.role = 'participant',
            r.year = e.year,
            r.created_at = datetime()
        RETURN count(r) AS count
    """,

    "CREATED": """
        // Artist-Artwork 생성 관계
        MATCH (a:Artist)
        MATCH (w:Artwork)
        WHERE w.artist_name = a.name OR w.artist_name CONTAINS a.name
        MERGE (a)-[r:CREATED]->(w)
        ON CREATE SET
            r.role = 'primary_artist',
            r.created_at = datetime()
        RETURN count(r) AS count
    """,

    "AUTHORED": """
        // Artist-Publication 저술 관계
        MATCH (a:Artist)
        MATCH (p:Publication)
        WHERE p.authors IS NOT NULL AND a.name IN p.authors
        MERGE (a)-[r:AUTHORED]->(p)
        ON CREATE SET
            r.role = 'author',
            r.created_at = datetime()
        RETURN count(r) AS count
    """
}

VALIDATION_QUERIES = {
    "node_count": """
        MATCH (a:Artist) WITH count(a) AS artist_count
        MATCH (i:Institution) WITH artist_count, count(i) AS inst_count
        MATCH (e:Exhibition) WITH artist_count, inst_count, count(e) AS exh_count
        MATCH (w:Artwork) WITH artist_count, inst_count, exh_count, count(w) AS artwork_count
        MATCH (p:Publication) WITH artist_count, inst_count, exh_count, artwork_count, count(p) AS pub_count
        RETURN artist_count, inst_count, exh_count, artwork_count, pub_count
    """,

    "relationship_count": """
        MATCH ()-[r:COLLABORATED_WITH]->() WITH count(r) AS collab
        MATCH ()-[r:AFFILIATED_WITH]->() WITH collab, count(r) AS affil
        MATCH ()-[r:PARTICIPATED_IN]->() WITH collab, affil, count(r) AS partic
        MATCH ()-[r:CREATED]->() WITH collab, affil, partic, count(r) AS created
        MATCH ()-[r:AUTHORED]->() WITH collab, affil, partic, created, count(r) AS authored
        RETURN collab, affil, partic, created, authored
    """,

    "orphan_check": """
        MATCH ()-[r]->()
        WHERE NOT exists(startNode(r)) OR NOT exists(endNode(r))
        RETURN type(r) AS type, count(r) AS orphan_count
    """,

    "isolated_artists": """
        MATCH (a:Artist)
        WHERE NOT (a)--()
        RETURN count(a) AS isolated_count
    """
}


class RelationshipCreator:
    """관계 생성 및 검증 클래스"""

    def __init__(self):
        self.results = {}
        self.start_time = None

    def run_query(self, name: str, query: str) -> Optional[Dict]:
        """쿼리 실행 및 결과 반환"""
        try:
            result = neo4j_service.execute_query(query)
            if result and len(result) > 0:
                return result[0]
            return {}
        except Exception as e:
            logger.error(f"쿼리 실행 실패 [{name}]: {e}")
            return None

    def validate_prerequisites(self) -> bool:
        """Phase 1 검증: 노드 데이터 존재 확인"""
        print("\n" + "=" * 60)
        print("사전 검증: 노드 데이터 확인")
        print("=" * 60)

        result = self.run_query("node_count", VALIDATION_QUERIES["node_count"])

        if result is None:
            print("✗ 노드 카운트 조회 실패")
            return False

        print(f"  Artist: {result.get('artist_count', 0)}개")
        print(f"  Institution: {result.get('inst_count', 0)}개")
        print(f"  Exhibition: {result.get('exh_count', 0)}개")
        print(f"  Artwork: {result.get('artwork_count', 0)}개")
        print(f"  Publication: {result.get('pub_count', 0)}개")

        # 최소 요건 확인
        if result.get('artist_count', 0) < 10:
            print("\n✗ Artist 노드가 부족합니다 (최소 10개 필요)")
            return False

        print("\n✓ 사전 검증 통과")
        return True

    def create_relationships(self, relationship_types: Optional[List[str]] = None):
        """관계 생성 실행"""
        self.start_time = datetime.now()

        print("\n" + "=" * 60)
        print("Phase 2: 관계 생성")
        print(f"시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        types_to_create = relationship_types or list(RELATIONSHIP_QUERIES.keys())

        for rel_type in types_to_create:
            if rel_type not in RELATIONSHIP_QUERIES:
                logger.warning(f"알 수 없는 관계 타입: {rel_type}")
                continue

            print(f"\n▶ {rel_type} 관계 생성 중...")

            query = RELATIONSHIP_QUERIES[rel_type]
            result = self.run_query(rel_type, query)

            if result is not None:
                count = result.get('count', 0)
                self.results[rel_type] = count
                print(f"  ✓ {count}개 생성 완료")
            else:
                self.results[rel_type] = -1
                print(f"  ✗ 생성 실패")

    def validate_results(self) -> bool:
        """관계 생성 결과 검증"""
        print("\n" + "=" * 60)
        print("검증 게이트: 관계 무결성 확인")
        print("=" * 60)

        # 관계 카운트 확인
        result = self.run_query("relationship_count", VALIDATION_QUERIES["relationship_count"])

        if result:
            print("\n관계 타입별 카운트:")
            print(f"  COLLABORATED_WITH: {result.get('collab', 0)}")
            print(f"  AFFILIATED_WITH: {result.get('affil', 0)}")
            print(f"  PARTICIPATED_IN: {result.get('partic', 0)}")
            print(f"  CREATED: {result.get('created', 0)}")
            print(f"  AUTHORED: {result.get('authored', 0)}")

        # 고아 관계 확인
        orphan_result = self.run_query("orphan_check", VALIDATION_QUERIES["orphan_check"])
        if orphan_result and orphan_result.get('orphan_count', 0) > 0:
            print(f"\n⚠ 고아 관계 발견: {orphan_result.get('orphan_count')}개")
        else:
            print("\n✓ 고아 관계 없음")

        # 고립 노드 확인
        isolated_result = self.run_query("isolated_artists", VALIDATION_QUERIES["isolated_artists"])
        isolated_count = isolated_result.get('isolated_count', 0) if isolated_result else 0

        if isolated_count > 0:
            print(f"⚠ 고립된 Artist 노드: {isolated_count}개")
        else:
            print("✓ 모든 Artist 노드 연결됨")

        # 성공 기준 판단
        total_relations = sum(
            result.get(k, 0) for k in ['collab', 'affil', 'partic', 'created', 'authored']
        ) if result else 0

        passed = total_relations >= 50 and isolated_count < 50

        if passed:
            print("\n✓ 검증 게이트 통과")
        else:
            print("\n✗ 검증 게이트 미통과")

        return passed

    def print_summary(self):
        """실행 요약 출력"""
        end_time = datetime.now()
        duration = end_time - self.start_time if self.start_time else None

        print("\n" + "=" * 60)
        print("실행 요약")
        print("=" * 60)

        total_created = 0
        for rel_type, count in self.results.items():
            status = "✓" if count >= 0 else "✗"
            print(f"  {status} {rel_type}: {count if count >= 0 else '실패'}")
            if count > 0:
                total_created += count

        print(f"\n총 생성된 관계: {total_created}개")

        if duration:
            print(f"소요 시간: {duration.total_seconds():.2f}초")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='ARGO 관계 생성 스크립트 v2',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--validate-only', '-v',
        action='store_true',
        help='검증만 실행 (관계 생성 없음)'
    )

    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='사전 검증 건너뛰기'
    )

    parser.add_argument(
        '--types', '-t',
        nargs='+',
        choices=list(RELATIONSHIP_QUERIES.keys()),
        help='생성할 관계 타입 지정'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("ARGO 관계 생성 스크립트 v2")
    print("=" * 60)

    creator = RelationshipCreator()

    # 검증만 실행
    if args.validate_only:
        creator.validate_prerequisites()
        creator.validate_results()
        return

    # 사전 검증
    if not args.skip_validation:
        if not creator.validate_prerequisites():
            print("\n사전 검증 실패. 종료합니다.")
            return

    # 관계 생성
    creator.create_relationships(args.types)

    # 결과 검증
    creator.validate_results()

    # 요약
    creator.print_summary()


if __name__ == "__main__":
    main()
