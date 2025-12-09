"""
데이터 품질 검증 스크립트

점수 범위 검증, 좌표 범위 검증, 필수 필드 누락 확인, 데이터 소스 메타데이터 확인
실행: python scripts/verify_data_quality.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_score_ranges():
    """점수 범위 검증 (0-100)"""
    logger.info("\n=== 점수 범위 검증 ===")
    try:
        query = """
        MATCH (a:Artist)
        WHERE a.inst_score < 0 OR a.inst_score > 100
           OR a.acad_score < 0 OR a.acad_score > 100
           OR a.media_score < 0 OR a.media_score > 100
           OR a.network_score < 0 OR a.network_score > 100
           OR a.composite_score < 0 OR a.composite_score > 100
        RETURN a.id AS id, a.name AS name,
               a.inst_score AS inst, a.acad_score AS acad,
               a.media_score AS media, a.network_score AS network,
               a.composite_score AS composite
        LIMIT 10
        """
        invalid = neo4j_service.execute_query(query)
        
        if invalid:
            logger.error(f"❌ 범위를 벗어난 점수 발견: {len(invalid)}개")
            for item in invalid[:5]:
                logger.error(f"   - {item.get('name')}: inst={item.get('inst')}, acad={item.get('acad')}, "
                           f"media={item.get('media')}, network={item.get('network')}, composite={item.get('composite')}")
            return False
        
        logger.info("✅ 모든 점수가 0-100 범위 내")
        return True
        
    except Exception as e:
        logger.error(f"❌ 점수 범위 검증 실패: {e}")
        return False


def verify_coordinate_ranges():
    """좌표 범위 검증"""
    logger.info("\n=== 좌표 범위 검증 ===")
    try:
        query = """
        MATCH (a:Artist)
        WHERE a.coordinates_3d IS NOT NULL
        WITH a,
             a.coordinates_3d.x AS x,
             a.coordinates_3d.y AS y,
             a.coordinates_3d.z AS z,
             a.coordinates_3d.radius AS radius
        WHERE x < -100 OR x > 100
           OR y < -100 OR y > 100
           OR z < -100 OR z > 100
           OR radius < 0 OR radius > 100
        RETURN a.id AS id, a.name AS name,
               a.coordinates_3d AS coords
        LIMIT 10
        """
        invalid = neo4j_service.execute_query(query)
        
        if invalid:
            logger.error(f"❌ 범위를 벗어난 좌표 발견: {len(invalid)}개")
            for item in invalid[:5]:
                logger.error(f"   - {item.get('name')}: {item.get('coords')}")
            return False
        
        logger.info("✅ 모든 좌표가 유효한 범위 내")
        return True
        
    except Exception as e:
        logger.error(f"❌ 좌표 범위 검증 실패: {e}")
        return False


def verify_required_fields():
    """필수 필드 누락 확인"""
    logger.info("\n=== 필수 필드 누락 확인 ===")
    try:
        # Artist 노드 필수 필드
        query = """
        MATCH (a:Artist)
        WHERE a.id IS NULL 
           OR a.name IS NULL
           OR a.inst_score IS NULL
           OR a.acad_score IS NULL
           OR a.media_score IS NULL
           OR a.network_score IS NULL
           OR a.composite_score IS NULL
        RETURN a.id AS id, a.name AS name,
               a.inst_score IS NULL AS missing_inst,
               a.acad_score IS NULL AS missing_acad,
               a.media_score IS NULL AS missing_media,
               a.network_score IS NULL AS missing_network,
               a.composite_score IS NULL AS missing_composite
        LIMIT 10
        """
        missing = neo4j_service.execute_query(query)
        
        if missing:
            logger.warning(f"⚠️  필수 필드 누락: {len(missing)}개")
            for item in missing[:5]:
                missing_fields = []
                if item.get('missing_inst'): missing_fields.append('inst_score')
                if item.get('missing_acad'): missing_fields.append('acad_score')
                if item.get('missing_media'): missing_fields.append('media_score')
                if item.get('missing_network'): missing_fields.append('network_score')
                if item.get('missing_composite'): missing_fields.append('composite_score')
                logger.warning(f"   - {item.get('name')}: 누락된 필드 {', '.join(missing_fields)}")
        else:
            logger.info("✅ 모든 Artist 노드에 필수 필드 존재")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 필수 필드 검증 실패: {e}")
        return False


def verify_data_sources():
    """데이터 소스 메타데이터 확인"""
    logger.info("\n=== 데이터 소스 메타데이터 확인 ===")
    try:
        query = """
        MATCH (a:Artist)
        WHERE a.metadata IS NOT NULL
        WITH a.metadata.data_source AS sources, count(a) AS count
        RETURN sources, count
        ORDER BY count DESC
        """
        sources = neo4j_service.execute_query(query)
        
        if sources:
            logger.info("데이터 소스 분포:")
            for src in sources:
                src_list = src.get('sources', [])
                if isinstance(src_list, list):
                    src_str = ', '.join(src_list)
                else:
                    src_str = str(src_list)
                logger.info(f"   - {src_str}: {src.get('count')}개")
        else:
            logger.warning("⚠️  데이터 소스 메타데이터 없음")
        
        # 메타데이터 없는 노드 확인
        query_no_meta = """
        MATCH (a:Artist)
        WHERE a.metadata IS NULL
        RETURN count(a) AS count
        """
        result = neo4j_service.find_one(query_no_meta)
        no_meta_count = result.get('count', 0) if result else 0
        
        if no_meta_count > 0:
            logger.warning(f"⚠️  메타데이터 없는 노드: {no_meta_count}개")
        else:
            logger.info("✅ 모든 노드에 메타데이터 존재")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 데이터 소스 메타데이터 검증 실패: {e}")
        return False


def verify_composite_confidence():
    """composite_confidence 범위 검증 (0-1)"""
    logger.info("\n=== Composite Confidence 범위 검증 ===")
    try:
        query = """
        MATCH (a:Artist)
        WHERE a.composite_confidence IS NOT NULL
          AND (a.composite_confidence < 0 OR a.composite_confidence > 1)
        RETURN a.id AS id, a.name AS name, a.composite_confidence AS confidence
        LIMIT 10
        """
        invalid = neo4j_service.execute_query(query)
        
        if invalid:
            logger.error(f"❌ 범위를 벗어난 confidence 발견: {len(invalid)}개")
            for item in invalid[:5]:
                logger.error(f"   - {item.get('name')}: {item.get('confidence')}")
            return False
        
        logger.info("✅ 모든 composite_confidence가 0-1 범위 내")
        return True
        
    except Exception as e:
        logger.error(f"❌ composite_confidence 범위 검증 실패: {e}")
        return False


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("데이터 품질 검증 시작")
    logger.info("=" * 60)
    
    results = []
    
    results.append(("점수 범위", verify_score_ranges()))
    results.append(("좌표 범위", verify_coordinate_ranges()))
    results.append(("필수 필드", verify_required_fields()))
    results.append(("데이터 소스 메타데이터", verify_data_sources()))
    results.append(("Composite Confidence 범위", verify_composite_confidence()))
    
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


