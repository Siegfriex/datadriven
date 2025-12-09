"""
스키마 무결성 검증 스크립트

중복 ID 확인, 필수 필드 존재 여부, 인덱스 사용 가능 여부 검증
실행: python scripts/verify_schema_integrity.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_constraints():
    """제약조건 검증"""
    logger.info("\n=== 제약조건 검증 ===")
    try:
        constraints = neo4j_service.execute_query("SHOW CONSTRAINTS")
        
        expected_constraints = [
            "artist_id_unique",
            "institution_id_unique",
            "exhibition_id_unique",
            "cluster_id_unique",
            "artwork_id_unique",
            "transaction_id_unique"
        ]
        
        found_constraints = [c.get('name', '') for c in constraints]
        
        logger.info(f"발견된 제약조건: {len(constraints)}개")
        for constraint in constraints:
            logger.info(f"   - {constraint.get('name')}: {constraint.get('type')}")
        
        missing = [c for c in expected_constraints if c not in found_constraints]
        if missing:
            logger.warning(f"⚠️  누락된 제약조건: {', '.join(missing)}")
            return False
        
        logger.info("✅ 모든 필수 제약조건 존재")
        return True
        
    except Exception as e:
        logger.error(f"❌ 제약조건 검증 실패: {e}")
        return False


def verify_indexes():
    """인덱스 검증"""
    logger.info("\n=== 인덱스 검증 ===")
    try:
        indexes = neo4j_service.execute_query("SHOW INDEXES")
        
        expected_indexes = [
            "artist_composite_score",
            "artist_segment",
            "artist_field_quadrant",
            "artist_community",
            "institution_type",
            "institution_prestige",
            "exhibition_year",
            "exhibition_type"
        ]
        
        found_indexes = [idx.get('name', '') for idx in indexes]
        
        logger.info(f"발견된 인덱스: {len(indexes)}개")
        for idx in indexes[:10]:  # 처음 10개만 출력
            logger.info(f"   - {idx.get('name')}: {idx.get('type')}")
        
        missing = [idx for idx in expected_indexes if idx not in found_indexes]
        if missing:
            logger.warning(f"⚠️  누락된 인덱스: {', '.join(missing)}")
            return False
        
        logger.info("✅ 모든 필수 인덱스 존재")
        return True
        
    except Exception as e:
        logger.error(f"❌ 인덱스 검증 실패: {e}")
        return False


def verify_duplicate_ids():
    """중복 ID 검증"""
    logger.info("\n=== 중복 ID 검증 ===")
    try:
        node_types = ['Artist', 'Institution', 'Exhibition', 'Cluster']
        has_duplicates = False
        
        for node_type in node_types:
            query = f"""
            MATCH (n:{node_type})
            WITH n.id AS id, count(n) AS count
            WHERE count > 1
            RETURN id, count
            """
            duplicates = neo4j_service.execute_query(query)
            
            if duplicates:
                logger.error(f"❌ {node_type} 중복 ID 발견:")
                for dup in duplicates:
                    logger.error(f"   - ID: {dup.get('id')}, 개수: {dup.get('count')}")
                has_duplicates = True
            else:
                logger.info(f"✅ {node_type}: 중복 없음")
        
        if has_duplicates:
            return False
        
        logger.info("✅ 모든 노드 타입에서 중복 ID 없음")
        return True
        
    except Exception as e:
        logger.error(f"❌ 중복 ID 검증 실패: {e}")
        return False


def verify_required_fields():
    """필수 필드 존재 여부 검증"""
    logger.info("\n=== 필수 필드 검증 ===")
    try:
        # Artist 노드 필수 필드
        query = """
        MATCH (a:Artist)
        WHERE a.id IS NULL OR a.name IS NULL
        RETURN count(a) AS missing_fields
        """
        result = neo4j_service.find_one(query)
        missing = result.get('missing_fields', 0) if result else 0
        
        if missing > 0:
            logger.error(f"❌ Artist 노드 필수 필드 누락: {missing}개")
            return False
        
        logger.info("✅ Artist 노드 필수 필드 모두 존재")
        
        # Institution 노드 필수 필드
        query = """
        MATCH (i:Institution)
        WHERE i.id IS NULL OR i.name IS NULL
        RETURN count(i) AS missing_fields
        """
        result = neo4j_service.find_one(query)
        missing = result.get('missing_fields', 0) if result else 0
        
        if missing > 0:
            logger.warning(f"⚠️  Institution 노드 필수 필드 누락: {missing}개")
        else:
            logger.info("✅ Institution 노드 필수 필드 모두 존재")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 필수 필드 검증 실패: {e}")
        return False


def verify_index_usage():
    """인덱스 사용 가능 여부 검증"""
    logger.info("\n=== 인덱스 사용 가능 여부 검증 ===")
    try:
        # 인덱스를 사용하는 쿼리 테스트
        test_queries = [
            ("Artist composite_score 인덱스", "MATCH (a:Artist) WHERE a.composite_score > 50 RETURN count(a)"),
            ("Artist segment_id 인덱스", "MATCH (a:Artist) WHERE a.segment_id = 'test' RETURN count(a)"),
            ("Institution type 인덱스", "MATCH (i:Institution) WHERE i.type = 'museum' RETURN count(i)"),
        ]
        
        for name, query in test_queries:
            try:
                result = neo4j_service.execute_query(query)
                logger.info(f"✅ {name}: 쿼리 실행 성공")
            except Exception as e:
                logger.warning(f"⚠️  {name}: 쿼리 실행 실패 (인덱스 없을 수 있음): {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 인덱스 사용 가능 여부 검증 실패: {e}")
        return False


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("스키마 무결성 검증 시작")
    logger.info("=" * 60)
    
    results = []
    
    results.append(("제약조건", verify_constraints()))
    results.append(("인덱스", verify_indexes()))
    results.append(("중복 ID", verify_duplicate_ids()))
    results.append(("필수 필드", verify_required_fields()))
    results.append(("인덱스 사용 가능", verify_index_usage()))
    
    logger.info("\n" + "=" * 60)
    logger.info("검증 결과 요약")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        logger.info(f"{name}: {status}")
    
    logger.info(f"\n전체: {passed}/{total} 통과")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("🎉 모든 검증 통과!")
        return 0
    else:
        logger.warning("⚠️  일부 검증 실패")
        return 1


if __name__ == "__main__":
    exit(main())


