"""
환경변수 검증 스크립트

필수 환경변수가 설정되어 있는지 확인
실행: python scripts/verify_env.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_environment():
    """환경변수 검증"""
    logger.info("=" * 60)
    logger.info("환경변수 검증 시작")
    logger.info("=" * 60)
    
    settings = get_settings()
    errors = []
    warnings = []
    
    # 필수 환경변수 검증
    required_vars = {
        "NEO4J_URI": settings.NEO4J_URI,
        "NEO4J_USER": settings.NEO4J_USER,
        "NEO4J_PASSWORD": settings.NEO4J_PASSWORD,
    }
    
    # 선택적 환경변수 (데이터 수집용)
    optional_vars = {
        "ARKO_API_KEY": settings.ARKO_API_KEY,
        "ARKO_SERVICE_KEY": settings.ARKO_SERVICE_KEY,
        "GEMINI_API_KEY": settings.GEMINI_API_KEY,
    }
    
    # 필수 환경변수 검증
    logger.info("\n=== 필수 환경변수 ===")
    for var_name, var_value in required_vars.items():
        if var_value:
            masked_value = "*" * min(len(str(var_value)), 20) if "PASSWORD" in var_name else str(var_value)[:50]
            logger.info(f"✅ {var_name}: {masked_value}")
        else:
            logger.error(f"❌ {var_name}: 설정되지 않음")
            errors.append(var_name)
    
    # 선택적 환경변수 검증
    logger.info("\n=== 선택적 환경변수 (데이터 수집용) ===")
    for var_name, var_value in optional_vars.items():
        if var_value:
            masked_value = "*" * min(len(str(var_value)), 20) if "KEY" in var_name else str(var_value)[:50]
            logger.info(f"✅ {var_name}: {masked_value}")
        else:
            logger.warning(f"⚠️  {var_name}: 설정되지 않음 (데이터 수집 기능 제한)")
            warnings.append(var_name)
    
    # 프로젝트 설정 확인
    logger.info("\n=== 프로젝트 설정 ===")
    logger.info(f"✅ PROJECT_ID: {settings.PROJECT_ID}")
    logger.info(f"✅ ALLOWED_ORIGINS: {len(settings.ALLOWED_ORIGINS)}개")
    
    # 결과 요약
    logger.info("\n" + "=" * 60)
    logger.info("검증 결과 요약")
    logger.info("=" * 60)
    
    if errors:
        logger.error(f"❌ 필수 환경변수 누락: {', '.join(errors)}")
        logger.error("   .env 파일을 확인하고 누락된 환경변수를 설정하세요")
        return False
    
    if warnings:
        logger.warning(f"⚠️  선택적 환경변수 누락: {', '.join(warnings)}")
        logger.warning("   데이터 수집 기능이 제한될 수 있습니다")
    
    logger.info("✅ 모든 필수 환경변수 설정 완료!")
    logger.info("=" * 60)
    return True


if __name__ == "__main__":
    success = verify_environment()
    sys.exit(0 if success else 1)


