"""
Neo4j 연결 테스트 스크립트

Neo4j URI 접근 가능 여부, 인증 정보 유효성, 기본 쿼리 실행 가능 여부 검증
실행: python scripts/test_neo4j_connection.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.services.neo4j_service import neo4j_service
from app.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection():
    """Neo4j 연결 테스트"""
    logger.info("=" * 60)
    logger.info("Neo4j AuraDB Professional 연결 테스트")
    logger.info("=" * 60)
    logger.info("인스턴스 정보:")
    logger.info("  - ID: be57a318")
    logger.info("  - Type: AuraDB Professional")
    logger.info("  - Version: 2025.10")
    logger.info("  - Region: us-central1 (Iowa, USA)")
    logger.info("  - Memory: 1GB, CPU: 1, Storage: 2GB")
    logger.info("  - Graph Analytics: Serverless")
    logger.info("=" * 60)
    
    try:
        # 설정 확인
        settings = get_settings()
        logger.info(f"Neo4j URI: {settings.NEO4J_URI}")
        logger.info(f"Neo4j User: {settings.NEO4J_USER}")
        logger.info(f"Neo4j Password: {'*' * len(settings.NEO4J_PASSWORD) if settings.NEO4J_PASSWORD else 'NOT SET'}")
        
        # URI 형식 검증
        if not settings.NEO4J_URI.startswith(("neo4j://", "neo4j+s://", "bolt://", "bolt+s://")):
            logger.error("❌ URI 형식 오류: neo4j:// 또는 neo4j+s://로 시작해야 함")
            return False
        
        if not settings.NEO4J_URI.startswith("neo4j+s://"):
            logger.warning("⚠️  AuraDB는 neo4j+s:// 형식 권장 (암호화 필수)")
        
        # 드라이버 연결 테스트
        db = get_db()
        driver = db.driver
        
        # 연결 확인
        driver.verify_connectivity()
        logger.info("✅ Neo4j 연결 성공")
        
        # 기본 쿼리 실행 테스트
        test_query = "RETURN 1 as test"
        result = neo4j_service.execute_query(test_query)
        
        if result and result[0].get('test') == 1:
            logger.info("✅ 기본 쿼리 실행 성공")
        else:
            logger.error("❌ 기본 쿼리 실행 실패")
            return False
        
        # Neo4j 버전 확인
        version_query = "CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] as version, edition"
        version_result = neo4j_service.execute_query(version_query)
        
        if version_result:
            logger.info("✅ Neo4j 버전 정보:")
            for comp in version_result:
                logger.info(f"   - {comp.get('name')}: {comp.get('version')} ({comp.get('edition')})")
        
        # GDS 라이브러리 확인
        try:
            gds_query = "CALL gds.version() YIELD version"
            gds_result = neo4j_service.execute_query(gds_query)
            if gds_result:
                logger.info(f"✅ GDS 라이브러리 사용 가능: {gds_result[0].get('version')}")
            else:
                logger.warning("⚠️  GDS 라이브러리 확인 실패 (Enterprise 플랜 필요)")
        except Exception as e:
            logger.warning(f"⚠️  GDS 라이브러리 확인 실패: {e}")
            logger.warning("   GDS는 Neo4j Enterprise 플랜에서만 사용 가능합니다")
        
        logger.info("=" * 60)
        logger.info("✅ 모든 연결 테스트 통과!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ Neo4j 연결 실패")
        logger.error("=" * 60)
        logger.error(f"오류: {e}")
        logger.error("\n해결 방법:")
        logger.error("1. .env 파일의 NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD 확인")
        logger.error("2. Neo4j Aura 인스턴스 상태 확인")
        logger.error("3. 방화벽 설정 확인")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

