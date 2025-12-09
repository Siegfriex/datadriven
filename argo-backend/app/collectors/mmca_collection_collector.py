"""
국립현대미술관 소장작품 API 데이터 수집기

API 정보:
- Host: api.kcisa.kr
- Base Path: /openapi/service/rest/meta10/get20150041
- 엔드포인트: /openapi/service/rest/meta10/get20150041
- 인증: serviceKey 쿼리 파라미터
- 데이터 형식: JSON, XML
- 신뢰도: 0.95 (국립현대미술관 공식 소장작품 데이터)
- 업데이트 주기: 비정기 (소장작품 추가 시)
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import time
import logging
import re
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


class MMCACollectionCollector:
    """
    국립현대미술관 소장작품 API 데이터 수집기
    
    한국문화정보원(KCISA) API 사용
    국립현대미술관에서 제공하는 소장작품 정보
    """
    
    BASE_URL = "https://api.kcisa.kr/openapi/service/rest/meta10/get20150041"
    
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
    def get_collection_page(
        self,
        page_no: int = 1,
        num_of_rows: int = 100
    ) -> Dict:
        """
        소장작품 페이지 조회
        
        Args:
            page_no: 페이지 번호 (1부터 시작)
            num_of_rows: 페이지당 항목 수 (기본 10, 최대 100)
            
        Returns:
            API 응답 딕셔너리
        """
        params = {
            "serviceKey": self.service_key,
            "pageNo": str(page_no),
            "numOfRows": str(min(num_of_rows, 100))  # 최대 100
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"MMCA 소장작품 API 응답 오류 (상태 코드: {response.status_code})")
                logger.error(f"응답 본문: {response.text[:500]}")
                logger.error(f"요청 URL: {response.url}")
            
            response.raise_for_status()
            
            data = response.json()
            
            # 응답 구조 확인 및 처리
            if "body" in data:
                body = data["body"]
                items = body.get("items", {})
                
                # items가 딕셔너리인 경우 item 배열 추출
                if isinstance(items, dict) and "item" in items:
                    item_list = items["item"]
                    # 단일 항목인 경우 리스트로 변환
                    if not isinstance(item_list, list):
                        item_list = [item_list]
                else:
                    item_list = []
                
                total_count = int(body.get("totalCount", 0))
                
                logger.info(
                    f"MMCA 소장작품 API: 페이지 {page_no} 수집 완료 "
                    f"(현재: {len(item_list)}, 전체: {total_count})"
                )
                
                return {
                    "items": item_list,
                    "totalCount": total_count,
                    "pageNo": int(body.get("pageNo", page_no)),
                    "numOfRows": int(body.get("numOfRows", num_of_rows))
                }
            
            return {"items": [], "totalCount": 0, "pageNo": page_no, "numOfRows": num_of_rows}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MMCA 소장작품 API 요청 실패 (page {page_no}): {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 본문: {e.response.text[:500]}")
            raise
    
    def collect_all(
        self,
        max_count: Optional[int] = None
    ) -> List[Dict]:
        """
        전체 소장작품 데이터 수집
        
        Args:
            max_count: 최대 수집 수량 (None이면 전체 수집)
            
        Returns:
            소장작품 데이터 리스트
        """
        all_works = []
        page = 1
        per_page = 100
        
        # 첫 페이지로 전체 개수 확인
        first_page = self.get_collection_page(page_no=1, num_of_rows=per_page)
        total_count = first_page.get("totalCount", 0)
        
        logger.info(f"MMCA 소장작품 API 전체 작품 수: {total_count}개")
        
        # 첫 페이지 데이터 추가
        all_works.extend(first_page.get("items", []))
        
        # 나머지 페이지 수집
        total_pages = (total_count + per_page - 1) // per_page
        
        for page in range(2, total_pages + 1):
            if max_count and len(all_works) >= max_count:
                break
            
            page_data = self.get_collection_page(page_no=page, num_of_rows=per_page)
            all_works.extend(page_data.get("items", []))
            
            # Rate Limit 고려
            time.sleep(0.1)
            
            logger.info(f"수집 진행: {len(all_works)}/{total_count}")
        
        # max_count 제한 적용
        if max_count:
            all_works = all_works[:max_count]
        
        logger.info(f"MMCA 소장작품 API 수집 완료: {len(all_works)}개 작품")
        return all_works
    
    def parse_creator(self, creator_str: str) -> List[str]:
        """
        creator 필드에서 작가 이름 리스트 추출
        
        Args:
            creator_str: creator 필드 문자열 (여러 작가가 쉼표로 구분될 수 있음)
            
        Returns:
            작가 이름 리스트
        """
        if not creator_str:
            return []
        
        # 쉼표로 구분된 작가 이름 파싱
        creators = [c.strip() for c in creator_str.split(",") if c.strip()]
        return creators
    
    def parse_temporal_coverage(self, temporal_str: str) -> Optional[int]:
        """
        temporalCoverage 필드에서 제작 연도 추출
        
        Args:
            temporal_str: temporalCoverage 필드 문자열
            
        Returns:
            제작 연도 (없으면 None)
        """
        if not temporal_str:
            return None
        
        # 연도 패턴 찾기 (4자리 숫자)
        year_pattern = r'\b(19|20)\d{2}\b'
        matches = re.findall(year_pattern, temporal_str)
        
        if matches:
            # 첫 번째 매칭된 연도 반환
            try:
                return int(matches[0] + matches[1] if len(matches) >= 2 else matches[0])
            except:
                # 전체 문자열에서 연도 찾기
                full_year_match = re.search(r'\b(19|20)\d{2}\b', temporal_str)
                if full_year_match:
                    return int(full_year_match.group())
        
        return None
    
    def normalize_collection_data(self, raw_data: Dict) -> Dict:
        """
        MMCA 소장작품 API 응답 데이터를 ARGO 형식으로 정규화
        
        Args:
            raw_data: MMCA 소장작품 API 원본 데이터
            
        Returns:
            정규화된 소장작품 데이터
        """
        # 안전한 값 추출 헬퍼
        def safe_str(value, default=""):
            if value is None:
                return default
            return str(value).strip() if isinstance(value, str) else str(value)
        
        # creator 파싱
        creator_str = safe_str(raw_data.get("creator", ""))
        creators = self.parse_creator(creator_str)
        
        # temporalCoverage 파싱
        temporal_str = safe_str(raw_data.get("temporalCoverage", ""))
        creation_year = self.parse_temporal_coverage(temporal_str)
        
        return {
            # 작품 기본 정보
            "title": safe_str(raw_data.get("title", "")),
            "alternative_title": safe_str(raw_data.get("alternativeTitle", "")),
            "description": safe_str(raw_data.get("description", "")),
            
            # 작가 정보
            "creators": creators,
            "first_creator": creators[0] if creators else None,
            "contributor": safe_str(raw_data.get("contributor", "")),
            "person": safe_str(raw_data.get("person", "")),
            
            # 제작 정보
            "creation_year": creation_year,
            "temporal_coverage": temporal_str,
            
            # 분류 정보
            "subject_category": safe_str(raw_data.get("subjectCategory", "")),
            "subject_keyword": safe_str(raw_data.get("subjectKeyword", "")),
            
            # 공간 정보
            "spatial": safe_str(raw_data.get("spatial", "")),
            
            # 물리적 정보
            "extent": safe_str(raw_data.get("extent", "")),
            
            # 미디어 정보
            "reference_identifier": safe_str(raw_data.get("referenceIdentifier", "")),  # 썸네일 이미지
            "url": safe_str(raw_data.get("url", "")),
            
            # 권리 정보
            "rights": safe_str(raw_data.get("rights", "")),
            "copyright_others": safe_str(raw_data.get("copyrightOthers", "")),
            
            # 메타데이터
            "collection_db": safe_str(raw_data.get("collectionDb", "")),
            "language": safe_str(raw_data.get("language", "")),
            "source_title": safe_str(raw_data.get("sourceTitle", "")),
            "registration_date": safe_str(raw_data.get("regDate", "")),
            
            # 메타데이터
            "source": "MMCA_COLLECTION",
            "data_source": ["MMCA_COLLECTION"],
            "confidence_score": 0.95,  # 국립현대미술관 공식 소장작품 데이터
            "collected_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def group_by_creator(self, works: List[Dict]) -> Dict[str, List[Dict]]:
        """
        작가별로 소장작품 그룹화
        
        Args:
            works: 정규화된 소장작품 데이터 리스트
            
        Returns:
            {작가명: [작품 리스트]} 딕셔너리
        """
        creator_works = {}
        
        for work in works:
            creators = work.get("creators", [])
            
            for creator in creators:
                if not creator:
                    continue
                
                if creator not in creator_works:
                    creator_works[creator] = []
                
                creator_works[creator].append(work)
        
        logger.info(f"작가별 그룹화 완료: {len(creator_works)}명의 작가")
        return creator_works
    
    def match_artists_to_collection(
        self,
        artist_names: List[str],
        works: List[Dict]
    ) -> Dict[str, Dict]:
        """
        작가 이름으로 소장작품 매칭
        
        Args:
            artist_names: 작가 이름 리스트 (한글, 영문 모두 포함 가능)
            works: 정규화된 소장작품 데이터 리스트
            
        Returns:
            {작가명: 소장작품 정보} 딕셔너리
        """
        matched = {}
        
        # 작가 이름 정규화
        normalized_artist_names = {
            name.lower().replace(" ", ""): name 
            for name in artist_names
        }
        
        for work in works:
            creators = work.get("creators", [])
            
            for creator in creators:
                if not creator:
                    continue
                
                # 정규화된 이름으로 매칭
                normalized_creator = creator.lower().replace(" ", "")
                
                # 정확 일치 확인
                if normalized_creator in normalized_artist_names:
                    artist_name = normalized_artist_names[normalized_creator]
                    if artist_name not in matched:
                        matched[artist_name] = {
                            "collection_count": 0,
                            "works": []
                        }
                    matched[artist_name]["collection_count"] += 1
                    matched[artist_name]["works"].append(work)
                    continue
                
                # 부분 일치 확인
                for normalized_artist, original_artist in normalized_artist_names.items():
                    if len(normalized_artist) >= 2:
                        # 이름이 포함되어 있는지 확인
                        if normalized_artist in normalized_creator or normalized_creator in normalized_artist:
                            if original_artist not in matched:
                                matched[original_artist] = {
                                    "collection_count": 0,
                                    "works": []
                                }
                            matched[original_artist]["collection_count"] += 1
                            matched[original_artist]["works"].append(work)
                            break
        
        logger.info(f"작가-소장작품 매칭 완료: {len(matched)}명의 작가에 매칭")
        return matched

