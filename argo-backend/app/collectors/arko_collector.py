"""
ARKO (한국문화예술위원회) API 데이터 수집기

API 정보:
- Host: api.odcloud.kr
- Base Path: /api
- 엔드포인트: /15046037/v1/uddi:0688d256-3e27-4714-b5a6-c67c2b0e34e3
- 인증: Authorization 헤더 + serviceKey 쿼리 파라미터
- 신뢰도: 0.95 (최고)
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0):
    """지수 백오프 재시도 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"{func.__name__} 최대 재시도 횟수 초과: {e}")
                        raise
                    
                    wait_time = backoff_factor ** retries
                    logger.warning(f"{func.__name__} 실패 (재시도 {retries}/{max_retries}): {e}. {wait_time}초 대기")
                    time.sleep(wait_time)
            raise RuntimeError("재시도 로직 오류")
        return wrapper
    return decorator


class ARKOCollector:
    """
    ARKO (한국문화예술위원회) API 데이터 수집기
    
    공공데이터포털(ODCloud) API 사용
    """
    
    BASE_URL = "https://api.odcloud.kr/api"
    ENDPOINT = "/15046037/v1/uddi:0688d256-3e27-4714-b5a6-c67c2b0e34e3"
    
    def __init__(self, api_key: str, service_key: str):
        """
        Args:
            api_key: Authorization 헤더 값 (선택사항, 공공데이터포털은 주로 serviceKey만 사용)
            service_key: serviceKey 쿼리 파라미터 값 (필수)
        """
        self.api_key = api_key
        self.service_key = service_key
        self.session = requests.Session()
        # 공공데이터포털 API는 Authorization 헤더가 선택사항일 수 있음
        if api_key:
            self.session.headers.update({
                "Authorization": api_key,
            })
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ARGO-DataCollector/1.0"
        })
    
    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def get_artists_page(
        self, 
        page: int = 1, 
        per_page: int = 100
    ) -> Dict:
        """
        작가 목록 페이지 조회
        
        Args:
            page: 페이지 번호 (1부터 시작)
            per_page: 페이지당 항목 수 (기본 10, 최대 100)
            
        Returns:
            API 응답 딕셔너리
            {
                "page": int,
                "perPage": int,
                "totalCount": int,
                "currentCount": int,
                "matchCount": int,
                "data": List[Dict]
            }
        """
        url = f"{self.BASE_URL}{self.ENDPOINT}"
        params = {
            "page": page,
            "perPage": min(per_page, 100),  # 최대 100
            "serviceKey": self.service_key,
            "returnType": "JSON"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            # 에러 응답 상세 확인
            if response.status_code != 200:
                logger.error(f"ARKO API 응답 오류 (상태 코드: {response.status_code})")
                logger.error(f"응답 본문: {response.text[:500]}")
                logger.error(f"요청 URL: {response.url}")
            
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(
                f"ARKO API: 페이지 {page} 수집 완료 "
                f"(현재: {data.get('currentCount', 0)}, 전체: {data.get('totalCount', 0)})"
            )
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ARKO API 요청 실패 (page {page}): {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 본문: {e.response.text[:500]}")
            raise
    
    def collect_all(self, max_count: Optional[int] = None) -> List[Dict]:
        """
        전체 작가 데이터 수집
        
        Args:
            max_count: 최대 수집 수량 (None이면 전체 수집)
            
        Returns:
            작가 데이터 리스트
        """
        all_artists = []
        page = 1
        per_page = 100
        
        # 첫 페이지로 전체 개수 확인
        first_page = self.get_artists_page(page=1, per_page=per_page)
        total_count = first_page.get("totalCount", 0)
        
        logger.info(f"ARKO API 전체 작가 수: {total_count}명")
        
        # 첫 페이지 데이터 추가
        all_artists.extend(first_page.get("data", []))
        
        # 나머지 페이지 수집
        total_pages = (total_count + per_page - 1) // per_page
        
        for page in range(2, total_pages + 1):
            if max_count and len(all_artists) >= max_count:
                break
            
            page_data = self.get_artists_page(page=page, per_page=per_page)
            all_artists.extend(page_data.get("data", []))
            
            # Rate Limit 고려 (초당 10회 제한 가정)
            time.sleep(0.1)
            
            logger.info(f"수집 진행: {len(all_artists)}/{total_count}")
        
        # max_count 제한 적용
        if max_count:
            all_artists = all_artists[:max_count]
        
        logger.info(f"ARKO API 수집 완료: {len(all_artists)}명")
        return all_artists
    
    def normalize_artist_data(self, raw_data: Dict) -> Dict:
        """
        ARKO API 응답 데이터를 ARGO 형식으로 정규화
        
        Args:
            raw_data: ARKO API 원본 데이터
                {
                    "이름": "작가명",
                    "이형표기": "영문명",
                    "분야": "분야명"
                }
        
        Returns:
            정규화된 작가 데이터
        """
        return {
            "name": raw_data.get("이름", "").strip(),
            "name_ko": raw_data.get("이름", "").strip(),
            "alternateName": raw_data.get("이형표기", "").strip() or None,
            "genre": raw_data.get("분야", "").strip() or None,
            "source": "ARKO",
            "data_source": ["ARKO"],
            "confidence_score": 0.95,  # ARKO 신뢰도
            "collected_at": datetime.utcnow().isoformat() + "Z"
        }

