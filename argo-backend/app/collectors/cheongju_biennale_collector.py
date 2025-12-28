"""
청주공예비엔날레 출품작 기반 공예작가/작품 데이터 수집기

API 정보:
- Host: apis.data.go.kr
- Base Path: /5710000/benlService
- 엔드포인트:
  - 작가별 참여 작품 상세 조회: /getArtistWorkList
  - 공모전 입상별 작가 상세 조회: /getAwardArtistList
  - 국가별 작품,공모전 입상작 조회: /getCountryWorkList
  - 작품 이미지 상세 조회: /getWorkImageList
  - 행사별 참여 작가,작품 통계 조회: /getEventStatList
  - 기법,재질,부문별 작가 상세 조회: /getTechniqueArtistList
- 인증: serviceKey 쿼리 파라미터
- 데이터 형식: JSON, XML
- 신뢰도: 0.90 (공식 비엔날레 데이터)
- 업데이트 주기: 비정기 (행사 개최 시)
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


class CheongjuBiennaleCollector:
    """
    청주공예비엔날레 출품작 기반 공예작가/작품 데이터 수집기
    
    공공데이터포털 API 사용
    충청북도 청주시에서 제공하는 공예비엔날레 데이터
    """
    
    BASE_URL = "https://apis.data.go.kr/5710000/benlService"
    
    # 주요 엔드포인트
    ARTIST_WORK_ENDPOINT = "/getArtistWorkList"  # 작가별 참여 작품 상세 조회
    AWARD_ARTIST_ENDPOINT = "/getAwardArtistList"  # 공모전 입상별 작가 상세 조회
    COUNTRY_WORK_ENDPOINT = "/getCountryWorkList"  # 국가별 작품,공모전 입상작 조회
    WORK_IMAGE_ENDPOINT = "/getWorkImageList"  # 작품 이미지 상세 조회
    EVENT_STAT_ENDPOINT = "/getEventStatList"  # 행사별 참여 작가,작품 통계 조회
    TECHNIQUE_ARTIST_ENDPOINT = "/getTechniqueArtistList"  # 기법,재질,부문별 작가 상세 조회
    
    def __init__(self, service_key: str):
        """
        Args:
            service_key: serviceKey 쿼리 파라미터 값 (필수)
        """
        self.service_key = service_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ARGO-DataCollector/1.0"
        })
    
    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def get_artist_works(
        self,
        artist_name_ko: Optional[str] = None,
        artist_name_en: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 100
    ) -> Dict:
        """
        작가별 참여 작품 상세 조회
        
        Args:
            artist_name_ko: 작가명(국문)
            artist_name_en: 작가명(영문)
            page_no: 페이지 번호
            num_of_rows: 페이지당 항목 수
            
        Returns:
            API 응답 딕셔너리
        """
        url = f"{self.BASE_URL}{self.ARTIST_WORK_ENDPOINT}"
        params = {
            "serviceKey": self.service_key,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
            "resultType": "json"
        }
        
        if artist_name_ko:
            params["artistNameKo"] = artist_name_ko
        if artist_name_en:
            params["artistNameEn"] = artist_name_en
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"청주공예비엔날레 API 응답 오류 (상태 코드: {response.status_code})")
                logger.error(f"응답 본문: {response.text[:500]}")
                logger.error(f"요청 URL: {response.url}")
            
            response.raise_for_status()
            
            data = response.json()
            
            # 응답 구조 확인 및 처리
            if "response" in data:
                body = data["response"].get("body", {})
                items = body.get("items", [])
                total_count = body.get("totalCount", 0)
                
                logger.info(
                    f"청주공예비엔날레 API: 작가별 작품 조회 완료 "
                    f"(현재: {len(items)}, 전체: {total_count})"
                )
                
                return {
                    "items": items if isinstance(items, list) else [],
                    "totalCount": total_count,
                    "pageNo": page_no,
                    "numOfRows": num_of_rows
                }
            
            return {"items": [], "totalCount": 0, "pageNo": page_no, "numOfRows": num_of_rows}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"청주공예비엔날레 API 요청 실패: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 본문: {e.response.text[:500]}")
            raise
    
    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def get_event_statistics(
        self,
        event_name_ko: Optional[str] = None,
        event_name_en: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 100
    ) -> Dict:
        """
        행사별 참여 작가,작품 통계 조회
        
        Args:
            event_name_ko: 행사명(국문)
            event_name_en: 행사명(영문)
            page_no: 페이지 번호
            num_of_rows: 페이지당 항목 수
            
        Returns:
            API 응답 딕셔너리
        """
        url = f"{self.BASE_URL}{self.EVENT_STAT_ENDPOINT}"
        params = {
            "serviceKey": self.service_key,
            "pageNo": page_no,
            "num_of_rows": num_of_rows,
            "resultType": "json"
        }
        
        if event_name_ko:
            params["eventNameKo"] = event_name_ko
        if event_name_en:
            params["eventNameEn"] = event_name_en
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"청주공예비엔날레 API 응답 오류 (상태 코드: {response.status_code})")
                logger.error(f"응답 본문: {response.text[:500]}")
            
            response.raise_for_status()
            
            data = response.json()
            
            # 응답 구조 확인 및 처리
            if "response" in data:
                body = data["response"].get("body", {})
                items = body.get("items", [])
                total_count = body.get("totalCount", 0)
                
                logger.info(
                    f"청주공예비엔날레 API: 행사별 통계 조회 완료 "
                    f"(현재: {len(items)}, 전체: {total_count})"
                )
                
                return {
                    "items": items if isinstance(items, list) else [],
                    "totalCount": total_count,
                    "pageNo": page_no,
                    "numOfRows": num_of_rows
                }
            
            return {"items": [], "totalCount": 0, "pageNo": page_no, "numOfRows": num_of_rows}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"청주공예비엔날레 API 요청 실패: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 본문: {e.response.text[:500]}")
            raise
    
    def collect_all_artist_works(
        self,
        max_count: Optional[int] = None
    ) -> List[Dict]:
        """
        전체 작가별 작품 데이터 수집
        
        Args:
            max_count: 최대 수집 수량 (None이면 전체 수집)
            
        Returns:
            작가별 작품 데이터 리스트
        """
        all_works = []
        page = 1
        per_page = 100
        
        # 첫 페이지로 전체 개수 확인
        first_page = self.get_artist_works(page_no=1, num_of_rows=per_page)
        total_count = first_page.get("totalCount", 0)
        
        logger.info(f"청주공예비엔날레 API 전체 작품 수: {total_count}개")
        
        # 첫 페이지 데이터 추가
        all_works.extend(first_page.get("items", []))
        
        # 나머지 페이지 수집
        total_pages = (total_count + per_page - 1) // per_page
        
        for page in range(2, total_pages + 1):
            if max_count and len(all_works) >= max_count:
                break
            
            page_data = self.get_artist_works(page_no=page, num_of_rows=per_page)
            all_works.extend(page_data.get("items", []))
            
            # Rate Limit 고려
            time.sleep(0.1)
            
            logger.info(f"수집 진행: {len(all_works)}/{total_count}")
        
        # max_count 제한 적용
        if max_count:
            all_works = all_works[:max_count]
        
        logger.info(f"청주공예비엔날레 API 수집 완료: {len(all_works)}개 작품")
        return all_works
    
    def normalize_artist_work_data(self, raw_data: Dict) -> Dict:
        """
        청주공예비엔날레 API 응답 데이터를 ARGO 형식으로 정규화
        
        Args:
            raw_data: 청주공예비엔날레 API 원본 데이터
            
        Returns:
            정규화된 작가-작품 데이터
        """
        # 안전한 값 추출 헬퍼
        def safe_str(value, default=""):
            if value is None:
                return default
            return str(value).strip() if isinstance(value, str) else str(value)
        
        def safe_int(value, default=0):
            try:
                return int(value) if value is not None else default
            except:
                return default
        
        return {
            # 작가 정보
            "artist_name_ko": safe_str(raw_data.get("artistNameKo", "")),
            "artist_name_en": safe_str(raw_data.get("artistNameEn", "")),
            "artist_country": safe_str(raw_data.get("artistCountry", "")),
            
            # 작품 정보
            "work_name_ko": safe_str(raw_data.get("workNameKo", "")),
            "work_name_en": safe_str(raw_data.get("workNameEn", "")),
            "work_year": safe_int(raw_data.get("workYear")),
            "work_technique": safe_str(raw_data.get("workTechnique", "")),
            "work_material": safe_str(raw_data.get("workMaterial", "")),
            "work_category": safe_str(raw_data.get("workCategory", "")),
            
            # 비엔날레 정보
            "event_name_ko": safe_str(raw_data.get("eventNameKo", "")),
            "event_name_en": safe_str(raw_data.get("eventNameEn", "")),
            "event_year": safe_int(raw_data.get("eventYear")),
            "award_name": safe_str(raw_data.get("awardName", "")),
            
            # 이미지 정보
            "work_image_url": safe_str(raw_data.get("workImageUrl", "")),
            
            # 메타데이터
            "source": "CHEONGJU_BIENNALE",
            "data_source": ["CHEONGJU_BIENNALE"],
            "confidence_score": 0.90,  # 공식 비엔날레 데이터
            "collected_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def group_by_artist(self, works: List[Dict]) -> Dict[str, List[Dict]]:
        """
        작가별로 작품 그룹화
        
        Args:
            works: 정규화된 작품 데이터 리스트
            
        Returns:
            {작가명: [작품 리스트]} 딕셔너리
        """
        artist_works = {}
        
        for work in works:
            artist_name = work.get("artist_name_ko", "").strip()
            if not artist_name:
                artist_name = work.get("artist_name_en", "").strip()
            
            if not artist_name:
                continue
            
            if artist_name not in artist_works:
                artist_works[artist_name] = []
            
            artist_works[artist_name].append(work)
        
        logger.info(f"작가별 그룹화 완료: {len(artist_works)}명의 작가")
        return artist_works
    
    def match_artists_to_biennale(
        self,
        artist_names: List[str],
        works: List[Dict]
    ) -> Dict[str, Dict]:
        """
        작가 이름으로 비엔날레 참여 정보 매칭
        
        Args:
            artist_names: 작가 이름 리스트 (한글, 영문 모두 포함 가능)
            works: 정규화된 작품 데이터 리스트
            
        Returns:
            {작가명: 비엔날레 참여 정보} 딕셔너리
        """
        matched = {}
        
        # 작가 이름 정규화
        normalized_artist_names = {
            name.lower().replace(" ", ""): name 
            for name in artist_names
        }
        
        for work in works:
            artist_name_ko = work.get("artist_name_ko", "").lower().replace(" ", "")
            artist_name_en = work.get("artist_name_en", "").lower().replace(" ", "")
            
            # 한글 이름으로 매칭
            if artist_name_ko in normalized_artist_names:
                artist_name = normalized_artist_names[artist_name_ko]
                if artist_name not in matched:
                    matched[artist_name] = {
                        "participation_count": 0,
                        "award_count": 0,
                        "events": [],
                        "works": []
                    }
                matched[artist_name]["participation_count"] += 1
                matched[artist_name]["works"].append(work)
                
                # 입상 정보 확인
                if work.get("award_name"):
                    matched[artist_name]["award_count"] += 1
                
                # 행사 정보 추가
                event_name = work.get("event_name_ko") or work.get("event_name_en")
                if event_name and event_name not in matched[artist_name]["events"]:
                    matched[artist_name]["events"].append(event_name)
            
            # 영문 이름으로 매칭
            elif artist_name_en:
                for normalized_artist, original_artist in normalized_artist_names.items():
                    if len(normalized_artist) >= 2 and normalized_artist in artist_name_en:
                        if original_artist not in matched:
                            matched[original_artist] = {
                                "participation_count": 0,
                                "award_count": 0,
                                "events": [],
                                "works": []
                            }
                        matched[original_artist]["participation_count"] += 1
                        matched[original_artist]["works"].append(work)
                        
                        if work.get("award_name"):
                            matched[original_artist]["award_count"] += 1
                        
                        event_name = work.get("event_name_ko") or work.get("event_name_en")
                        if event_name and event_name not in matched[original_artist]["events"]:
                            matched[original_artist]["events"].append(event_name)
                        break
        
        logger.info(f"작가-비엔날레 매칭 완료: {len(matched)}명의 작가에 매칭")
        return matched









