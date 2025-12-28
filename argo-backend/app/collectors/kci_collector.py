"""
KCI (한국학술지인용색인) API 데이터 수집기

API 정보:
- Host: api.odcloud.kr
- Base Path: /api
- 엔드포인트: /15083283/v1/uddi:9cdf9a0d-6563-4dfe-9957-ecbe798c53e6 (2025-08-25 최신 버전)
- 인증: serviceKey 쿼리 파라미터
- 신뢰도: 0.85 (학술 데이터, 공식 소스)
- 업데이트 주기: 연간
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


class KCICollector:
    """
    KCI (한국학술지인용색인) API 데이터 수집기
    
    공공데이터포털(ODCloud) API 사용
    한국연구재단에서 제공하는 학술 논문 정보
    """
    
    BASE_URL = "https://api.odcloud.kr/api"
    ENDPOINT = "/15083283/v1/uddi:9cdf9a0d-6563-4dfe-9957-ecbe798c53e6"  # 2025-08-25 최신 버전
    
    # 미술 관련 주제분야 키워드 (필터링용)
    ART_RELATED_KEYWORDS = [
        "미술", "예술", "조형", "회화", "조각", "공예", "디자인",
        "art", "fine art", "visual art", "painting", "sculpture"
    ]
    
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
    def get_papers_page(
        self, 
        page: int = 1, 
        per_page: int = 100
    ) -> Dict:
        """
        논문 목록 페이지 조회
        
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
                logger.error(f"KCI API 응답 오류 (상태 코드: {response.status_code})")
                logger.error(f"응답 본문: {response.text[:500]}")
                logger.error(f"요청 URL: {response.url}")
            
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(
                f"KCI API: 페이지 {page} 수집 완료 "
                f"(현재: {data.get('currentCount', 0)}, 전체: {data.get('totalCount', 0)})"
            )
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"KCI API 요청 실패 (page {page}): {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 본문: {e.response.text[:500]}")
            raise
    
    def collect_all(
        self, 
        max_count: Optional[int] = None,
        filter_art_related: bool = True
    ) -> List[Dict]:
        """
        전체 논문 데이터 수집
        
        Args:
            max_count: 최대 수집 수량 (None이면 전체 수집)
            filter_art_related: 미술 관련 논문만 필터링 (기본: True)
            
        Returns:
            논문 데이터 리스트
        """
        all_papers = []
        page = 1
        per_page = 100
        
        # 첫 페이지로 전체 개수 확인
        first_page = self.get_papers_page(page=1, per_page=per_page)
        total_count = first_page.get("totalCount", 0)
        
        logger.info(f"KCI API 전체 논문 수: {total_count}개")
        
        # 첫 페이지 데이터 처리
        first_data = first_page.get("data", [])
        if filter_art_related:
            first_data = self._filter_art_related(first_data)
        all_papers.extend(first_data)
        
        # 나머지 페이지 수집
        total_pages = (total_count + per_page - 1) // per_page
        
        for page in range(2, total_pages + 1):
            if max_count and len(all_papers) >= max_count:
                break
            
            page_data = self.get_papers_page(page=page, per_page=per_page)
            page_papers = page_data.get("data", [])
            
            if filter_art_related:
                page_papers = self._filter_art_related(page_papers)
            
            all_papers.extend(page_papers)
            
            # Rate Limit 고려 (초당 10회 제한 가정)
            time.sleep(0.1)
            
            logger.info(f"수집 진행: {len(all_papers)}/{total_count if not filter_art_related else '필터링됨'}")
        
        # max_count 제한 적용
        if max_count:
            all_papers = all_papers[:max_count]
        
        logger.info(f"KCI API 수집 완료: {len(all_papers)}개 논문")
        return all_papers
    
    def _filter_art_related(self, papers: List[Dict]) -> List[Dict]:
        """
        미술 관련 논문만 필터링
        
        주제분야, 논문명, 키워드 등을 기반으로 필터링
        """
        filtered = []
        
        for paper in papers:
            # 주제분야 확인
            subject = paper.get("주제분야", "").lower()
            title_ko = paper.get("논문명(국문)", "").lower()
            title_en = paper.get("논문명(영어)", "").lower()
            keywords_ko = paper.get("키워드(국문)", "").lower()
            keywords_en = paper.get("키워드(영문)", "").lower()
            
            # 미술 관련 키워드 포함 여부 확인
            text_to_check = f"{subject} {title_ko} {title_en} {keywords_ko} {keywords_en}"
            
            if any(keyword.lower() in text_to_check for keyword in self.ART_RELATED_KEYWORDS):
                filtered.append(paper)
        
        return filtered
    
    def normalize_paper_data(self, raw_data: Dict) -> Dict:
        """
        KCI API 응답 데이터를 ARGO 형식으로 정규화
        
        Args:
            raw_data: KCI API 원본 데이터
            
        Returns:
            정규화된 논문 데이터
        """
        # 안전한 문자열 추출 헬퍼
        def safe_str(value, default=""):
            if value is None:
                return default
            return str(value).strip() if isinstance(value, str) else str(value)
        
        def safe_int(value, default=None):
            try:
                return int(value) if value is not None else default
            except:
                return default
        
        # 저자 파싱 (쉼표로 구분된 여러 저자)
        authors_str = safe_str(raw_data.get("저자", ""))
        authors = [a.strip() for a in authors_str.split(",") if a.strip()] if authors_str else []
        
        # 공동저자 파싱
        coauthors_str = safe_str(raw_data.get("공동저자", ""))
        coauthors = [a.strip() for a in coauthors_str.split(",") if a.strip()] if coauthors_str else []
        
        # 모든 저자 통합
        all_authors = list(set(authors + coauthors))
        
        # 등재구분 파싱
        registration_type = safe_str(raw_data.get("등재구분", ""))
        is_kci_registered = "등재" in registration_type or "KCI" in registration_type.upper()
        
        # 해외 등재 구분 파싱
        international_registration = safe_str(raw_data.get("해외 등재 구분", ""))
        is_international = bool(international_registration)
        
        return {
            # 논문 기본 정보
            "title_ko": safe_str(raw_data.get("논문명(국문)", "")),
            "title_en": safe_str(raw_data.get("논문명(영어)", "")),
            "title_foreign": safe_str(raw_data.get("논문명(외국어)", "")),
            
            # 저자 정보
            "authors": all_authors,
            "first_author": authors[0] if authors else None,
            "coauthors": coauthors,
            
            # 학술지 정보
            "journal_name_ko": safe_str(raw_data.get("학술지명(국문)", "")),
            "journal_name_foreign": safe_str(raw_data.get("학술지명(외국어)", "")),
            "issn": safe_str(raw_data.get("국제표준연속간행물", "")),
            
            # 발행 정보
            "publisher_ko": safe_str(raw_data.get("발행기관명(국문)", "")),
            "publisher_en": safe_str(raw_data.get("발행기관명(영문)", "")),
            "publication_year": safe_int(raw_data.get("발행년")),
            "volume": safe_int(raw_data.get("권")),
            "issue": safe_int(raw_data.get("호")),
            "start_page": safe_int(raw_data.get("시작페이지")),
            "end_page": safe_int(raw_data.get("끝페이지")),
            
            # 등재 정보
            "registration_type": registration_type,
            "is_kci_registered": is_kci_registered,
            "international_registration": international_registration,
            "is_international": is_international,
            
            # 키워드 및 주제
            "keywords_ko": [k.strip() for k in safe_str(raw_data.get("키워드(국문)", "")).split(",") if k.strip()],
            "keywords_en": [k.strip() for k in safe_str(raw_data.get("키워드(영문)", "")).split(",") if k.strip()],
            "keywords_foreign": [k.strip() for k in safe_str(raw_data.get("키워드(외국어)", "")).split(",") if k.strip()],
            "subject_area": safe_str(raw_data.get("주제분야", "")),
            
            # 메타데이터
            "data_date": safe_str(raw_data.get("데이터기준일", "")),
            "source": "KCI",
            "data_source": ["KCI"],
            "confidence_score": 0.85,  # KCI 신뢰도
            "collected_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def group_by_author(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        """
        저자별로 논문 그룹화
        
        Args:
            papers: 정규화된 논문 데이터 리스트
            
        Returns:
            {저자명: [논문 리스트]} 딕셔너리
        """
        author_papers = {}
        
        for paper in papers:
            authors = paper.get("authors", [])
            
            for author in authors:
                if not author:
                    continue
                
                if author not in author_papers:
                    author_papers[author] = []
                
                author_papers[author].append(paper)
        
        logger.info(f"저자별 그룹화 완료: {len(author_papers)}명의 저자")
        return author_papers
    
    def match_artists_to_papers(
        self, 
        artist_names: List[str], 
        papers: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        작가 이름으로 논문 매칭
        
        Args:
            artist_names: 작가 이름 리스트 (한글, 영문 모두 포함 가능)
            papers: 정규화된 논문 데이터 리스트
            
        Returns:
            {작가명: [매칭된 논문 리스트]} 딕셔너리
        """
        matched = {name: [] for name in artist_names}
        
        # 작가 이름 정규화 (공백 제거, 소문자 변환)
        normalized_artist_names = {
            name.lower().replace(" ", ""): name 
            for name in artist_names
        }
        
        for paper in papers:
            authors = paper.get("authors", [])
            
            for author in authors:
                # 저자 이름 정규화
                normalized_author = author.lower().replace(" ", "")
                
                # 정확히 일치하는 경우
                if normalized_author in normalized_artist_names:
                    artist_name = normalized_artist_names[normalized_author]
                    matched[artist_name].append(paper)
                    continue
                
                # 부분 일치 확인 (성씨 + 이름 일부)
                for normalized_artist, original_artist in normalized_artist_names.items():
                    if len(normalized_artist) >= 2 and normalized_artist in normalized_author:
                        matched[original_artist].append(paper)
                        break
        
        # 중복 제거
        for artist_name in matched:
            # 논문을 고유하게 만들기 위해 제목+저자+발행년 조합 사용
            seen = set()
            unique_papers = []
            for paper in matched[artist_name]:
                key = (
                    paper.get("title_ko", ""),
                    paper.get("first_author", ""),
                    paper.get("publication_year")
                )
                if key not in seen:
                    seen.add(key)
                    unique_papers.append(paper)
            matched[artist_name] = unique_papers
        
        logger.info(f"작가-논문 매칭 완료: {sum(1 for papers in matched.values() if papers)}명의 작가에 매칭")
        return matched









