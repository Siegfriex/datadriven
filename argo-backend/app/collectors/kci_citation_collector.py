"""
KCI 인용 정보 서비스 API 데이터 수집기

API 정보:
- Host: apis.data.go.kr
- Base Path: /B552540/KCIOpenApi/citedInfo
- 엔드포인트: 
  - 저자별 인용지수: /openApiM376List
  - 인용정보(학술지별): /openApiM373List
  - 공용코드: /openApiM372List
- 인증: serviceKey 쿼리 파라미터
- 데이터 형식: XML
- 신뢰도: 0.90 (인용 통계 데이터, 공식 소스)
- 업데이트 주기: 일 1회
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import time
import logging
import xml.etree.ElementTree as ET
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


class KCICitationCollector:
    """
    KCI 인용 정보 서비스 API 데이터 수집기
    
    공공데이터포털 API 사용
    한국연구재단에서 제공하는 학술 인용 통계 정보
    """
    
    BASE_URL = "http://apis.data.go.kr/B552540/KCIOpenApi/citedInfo"
    
    # 저자별 인용지수 조회 엔드포인트 (가장 중요)
    AUTHOR_CITATION_ENDPOINT = "/openApiM376List"
    
    # 인용정보(학술지별) 조회 엔드포인트
    JOURNAL_CITATION_ENDPOINT = "/openApiM373List"
    
    # 공용코드 조회 엔드포인트
    COMMON_CODE_ENDPOINT = "/openApiM372List"
    
    def __init__(self, service_key: str):
        """
        Args:
            service_key: serviceKey 쿼리 파라미터 값 (필수)
        """
        self.service_key = service_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/xml",
            "User-Agent": "ARGO-DataCollector/1.0"
        })
    
    def _parse_xml_response(self, xml_string: str) -> Dict:
        """
        XML 응답을 파싱하여 딕셔너리로 변환
        
        Args:
            xml_string: XML 응답 문자열
            
        Returns:
            파싱된 데이터 딕셔너리
        """
        try:
            root = ET.fromstring(xml_string)
            
            # 헤더 정보 추출
            header = root.find('header')
            result_code = header.find('resultCode').text if header is not None and header.find('resultCode') is not None else None
            result_msg = header.find('resultMsg').text if header is not None and header.find('resultMsg') is not None else None
            
            # 바디 정보 추출
            body = root.find('body')
            items = []
            
            if body is not None:
                items_elem = body.find('items')
                if items_elem is not None:
                    for item in items_elem.findall('item'):
                        item_dict = {}
                        for child in item:
                            # 텍스트 값 추출
                            text = child.text if child.text else None
                            # 숫자로 변환 가능한 경우 변환
                            if text is not None:
                                try:
                                    # 정수로 변환 시도
                                    if '.' in text:
                                        item_dict[child.tag] = float(text)
                                    else:
                                        item_dict[child.tag] = int(text)
                                except ValueError:
                                    item_dict[child.tag] = text
                            else:
                                item_dict[child.tag] = None
                        items.append(item_dict)
                
                # 페이지네이션 정보
                record_cnt = body.find('recordCnt')
                page_no = body.find('pageNo')
                total_count = body.find('totalCount')
                
                return {
                    "resultCode": result_code,
                    "resultMsg": result_msg,
                    "recordCnt": int(record_cnt.text) if record_cnt is not None and record_cnt.text else 0,
                    "pageNo": int(page_no.text) if page_no is not None and page_no.text else 0,
                    "totalCount": int(total_count.text) if total_count is not None and total_count.text else 0,
                    "items": items
                }
            
            return {
                "resultCode": result_code,
                "resultMsg": result_msg,
                "items": []
            }
            
        except ET.ParseError as e:
            logger.error(f"XML 파싱 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"응답 파싱 오류: {e}")
            raise
    
    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def get_author_citations_page(
        self,
        page: int = 1,
        per_page: int = 100
    ) -> Dict:
        """
        저자별 인용지수 페이지 조회
        
        Args:
            page: 페이지 번호 (1부터 시작)
            per_page: 페이지당 항목 수 (기본 10, 최대 100)
            
        Returns:
            API 응답 딕셔너리
        """
        url = f"{self.BASE_URL}{self.AUTHOR_CITATION_ENDPOINT}"
        params = {
            "serviceKey": self.service_key,
            "pageNo": page,
            "recordCnt": min(per_page, 100)  # 최대 100
        }
        
        try:
            response = self.session.get(url, params=params, timeout=60)  # 응답 시간이 길 수 있음 (14초 평균)
            
            if response.status_code != 200:
                logger.error(f"KCI 인용 정보 API 응답 오류 (상태 코드: {response.status_code})")
                logger.error(f"응답 본문: {response.text[:500]}")
                logger.error(f"요청 URL: {response.url}")
            
            response.raise_for_status()
            
            # XML 파싱
            data = self._parse_xml_response(response.text)
            
            # 에러 코드 확인
            if data.get("resultCode") != "00":
                error_msg = data.get("resultMsg", "Unknown error")
                logger.error(f"KCI 인용 정보 API 에러: {error_msg}")
                raise ValueError(f"API 에러: {error_msg}")
            
            logger.info(
                f"KCI 인용 정보 API: 페이지 {page} 수집 완료 "
                f"(현재: {len(data.get('items', []))}, 전체: {data.get('totalCount', 0)})"
            )
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"KCI 인용 정보 API 요청 실패 (page {page}): {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 본문: {e.response.text[:500]}")
            raise
    
    def collect_author_citations(
        self,
        max_count: Optional[int] = None,
        filter_art_related: bool = True
    ) -> List[Dict]:
        """
        저자별 인용지수 데이터 수집
        
        Args:
            max_count: 최대 수집 수량 (None이면 전체 수집)
            filter_art_related: 미술 관련 저자만 필터링 (기본: True)
            
        Returns:
            저자 인용지수 데이터 리스트
        """
        all_authors = []
        page = 1
        per_page = 100
        
        # 첫 페이지로 전체 개수 확인
        first_page = self.get_author_citations_page(page=1, per_page=per_page)
        total_count = first_page.get("totalCount", 0)
        
        logger.info(f"KCI 인용 정보 API 전체 저자 수: {total_count}명")
        
        # 첫 페이지 데이터 처리
        first_items = first_page.get("items", [])
        if filter_art_related:
            first_items = self._filter_art_related_authors(first_items)
        all_authors.extend(first_items)
        
        # 나머지 페이지 수집
        total_pages = (total_count + per_page - 1) // per_page
        
        for page in range(2, total_pages + 1):
            if max_count and len(all_authors) >= max_count:
                break
            
            page_data = self.get_author_citations_page(page=page, per_page=per_page)
            page_items = page_data.get("items", [])
            
            if filter_art_related:
                page_items = self._filter_art_related_authors(page_items)
            
            all_authors.extend(page_items)
            
            # Rate Limit 고려 (초당 30회 제한, 평균 응답 시간 14초)
            time.sleep(0.5)  # 안전한 간격 유지
            
            logger.info(f"수집 진행: {len(all_authors)}/{total_count if not filter_art_related else '필터링됨'}")
        
        # max_count 제한 적용
        if max_count:
            all_authors = all_authors[:max_count]
        
        logger.info(f"KCI 인용 정보 API 수집 완료: {len(all_authors)}명의 저자")
        return all_authors
    
    def _filter_art_related_authors(self, authors: List[Dict]) -> List[Dict]:
        """
        미술 관련 저자만 필터링
        
        연구분야명(SPCL_NM)을 기반으로 필터링
        """
        filtered = []
        
        art_keywords = [
            "미술", "예술", "조형", "회화", "조각", "공예", "디자인",
            "art", "fine art", "visual art", "painting", "sculpture"
        ]
        
        for author in authors:
            research_field = author.get("SPCL_NM", "").lower()
            
            if any(keyword.lower() in research_field for keyword in art_keywords):
                filtered.append(author)
        
        return filtered
    
    def normalize_author_citation_data(self, raw_data: Dict) -> Dict:
        """
        KCI 인용 정보 API 응답 데이터를 ARGO 형식으로 정규화
        
        Args:
            raw_data: KCI 인용 정보 API 원본 데이터
            
        Returns:
            정규화된 저자 인용지수 데이터
        """
        # 안전한 값 추출 헬퍼
        def safe_int(value, default=0):
            try:
                return int(value) if value is not None else default
            except:
                return default
        
        def safe_float(value, default=0.0):
            try:
                return float(value) if value is not None else default
            except:
                return default
        
        def safe_str(value, default=""):
            if value is None:
                return default
            return str(value).strip() if isinstance(value, str) else str(value)
        
        return {
            # 저자 기본 정보
            "author_id": safe_str(raw_data.get("CRET_ID", "")),
            "author_name_ko": safe_str(raw_data.get("CRET_KOR_NM", "")),
            "author_name_en": safe_str(raw_data.get("CRET_ENG_NM", "")),
            "birth_year": safe_int(raw_data.get("BIRTH_YEAR")),
            
            # 소속 기관 정보
            "institution_id": safe_str(raw_data.get("INSI_ID", "")),
            "institution_name": safe_str(raw_data.get("INSI_NM", "")),
            
            # 연구 분야 정보
            "research_field_code": safe_str(raw_data.get("SPCL_CD", "")),
            "research_field_name": safe_str(raw_data.get("SPCL_NM", "")),
            
            # 인용 통계 정보
            "total_citations": safe_int(raw_data.get("TOT_SERE_CNT", 0)),  # 전체년도 피인용수
            "average_citations": safe_float(raw_data.get("SERE_AVG", 0.0)),  # 평균 피인용 횟수
            "h_index": safe_int(raw_data.get("H_IDX", 0)),  # H지수
            "coauthor_adjusted_h_index": safe_int(raw_data.get("COR_H_IDX", 0)),  # 공저보정 H지수
            
            # 논문 통계 정보
            "total_papers": safe_int(raw_data.get("TOT_ARTI_CNT", 0)),  # 전체년도 논문수
            "solo_papers": safe_int(raw_data.get("CRET_1", 0)),  # 단독저자 논문수
            "coauthor_2_papers": safe_int(raw_data.get("CRET_2", 0)),  # 2인 저자 논문수
            "coauthor_3_papers": safe_int(raw_data.get("CRET_3", 0)),  # 3인 저자 논문수
            "coauthor_4plus_papers": safe_int(raw_data.get("CRET_4", 0)),  # 4인 이상 저자 논문수
            
            # 자기 인용 정보
            "self_citations": safe_int(raw_data.get("SELF_CITED_CNT", 0)),  # 자기 인용수
            "total_self_citations": safe_int(raw_data.get("TOT_SELF_CITED_CNT", 0)),  # 전체년도 자기 인용수
            
            # 추가 정보
            "kri_id": safe_str(raw_data.get("KRI_ID", "")),  # KRI ID
            "registration_date": safe_str(raw_data.get("RESI_DT", "")),  # 등록일시
            
            # 메타데이터
            "source": "KCI_CITATION",
            "data_source": ["KCI_CITATION"],
            "confidence_score": 0.90,  # 인용 통계 데이터는 높은 신뢰도
            "collected_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def match_artists_to_citations(
        self,
        artist_names: List[str],
        citation_data: List[Dict]
    ) -> Dict[str, Dict]:
        """
        작가 이름으로 인용지수 데이터 매칭
        
        Args:
            artist_names: 작가 이름 리스트 (한글, 영문 모두 포함 가능)
            citation_data: 정규화된 인용지수 데이터 리스트
            
        Returns:
            {작가명: 인용지수 데이터} 딕셔너리
        """
        matched = {}
        
        # 작가 이름 정규화 (공백 제거, 소문자 변환)
        normalized_artist_names = {
            name.lower().replace(" ", ""): name 
            for name in artist_names
        }
        
        for citation in citation_data:
            author_name_ko = citation.get("author_name_ko", "").lower().replace(" ", "")
            author_name_en = citation.get("author_name_en", "").lower().replace(" ", "")
            
            # 한글 이름으로 매칭
            if author_name_ko in normalized_artist_names:
                artist_name = normalized_artist_names[author_name_ko]
                if artist_name not in matched:
                    matched[artist_name] = citation
                continue
            
            # 영문 이름으로 매칭 (성, 이름 순서 고려)
            for normalized_artist, original_artist in normalized_artist_names.items():
                if len(normalized_artist) >= 2:
                    # 영문 이름에서 성(Last name) 추출 시도
                    if author_name_en and normalized_artist in author_name_en:
                        if original_artist not in matched:
                            matched[original_artist] = citation
                            break
        
        logger.info(f"작가-인용지수 매칭 완료: {len(matched)}명의 작가에 매칭")
        return matched







