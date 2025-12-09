"""
Neo4j 연결 상세 진단 스크립트

네트워크 연결은 정상이지만 드라이버 연결이 실패하는 경우 상세 진단
실행: python scripts/diagnose_neo4j_connection.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from app.config import get_settings
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def diagnose_connection():
    """상세 연결 진단"""
    logger.info("=" * 60)
    logger.info("Neo4j 연결 상세 진단")
    logger.info("=" * 60)
    
    settings = get_settings()
    
    logger.info(f"\n1. 환경변수 확인:")
    logger.info(f"   URI: {settings.NEO4J_URI}")
    logger.info(f"   User: {settings.NEO4J_USER}")
    logger.info(f"   Password 길이: {len(settings.NEO4J_PASSWORD) if settings.NEO4J_PASSWORD else 0}")
    
    # 방법 1: neo4j+s:// 직접 연결 시도
    logger.info(f"\n2. 방법 1: neo4j+s:// 직접 연결 시도")
    try:
        driver1 = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            max_connection_pool_size=1,
            connection_timeout=10
        )
        driver1.verify_connectivity()
        logger.info("   ✅ neo4j+s:// 연결 성공!")
        
        # 간단한 쿼리 테스트
        with driver1.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            logger.info(f"   ✅ 쿼리 실행 성공: {record['test']}")
        
        driver1.close()
        return True
    except Exception as e:
        logger.error(f"   ❌ neo4j+s:// 연결 실패: {e}")
        logger.debug(f"   상세 오류:\n{traceback.format_exc()}")
    
    # 방법 2: bolt+s:// 직접 연결 시도 (라우팅 우회)
    logger.info(f"\n3. 방법 2: bolt+s:// 직접 연결 시도 (라우팅 우회)")
    try:
        # neo4j+s://를 bolt+s://로 변환
        bolt_uri = settings.NEO4J_URI.replace("neo4j+s://", "bolt+s://")
        logger.info(f"   변환된 URI: {bolt_uri}")
        
        driver2 = GraphDatabase.driver(
            bolt_uri,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            max_connection_pool_size=1,
            connection_timeout=10
        )
        driver2.verify_connectivity()
        logger.info("   ✅ bolt+s:// 연결 성공!")
        
        # 간단한 쿼리 테스트
        with driver2.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            logger.info(f"   ✅ 쿼리 실행 성공: {record['test']}")
        
        driver2.close()
        logger.warning("   ⚠️  bolt+s://는 직접 연결이지만, neo4j+s://는 클러스터 라우팅 사용")
        return True
    except Exception as e:
        logger.error(f"   ❌ bolt+s:// 연결 실패: {e}")
        logger.debug(f"   상세 오류:\n{traceback.format_exc()}")
    
    # 방법 3: 최소 설정으로 연결 시도
    logger.info(f"\n4. 방법 3: 최소 설정으로 연결 시도")
    try:
        driver3 = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        driver3.verify_connectivity()
        logger.info("   ✅ 최소 설정 연결 성공!")
        driver3.close()
        return True
    except Exception as e:
        logger.error(f"   ❌ 최소 설정 연결 실패: {e}")
        logger.debug(f"   상세 오류:\n{traceback.format_exc()}")
    
    logger.info("\n" + "=" * 60)
    logger.info("진단 결과 요약")
    logger.info("=" * 60)
    logger.error("❌ 모든 연결 방법 실패")
    logger.info("\n가능한 원인:")
    logger.info("1. 인증 정보 오류 (비밀번호 확인 필요)")
    logger.info("2. Neo4j Aura 인스턴스가 중지됨")
    logger.info("3. 인스턴스가 다른 리전에 있거나 접근 불가")
    logger.info("4. Neo4j 드라이버 버전 호환성 문제")
    
    return False


if __name__ == "__main__":
    success = diagnose_connection()
    sys.exit(0 if success else 1)


