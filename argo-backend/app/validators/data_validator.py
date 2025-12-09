"""
데이터 검증 모듈 (전처리 단계)

역할:
- Pydantic 검증 전 빠른 실패(fail-fast) 검증 수행
- 기본적인 필수 필드 및 범위 검증
- Pydantic 검증보다 빠르지만 덜 엄격한 검증

주의:
- 데이터 수집 파이프라인에서는 Pydantic 모델 검증을 우선 사용
- 이 클래스는 Pydantic 검증 전 전처리 단계로 사용 가능
"""

from typing import Dict, List, Optional
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """
    데이터 검증 클래스 (전처리 단계)
    
    Pydantic 검증 전 빠른 실패 검증을 수행합니다.
    Pydantic 모델 검증이 더 엄격하고 권장되는 방법입니다.
    """
    
    @staticmethod
    def validate_artist(artist_data: Dict) -> bool:
        """
        작가 데이터 빠른 검증 (전처리 단계)
        
        Pydantic 검증 전 기본적인 검증을 수행합니다.
        더 엄격한 검증이 필요하면 Pydantic 모델을 사용하세요.
        
        Args:
            artist_data: 작가 데이터 딕셔너리
            
        Returns:
            검증 통과 여부
        """
        # 필수 필드 검증
        if not artist_data.get("name"):
            logger.warning("작가 이름이 없습니다")
            return False
        
        # 출생 연도 검증
        birth_year = artist_data.get("birth_year")
        if birth_year:
            current_year = datetime.now().year
            if not (1900 <= birth_year <= current_year):
                logger.warning(f"비정상적인 출생 연도: {birth_year}")
                return False
        
        # 점수 범위 검증 (빠른 실패)
        scores = ["inst_score", "acad_score", "media_score", "network_score", "composite_score"]
        for score_key in scores:
            score_value = artist_data.get(score_key)
            if score_value is not None:
                if not (0 <= score_value <= 100):
                    logger.warning(f"점수 범위 초과: {score_key} = {score_value}")
                    return False
        
        # 신뢰도 점수 검증
        confidence = artist_data.get("composite_confidence") or artist_data.get("confidence_score")
        if confidence is not None:
            if not (0 <= confidence <= 1):
                logger.warning(f"신뢰도 점수 범위 초과: {confidence}")
                return False
        
        return True
    
    @staticmethod
    def validate_batch(artists: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        """
        배치 데이터 빠른 검증 (전처리 단계)
        
        Pydantic 검증 전 기본적인 검증을 수행합니다.
        더 엄격한 검증이 필요하면 Pydantic 모델을 사용하세요.
        
        Args:
            artists: 작가 데이터 리스트
            
        Returns:
            (통과한 데이터, 실패한 데이터)
        """
        passed = []
        failed = []
        
        for artist in artists:
            if DataValidator.validate_artist(artist):
                passed.append(artist)
            else:
                failed.append(artist)
        
        logger.info(f"전처리 검증 완료: 통과 {len(passed)}명, 실패 {len(failed)}명")
        return passed, failed

