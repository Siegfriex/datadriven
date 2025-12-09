"""
ARKO 문화예술 채용정보 API 데이터 수집기

API 정보:
- Host: api.odcloud.kr
- Base Path: /api
- 엔드포인트: /15012952/v1/uddi:047d7b05-2abc-4f26-957f-a20ec21f773e_201607051740
- 인증: serviceKey 쿼리 파라미터
- 데이터 시점: 2016년 (1회성 데이터)
- 신뢰도: 0.85 (과거 데이터이므로 신뢰도 낮음)
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


class JobCollector:
    """
    ARKO 문화예술 채용정보 API 데이터 수집기
    
    공공데이터포털(ODCloud) API 사용
    기관의 채용 활동 정보 수집 (Institution 정보 보강용)
    """
    
    BASE_URL = "https://api.odcloud.kr/api"
    ENDPOINT = "/15012952/v1/uddi:047d7b05-2abc-4f26-957f-a20ec21f773e_201607051740"
    
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
    def get_jobs_page(
        self, 
        page: int = 1, 
        per_page: int = 100
    ) -> Dict:
        """
        채용정보 목록 페이지 조회
        
        Args:
            page: 페이지 번호 (1부터 시작)
            per_page: 페이지당 항목 수 (기본 10, 최대 100)
            
        Returns:
            API 응답 딕셔너리
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
                logger.error(f"ARKO 채용정보 API 응답 오류 (상태 코드: {response.status_code})")
                logger.error(f"응답 본문: {response.text[:500]}")
                logger.error(f"요청 URL: {response.url}")
            
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(
                f"ARKO 채용정보 API: 페이지 {page} 수집 완료 "
                f"(현재: {data.get('currentCount', 0)}, 전체: {data.get('totalCount', 0)})"
            )
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ARKO 채용정보 API 요청 실패 (page {page}): {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 본문: {e.response.text[:500]}")
            raise
    
    def collect_all(self, max_count: Optional[int] = None) -> List[Dict]:
        """
        전체 채용정보 데이터 수집
        
        Args:
            max_count: 최대 수집 수량 (None이면 전체 수집)
            
        Returns:
            채용정보 데이터 리스트
        """
        all_jobs = []
        page = 1
        per_page = 100
        
        # 첫 페이지로 전체 개수 확인
        first_page = self.get_jobs_page(page=1, per_page=per_page)
        total_count = first_page.get("totalCount", 0)
        
        logger.info(f"ARKO 채용정보 API 전체 채용정보 수: {total_count}개")
        
        # 첫 페이지 데이터 추가
        all_jobs.extend(first_page.get("data", []))
        
        # 나머지 페이지 수집
        total_pages = (total_count + per_page - 1) // per_page
        
        for page in range(2, total_pages + 1):
            if max_count and len(all_jobs) >= max_count:
                break
            
            page_data = self.get_jobs_page(page=page, per_page=per_page)
            all_jobs.extend(page_data.get("data", []))
            
            # Rate Limit 고려 (초당 10회 제한 가정)
            time.sleep(0.1)
            
            logger.info(f"수집 진행: {len(all_jobs)}/{total_count}")
        
        # max_count 제한 적용
        if max_count:
            all_jobs = all_jobs[:max_count]
        
        logger.info(f"ARKO 채용정보 API 수집 완료: {len(all_jobs)}개")
        return all_jobs
    
    def normalize_job_data(self, raw_data: Dict) -> Dict:
        """
        ARKO API 응답 데이터를 ARGO 형식으로 정규화
        
        Args:
            raw_data: ARKO API 원본 데이터
                {
                    "기관명": "기관명",
                    "근무지역": "근무지역",
                    "마감일": "2016-07-15"
                }
        
        Returns:
            정규화된 채용정보 데이터
        """
        # 안전한 문자열 추출 헬퍼
        def safe_str(value, default=""):
            if value is None:
                return default
            return str(value).strip() if isinstance(value, str) else default
        
        institution_name = safe_str(raw_data.get("기관명"))
        work_location = safe_str(raw_data.get("근무지역"))
        deadline_raw = safe_str(raw_data.get("마감일"))
        
        # 마감일 파싱
        deadline = None
        deadline_year = None
        if deadline_raw:
            try:
                # YYYY-MM-DD 형식 파싱
                deadline_date = datetime.strptime(deadline_raw, "%Y-%m-%d")
                deadline = deadline_raw
                deadline_year = deadline_date.year
            except:
                pass
        
        # 근무지역 파싱 (시/구 분리 시도)
        city = None
        district = None
        if work_location:
            # "서울시", "대구", "제주" 같은 경우
            if "시" in work_location or "도" in work_location or "특별시" in work_location:
                city = work_location.split()[0] if " " in work_location else work_location
            # "경기도 성남시 분당구" 같은 경우
            elif " " in work_location:
                parts = work_location.split()
                city = parts[0] if len(parts) > 0 else work_location
                district = " ".join(parts[1:]) if len(parts) > 1 else None
        
        return {
            "institution_name": institution_name,
            "work_location": work_location or None,
            "city": city,
            "district": district,
            "deadline": deadline,
            "deadline_year": deadline_year,
            "source": "ARKO",
            "data_source": ["ARKO"],
            "confidence_score": 0.85,  # 과거 데이터이므로 신뢰도 낮음
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "data_year": 2016  # 데이터 시점 명시
        }
    
    def group_by_institution(self, jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """
        기관별로 채용정보 그룹화
        
        Args:
            jobs: 채용정보 데이터 리스트
            
        Returns:
            {기관명: [채용정보 리스트]} 딕셔너리
        """
        institution_jobs = {}
        
        for job in jobs:
            institution_name = job.get("institution_name", "").strip()
            if not institution_name:
                continue
            
            if institution_name not in institution_jobs:
                institution_jobs[institution_name] = []
            
            institution_jobs[institution_name].append(job)
        
        logger.info(f"기관별 그룹화 완료: {len(institution_jobs)}개 기관")
        return institution_jobs

