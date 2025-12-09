"""
관계 생성 스크립트

COLLABORATED_WITH, AFFILIATED_WITH, PARTICIPATED_IN 관계 생성
실행: python scripts/create_relationships.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service
from app.config import get_settings
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_collaboration_relationships():
    """KCI 공동저자 관계 생성 (COLLABORATED_WITH)"""
    logger.info("\n=== COLLABORATED_WITH 관계 생성 ===")
    
    try:
        # KCI 논문 데이터에서 공동저자 관계 추출
        # 실제 구현에서는 KCI collector에서 수집한 논문 데이터를 사용해야 함
        # 여기서는 Neo4j에 이미 저장된 논문 데이터나 작가 메타데이터에서 추출
        
        # 예시: 작가의 metadata에 coauthors 정보가 있다고 가정
        query = """
        MATCH (a1:Artist)
        WHERE a1.metadata IS NOT NULL
          AND a1.metadata.coauthors IS NOT NULL
        UNWIND a1.metadata.coauthors AS coauthor_name
        MATCH (a2:Artist)
        WHERE a2.name = coauthor_name
           OR a2.alternateName = coauthor_name
           OR a2.alternativeName = coauthor_name
        WITH a1, a2, count(*) AS collaboration_count
        WHERE a1.id <> a2.id
        MERGE (a1)-[r:COLLABORATED_WITH]->(a2)
        ON CREATE SET 
            r.strength = 1,
            r.first_collaboration_year = coalesce(a1.metadata.first_paper_year, datetime().year),
            r.collaboration_count = collaboration_count,
            r.created_at = datetime()
        ON MATCH SET
            r.collaboration_count = r.collaboration_count + collaboration_count,
            r.updated_at = datetime()
        RETURN count(r) AS created_count
        """
        
        result = neo4j_service.find_one(query)
        created_count = result.get('created_count', 0) if result else 0
        
        if created_count > 0:
            logger.info(f"✅ COLLABORATED_WITH 관계 생성: {created_count}개")
        else:
            logger.warning("⚠️  COLLABORATED_WITH 관계 생성 없음 (공동저자 데이터 없음)")
        
        return created_count > 0
        
    except Exception as e:
        logger.error(f"❌ COLLABORATED_WITH 관계 생성 실패: {e}")
        return False


def create_affiliation_relationships():
    """작가-기관 소속 관계 생성 (AFFILIATED_WITH)"""
    logger.info("\n=== AFFILIATED_WITH 관계 생성 ===")
    
    try:
        # 작가의 metadata에서 소속 기관 정보 추출
        query = """
        MATCH (a:Artist)
        WHERE a.metadata IS NOT NULL
          AND a.metadata.affiliations IS NOT NULL
        UNWIND a.metadata.affiliations AS affiliation_data
        MATCH (i:Institution)
        WHERE i.name = affiliation_data.name
           OR i.name_en = affiliation_data.name
        MERGE (a)-[r:AFFILIATED_WITH]->(i)
        ON CREATE SET
            r.role = coalesce(affiliation_data.role, 'member'),
            r.start_year = affiliation_data.start_year,
            r.end_year = affiliation_data.end_year,
            r.is_current = coalesce(affiliation_data.is_current, false),
            r.created_at = datetime()
        ON MATCH SET
            r.updated_at = datetime()
        RETURN count(r) AS created_count
        """
        
        result = neo4j_service.find_one(query)
        created_count = result.get('created_count', 0) if result else 0
        
        if created_count > 0:
            logger.info(f"✅ AFFILIATED_WITH 관계 생성: {created_count}개")
        else:
            logger.warning("⚠️  AFFILIATED_WITH 관계 생성 없음 (소속 기관 데이터 없음)")
        
        return True  # 데이터가 없어도 성공으로 간주
        
    except Exception as e:
        logger.error(f"❌ AFFILIATED_WITH 관계 생성 실패: {e}")
        return False


def create_participation_relationships():
    """작가-전시 참여 관계 생성 (PARTICIPATED_IN)"""
    logger.info("\n=== PARTICIPATED_IN 관계 생성 ===")
    
    try:
        # 작가의 metadata에서 전시 참여 정보 추출
        query = """
        MATCH (a:Artist)
        WHERE a.metadata IS NOT NULL
          AND a.metadata.exhibitions IS NOT NULL
        UNWIND a.metadata.exhibitions AS exhibition_data
        MATCH (e:Exhibition)
        WHERE e.id = exhibition_data.id
           OR e.title = exhibition_data.title
        MERGE (a)-[r:PARTICIPATED_IN]->(e)
        ON CREATE SET
            r.role = coalesce(exhibition_data.role, 'participant'),
            r.year = exhibition_data.year,
            r.created_at = datetime()
        ON MATCH SET
            r.updated_at = datetime()
        RETURN count(r) AS created_count
        """
        
        result = neo4j_service.find_one(query)
        created_count = result.get('created_count', 0) if result else 0
        
        if created_count > 0:
            logger.info(f"✅ PARTICIPATED_IN 관계 생성: {created_count}개")
        else:
            logger.warning("⚠️  PARTICIPATED_IN 관계 생성 없음 (전시 참여 데이터 없음)")
        
        return True  # 데이터가 없어도 성공으로 간주
        
    except Exception as e:
        logger.error(f"❌ PARTICIPATED_IN 관계 생성 실패: {e}")
        return False


def verify_relationships():
    """생성된 관계 검증"""
    logger.info("\n=== 관계 검증 ===")
    
    try:
        # 각 관계 타입별 카운트
        queries = {
            "COLLABORATED_WITH": "MATCH ()-[r:COLLABORATED_WITH]->() RETURN count(r) AS count",
            "AFFILIATED_WITH": "MATCH ()-[r:AFFILIATED_WITH]->() RETURN count(r) AS count",
            "PARTICIPATED_IN": "MATCH ()-[r:PARTICIPATED_IN]->() RETURN count(r) AS count"
        }
        
        results = {}
        for rel_type, query in queries.items():
            result = neo4j_service.find_one(query)
            count = result.get('count', 0) if result else 0
            results[rel_type] = count
            logger.info(f"   - {rel_type}: {count}개")
        
        # 고아 관계 확인 (참조된 노드가 없는 관계)
        orphan_query = """
        MATCH (a:Artist)-[r:COLLABORATED_WITH]->(b:Artist)
        WHERE NOT EXISTS((b))
        RETURN count(r) AS orphan_count
        """
        orphan_result = neo4j_service.find_one(orphan_query)
        orphan_count = orphan_result.get('orphan_count', 0) if orphan_result else 0
        
        if orphan_count > 0:
            logger.warning(f"⚠️  고아 관계 발견: {orphan_count}개")
        else:
            logger.info("✅ 고아 관계 없음")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 관계 검증 실패: {e}")
        return False


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("관계 생성 시작")
    logger.info("=" * 60)
    
    results = []
    
    results.append(("COLLABORATED_WITH", create_collaboration_relationships()))
    results.append(("AFFILIATED_WITH", create_affiliation_relationships()))
    results.append(("PARTICIPATED_IN", create_participation_relationships()))
    results.append(("관계 검증", verify_relationships()))
    
    logger.info("\n" + "=" * 60)
    logger.info("관계 생성 결과 요약")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        logger.info(f"{name}: {status}")
    
    logger.info(f"\n전체: {passed}/{total} 성공")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("🎉 모든 관계 생성 완료!")
        return 0
    else:
        logger.warning("⚠️  일부 관계 생성 실패")
        return 1


if __name__ == "__main__":
    exit(main())


