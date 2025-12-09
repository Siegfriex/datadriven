"""
ARKO 미술작품 정보 API 데이터 수집기

API 정보:
- Host: api.odcloud.kr
- Base Path: /api
- 엔드포인트: /15083293/v1/uddi:53bdef84-da7b-4635-a6a7-b820b5dc8f86
- 인증: serviceKey 쿼리 파라미터
- 기간: 1988년~2024년
- 신뢰도: 0.95 (공식 데이터 소스)
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


class ArtworkCollector:
    """
    ARKO 미술작품 정보 API 데이터 수집기
    
    공공데이터포털(ODCloud) API 사용
    건축물 미술작품 정보 (1988~2024)
    """
    
    BASE_URL = "https://api.odcloud.kr/api"
    ENDPOINT = "/15083293/v1/uddi:53bdef84-da7b-4635-a6a7-b820b5dc8f86"
    
    def __init__(self, service_key: str):
        """
        Args:
            service_key: serviceKey 쿼리 파라미터 값
        """
        self.service_key = service_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ARGO-DataCollector/1.0"
        })
    
    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def get_artworks_page(
        self, 
        page: int = 1, 
        per_page: int = 100
    ) -> Dict:
        """
        미술작품 목록 페이지 조회
        
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
                logger.error(f"ARKO 작품 API 응답 오류 (상태 코드: {response.status_code})")
                logger.error(f"응답 본문: {response.text[:500]}")
                logger.error(f"요청 URL: {response.url}")
            
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(
                f"ARKO 작품 API: 페이지 {page} 수집 완료 "
                f"(현재: {data.get('currentCount', 0)}, 전체: {data.get('totalCount', 0)})"
            )
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ARKO 작품 API 요청 실패 (page {page}): {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 본문: {e.response.text[:500]}")
            raise
    
    def collect_all(self, max_count: Optional[int] = None) -> List[Dict]:
        """
        전체 미술작품 데이터 수집
        
        Args:
            max_count: 최대 수집 수량 (None이면 전체 수집)
            
        Returns:
            작품 데이터 리스트
        """
        all_artworks = []
        page = 1
        per_page = 100
        
        # 첫 페이지로 전체 개수 확인
        first_page = self.get_artworks_page(page=1, per_page=per_page)
        total_count = first_page.get("totalCount", 0)
        
        logger.info(f"ARKO 작품 API 전체 작품 수: {total_count}개")
        
        # 첫 페이지 데이터 추가
        all_artworks.extend(first_page.get("data", []))
        
        # 나머지 페이지 수집
        total_pages = (total_count + per_page - 1) // per_page
        
        for page in range(2, total_pages + 1):
            if max_count and len(all_artworks) >= max_count:
                break
            
            page_data = self.get_artworks_page(page=page, per_page=per_page)
            all_artworks.extend(page_data.get("data", []))
            
            # Rate Limit 고려 (초당 10회 제한 가정)
            time.sleep(0.1)
            
            logger.info(f"수집 진행: {len(all_artworks)}/{total_count}")
        
        # max_count 제한 적용
        if max_count:
            all_artworks = all_artworks[:max_count]
        
        logger.info(f"ARKO 작품 API 수집 완료: {len(all_artworks)}개")
        return all_artworks
    
    def normalize_artwork_data(self, raw_data: Dict) -> Dict:
        """
        ARKO API 응답 데이터를 ARGO 형식으로 정규화
        
        Args:
            raw_data: ARKO API 원본 데이터
                {
                    "설치일자": "2024-12-31",
                    "지역": "인천/서구",
                    "작품명": "작품명",
                    "작가명": "작가명",
                    "분류": "조각",
                    "건축물명": "건축물명",
                    "건축물주소": "주소",
                    "건축물용도": "공동주택"
                }
        
        Returns:
            정규화된 작품 데이터
        """
        # 설치일자 파싱
        install_date_raw = raw_data.get("설치일자") or ""
        install_date = install_date_raw.strip() if isinstance(install_date_raw, str) else ""
        install_year = None
        if install_date:
            try:
                # YYYY-MM-DD 형식에서 연도 추출
                install_year = int(install_date.split("-")[0])
            except:
                pass
        
        # 지역 파싱 (시/구 분리)
        region_raw = raw_data.get("지역") or ""
        region = region_raw.strip() if isinstance(region_raw, str) else ""
        city = None
        district = None
        if region:
            parts = region.split("/")
            city = parts[0].strip() if len(parts) > 0 else None
            district = parts[1].strip() if len(parts) > 1 else None
        
        # 안전한 문자열 추출 헬퍼
        def safe_str(value, default=""):
            if value is None:
                return default
            return str(value).strip() if isinstance(value, str) else default
        
        return {
            "title": safe_str(raw_data.get("작품명")),
            "artist_name": safe_str(raw_data.get("작가명")),
            "category": safe_str(raw_data.get("분류")) or None,
            "install_date": install_date or None,
            "install_year": install_year,
            "region": region or None,
            "city": city,
            "district": district,
            "building_name": safe_str(raw_data.get("건축물명")) or None,
            "building_address": safe_str(raw_data.get("건축물주소")) or None,
            "building_type": safe_str(raw_data.get("건축물용도")) or None,
            "source": "ARKO",
            "data_source": ["ARKO"],
            "confidence_score": 0.95,
            "collected_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def group_by_artist(self, artworks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        작가별로 작품 그룹화
        
        Args:
            artworks: 작품 데이터 리스트
            
        Returns:
            {작가명: [작품 리스트]} 딕셔너리
        """
        artist_artworks = {}
        
        for artwork in artworks:
            artist_name = artwork.get("artist_name", "").strip()
            if not artist_name:
                continue
            
            if artist_name not in artist_artworks:
                artist_artworks[artist_name] = []
            
            artist_artworks[artist_name].append(artwork)
        
        logger.info(f"작가별 그룹화 완료: {len(artist_artworks)}명의 작가")
        return artist_artworks

