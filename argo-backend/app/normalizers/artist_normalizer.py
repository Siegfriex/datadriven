"""
작가 데이터 정규화 모듈

- 이름 표준화 (한글 + 영문)
- 날짜 정규화 (YYYY-MM-DD)
- 주소 정규화
"""

import re
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ArtistNormalizer:
    """
    작가 데이터 정규화 클래스
    """
    
    @staticmethod
    def normalize_name(name: str, name_en: Optional[str] = None) -> Dict[str, str]:
        """
        이름 표준화
        
        Args:
            name: 한글 이름
            name_en: 영문 이름 (선택)
            
        Returns:
            {"name": "이상훈", "name_en": "Sang-Hoon Lee"}
        """
        # 한글 이름 정규화 (공백 제거)
        name_ko = re.sub(r'\s+', '', name.strip())
        
        # 영문 이름 정규화
        if name_en:
            name_en = name_en.strip()
        else:
            # 영문 이름이 없으면 한글 이름 그대로 사용 (임시)
            name_en = name_ko
        
        return {
            "name": name_ko,
            "name_en": name_en
        }
    
    @staticmethod
    def normalize_birth_year(birth_year: Optional[int]) -> Optional[int]:
        """
        출생 연도 정규화 및 검증
        
        Args:
            birth_year: 출생 연도
            
        Returns:
            정규화된 출생 연도 (1900 ~ 현재 연도)
        """
        if not birth_year:
            return None
        
        current_year = datetime.now().year
        
        # 범위 검증
        if 1900 <= birth_year <= current_year:
            return birth_year
        
        logger.warning(f"비정상적인 출생 연도: {birth_year}")
        return None
    
    @staticmethod
    def normalize_date(date_str: str) -> Optional[str]:
        """
        날짜 정규화 (YYYY-MM-DD)
        
        Args:
            date_str: 날짜 문자열 (다양한 형식)
            
        Returns:
            YYYY-MM-DD 형식 날짜 문자열
        """
        if not date_str:
            return None
        
        # 다양한 날짜 형식 파싱
        patterns = [
            (r'(\d{4})\.(\d{2})\.(\d{2})', r'\1-\2-\3'),
            (r'(\d{4})-(\d{2})-(\d{2})', r'\1-\2-\3'),
            (r'(\d{4})/(\d{2})/(\d{2})', r'\1-\2-\3'),
            (r'(\d{4})(\d{2})(\d{2})', r'\1-\2-\3'),
        ]
        
        for pattern, replacement in patterns:
            match = re.match(pattern, date_str.strip())
            if match:
                normalized = re.sub(pattern, replacement, date_str.strip())
                # 유효성 검증
                try:
                    datetime.strptime(normalized, "%Y-%m-%d")
                    return normalized
                except ValueError:
                    continue
        
        logger.warning(f"날짜 파싱 실패: {date_str}")
        return None
    
    @staticmethod
    def normalize_identifier(artist_id: str) -> Dict[str, str]:
        """
        identifier 필드 생성 (Schema.org PropertyValue 형식)
        
        Args:
            artist_id: 작가 ID
            
        Returns:
            PropertyValue 형식 딕셔너리
        """
        return {
            "@type": "PropertyValue",
            "value": artist_id
        }
    
    @staticmethod
    def normalize_segment_id(genre: Optional[str]) -> Optional[str]:
        """
        장르를 segment_id로 변환
        
        Args:
            genre: 장르명 (예: "회화", "조각", "설치미술")
            
        Returns:
            segment_id (예: "contemporary_painting_KR")
        """
        if not genre:
            return None
        
        # 장르 매핑 (간단 버전, 실제로는 더 정교한 매핑 필요)
        genre_mapping = {
            "회화": "contemporary_painting_KR",
            "조각": "sculpture_KR",
            "설치미술": "installation_KR",
            "미디어아트": "media_art_KR",
            "사진": "photography_KR",
        }
        
        return genre_mapping.get(genre.strip(), "contemporary_KR")

