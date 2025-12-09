"""
ARGO 데이터 수집 통합 파이프라인

Step 1: 데이터 수집 (ARKO API)
Step 2: 데이터 검증
Step 3: 데이터 정규화
Step 4: 점수 계산
Step 5: 최종 검증
Step 6: Neo4j 업로드
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.collectors.arko_collector import ARKOCollector
from app.collectors.artwork_collector import ArtworkCollector
from app.collectors.institution_collector import InstitutionCollector
from app.collectors.job_collector import JobCollector
from app.collectors.kci_collector import KCICollector
from app.collectors.kci_citation_collector import KCICitationCollector
from app.collectors.cheongju_biennale_collector import CheongjuBiennaleCollector
from app.collectors.mmca_residency_collector import MMCAResidencyCollector
from app.collectors.mmca_collection_collector import MMCACollectionCollector
from app.normalizers.artist_normalizer import ArtistNormalizer
from app.normalizers.score_calculator import ScoreCalculator
from app.validators.data_validator import DataValidator
from app.uploaders.neo4j_uploader import Neo4jUploader


class DataCollectionPipeline:
    """
    데이터 수집 통합 파이프라인
    """
    
    def __init__(self):
        settings = get_settings()
        
        # ARKO API 키 확인
        if not settings.ARKO_API_KEY or not settings.ARKO_SERVICE_KEY:
            raise ValueError(
                "ARKO API 키가 설정되지 않았습니다. "
                ".env 파일에 ARKO_API_KEY와 ARKO_SERVICE_KEY를 설정하세요."
            )
        
        self.arko_collector = ARKOCollector(
            api_key=settings.ARKO_API_KEY,
            service_key=settings.ARKO_SERVICE_KEY
        )
        self.artwork_collector = ArtworkCollector(
            service_key=settings.ARKO_SERVICE_KEY
        )
        self.institution_collector = InstitutionCollector(
            service_key=settings.ARKO_SERVICE_KEY
        )
        self.job_collector = JobCollector(
            service_key=settings.ARKO_SERVICE_KEY
        )
        self.kci_collector = KCICollector(
            service_key=settings.ARKO_SERVICE_KEY
        )
        self.kci_citation_collector = KCICitationCollector(
            service_key=settings.ARKO_SERVICE_KEY
        )
        self.cheongju_biennale_collector = CheongjuBiennaleCollector(
            service_key=settings.ARKO_SERVICE_KEY
        )
        # MMCA 레지던시 API는 별도 키 사용
        mmca_residency_key = settings.MMCA_RESIDENCY_SERVICE_KEY or "0cc9c852-cd3b-417c-91b4-15722d964013"
        self.mmca_residency_collector = MMCAResidencyCollector(
            service_key=mmca_residency_key
        )
        # MMCA 소장작품 API는 별도 키 사용
        mmca_collection_key = settings.MMCA_COLLECTION_SERVICE_KEY or "c080ac2b-93ba-4300-af2d-8cc0ff71dda7"
        self.mmca_collection_collector = MMCACollectionCollector(
            service_key=mmca_collection_key
        )
        self.normalizer = ArtistNormalizer()
        self.score_calculator = ScoreCalculator()
        self.validator = DataValidator()
        self.uploader = Neo4jUploader()
    
    def run(self, target_count: int = 50, dry_run: bool = False):
        """
        파이프라인 실행
        
        Args:
            target_count: 목표 수집 수량
            dry_run: 실제 업로드 없이 테스트만 수행
        """
        logger.info(f"데이터 수집 파이프라인 시작 (목표: {target_count}명, dry_run: {dry_run})")
        
        # Step 1: 데이터 수집
        logger.info("=" * 60)
        logger.info("Step 1: 데이터 수집 시작")
        logger.info("=" * 60)
        raw_artists = self._collect_data(target_count)
        logger.info(f"작가 수집 완료: {len(raw_artists)}명")
        
        # 작품 정보 수집 (작가 점수 계산에 활용)
        # 주의: 전체 작품 수집은 시간이 오래 걸립니다 (약 1분)
        # 테스트 시에는 샘플만 수집하거나 캐싱 사용 권장
        logger.info("작품 정보 수집 시작...")
        # dry_run 모드에서는 샘플만 수집 (시간 절약)
        artwork_limit = 1000 if dry_run else None
        raw_artworks = self._collect_artworks(max_count=artwork_limit)
        logger.info(f"작품 수집 완료: {len(raw_artworks)}개")
        
        # 예술단체 정보 수집 (기관 데이터 보강)
        logger.info("예술단체 정보 수집 시작...")
        raw_institutions = self._collect_institutions()
        logger.info(f"예술단체 수집 완료: {len(raw_institutions)}개")
        
        # 채용정보 수집 (기관 활동성 정보 보강, 선택사항)
        logger.info("채용정보 수집 시작 (기관 정보 보강용)...")
        raw_jobs = self._collect_jobs()
        logger.info(f"채용정보 수집 완료: {len(raw_jobs)}개")
        
        # KCI 논문 정보 수집 (학술 점수 계산에 활용)
        logger.info("KCI 논문 정보 수집 시작 (학술 점수 계산용)...")
        # dry_run 모드에서는 샘플만 수집 (시간 절약)
        kci_limit = 500 if dry_run else None
        raw_papers = self._collect_kci_papers(max_count=kci_limit)
        logger.info(f"KCI 논문 수집 완료: {len(raw_papers)}개")
        
        # KCI 인용 정보 수집 (실제 인용 수 확인용)
        logger.info("KCI 인용 정보 수집 시작 (실제 인용 수 확인용)...")
        # dry_run 모드에서는 샘플만 수집 (시간 절약, 응답 시간이 길 수 있음)
        citation_limit = 200 if dry_run else None
        raw_citations = self._collect_kci_citations(max_count=citation_limit)
        logger.info(f"KCI 인용 정보 수집 완료: {len(raw_citations)}개")
        
        # 청주공예비엔날레 데이터 수집 (비엔날레 참여 정보)
        logger.info("청주공예비엔날레 데이터 수집 시작 (비엔날레 참여 정보용)...")
        # dry_run 모드에서는 샘플만 수집
        biennale_limit = 100 if dry_run else None
        raw_biennale_works = self._collect_cheongju_biennale(max_count=biennale_limit)
        logger.info(f"청주공예비엔날레 데이터 수집 완료: {len(raw_biennale_works)}개")
        
        # MMCA 레지던시작가소식 수집 (레지던시 참여 정보)
        logger.info("MMCA 레지던시작가소식 수집 시작 (레지던시 참여 정보용)...")
        # dry_run 모드에서는 샘플만 수집
        residency_limit = 100 if dry_run else None
        raw_residency_news = self._collect_mmca_residency(max_count=residency_limit)
        logger.info(f"MMCA 레지던시작가소식 수집 완료: {len(raw_residency_news)}개")
        
        # MMCA 소장작품 수집 (소장작품 정보)
        logger.info("MMCA 소장작품 수집 시작 (소장작품 정보용)...")
        # dry_run 모드에서는 샘플만 수집
        collection_limit = 200 if dry_run else None
        raw_collection_works = self._collect_mmca_collection(max_count=collection_limit)
        logger.info(f"MMCA 소장작품 수집 완료: {len(raw_collection_works)}개")
        
        # Step 2: 데이터 정규화
        logger.info("=" * 60)
        logger.info("Step 2: 데이터 정규화 시작")
        logger.info("=" * 60)
        normalized_artists = self._normalize_data(raw_artists)
        logger.info(f"정규화 완료: {len(normalized_artists)}명")
        
        # Step 3: 점수 계산 (작품 정보, 논문 정보, 인용 정보, 비엔날레 정보, 레지던시 정보, 소장작품 정보 활용)
        logger.info("=" * 60)
        logger.info("Step 3: 점수 계산 시작")
        logger.info("=" * 60)
        scored_artists = self._calculate_scores(
            normalized_artists, raw_artworks, raw_papers, raw_citations, raw_biennale_works, raw_residency_news, raw_collection_works
        )
        logger.info(f"점수 계산 완료: {len(scored_artists)}명")
        
        # Step 4: 데이터 검증
        logger.info("=" * 60)
        logger.info("Step 4: 데이터 검증 시작 (Pydantic 모델 검증)")
        logger.info("=" * 60)
        validated_artists, failed_artists = self._validate_data(scored_artists)
        logger.info(f"검증 완료: 통과 {len(validated_artists)}명, 실패 {len(failed_artists)}명")
        
        # 검증 실패 데이터 저장 (디버깅용)
        if failed_artists:
            failed_file = f"data/validation_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("data", exist_ok=True)
            with open(failed_file, "w", encoding="utf-8") as f:
                json.dump(failed_artists, f, ensure_ascii=False, indent=2)
            logger.warning(f"검증 실패 데이터 저장: {failed_file}")
        
        # Step 5: 최종 검증 (신뢰도 0.60 이상만)
        logger.info("=" * 60)
        logger.info("Step 5: 최종 검증 시작 (신뢰도 >= 0.50)")
        logger.info("=" * 60)
        final_artists = self._final_validation(validated_artists)
        logger.info(f"최종 검증 완료: {len(final_artists)}명")
        
        # 결과 저장
        output_file = f"data/collected_artists_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("data", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_artists, f, ensure_ascii=False, indent=2)
        logger.info(f"결과 저장: {output_file}")
        
        # Step 6: Neo4j 업로드 (dry_run이 아닐 때만)
        if not dry_run:
            logger.info("=" * 60)
            logger.info("Step 6: Neo4j 업로드 시작")
            logger.info("=" * 60)
            
            # 6.1: Artist 노드 업로드
            logger.info("6.1: Artist 노드 업로드 중...")
            upload_result = self._upload_to_neo4j(final_artists)
            logger.info(f"Artist 업로드 완료: 성공 {upload_result['success']}명, 실패 {upload_result['failed']}명")
            
            # 6.2: Institution 노드 업로드
            logger.info("6.2: Institution 노드 업로드 중...")
            if raw_institutions:
                inst_result = self._upload_institutions_to_neo4j(raw_institutions)
                logger.info(f"Institution 업로드 완료: 성공 {inst_result['success']}개, 실패 {inst_result['failed']}개")
            
            # 6.3: Exhibition 노드 업로드 (비엔날레 데이터에서)
            logger.info("6.3: Exhibition 노드 업로드 중...")
            if raw_biennale_works:
                exh_result = self._upload_exhibitions_to_neo4j(raw_biennale_works)
                logger.info(f"Exhibition 업로드 완료: 성공 {exh_result['success']}개, 실패 {exh_result['failed']}개")
            
            # 6.4: 관계 생성 (선택사항, 향후 확장)
            # TODO: KCI 공동저자 관계, 작가-기관 관계, 작가-전시 관계 생성
            logger.info("6.4: 관계 생성은 향후 구현 예정")
            
        else:
            logger.info("=" * 60)
            logger.info("Step 6: Neo4j 업로드 건너뜀 (dry_run 모드)")
            logger.info("=" * 60)
        
        logger.info("=" * 60)
        logger.info("파이프라인 완료!")
        logger.info("=" * 60)
        
        return {
            "collected": len(raw_artists),
            "normalized": len(normalized_artists),
            "scored": len(scored_artists),
            "validated": len(validated_artists),
            "final": len(final_artists),
            "failed": len(failed_artists),
            "artworks_collected": len(raw_artworks) if 'raw_artworks' in locals() else 0,
            "institutions_collected": len(raw_institutions) if 'raw_institutions' in locals() else 0,
            "jobs_collected": len(raw_jobs) if 'raw_jobs' in locals() else 0,
            "papers_collected": len(raw_papers) if 'raw_papers' in locals() else 0,
            "citations_collected": len(raw_citations) if 'raw_citations' in locals() else 0,
            "biennale_works_collected": len(raw_biennale_works) if 'raw_biennale_works' in locals() else 0,
            "residency_news_collected": len(raw_residency_news) if 'raw_residency_news' in locals() else 0,
            "collection_works_collected": len(raw_collection_works) if 'raw_collection_works' in locals() else 0,
            "output_file": output_file
        }
    
    def _collect_data(self, target_count: int) -> List[Dict]:
        """Step 1: 작가 데이터 수집"""
        return self.arko_collector.collect_all(max_count=target_count)
    
    def _collect_artworks(self, max_count: Optional[int] = None) -> List[Dict]:
        """Step 1: 작품 데이터 수집 (테스트용으로 제한 가능)"""
        try:
            # 테스트 모드에서는 샘플만 수집 (시간 절약)
            if max_count is None:
                # 전체 수집은 시간이 오래 걸리므로, 작가 이름 매칭에 필요한 만큼만
                # 실제로는 작가 이름으로 필터링하거나 캐싱 사용 권장
                logger.info("작품 정보 전체 수집 시작 (시간이 걸릴 수 있습니다)...")
            return self.artwork_collector.collect_all(max_count=max_count)
        except Exception as e:
            logger.warning(f"작품 정보 수집 실패 (계속 진행): {e}")
            return []
    
    def _collect_institutions(self) -> List[Dict]:
        """Step 1: 예술단체 데이터 수집"""
        try:
            return self.institution_collector.collect_all()
        except Exception as e:
            logger.warning(f"예술단체 정보 수집 실패 (계속 진행): {e}")
            return []
    
    def _collect_jobs(self) -> List[Dict]:
        """Step 1: 채용정보 데이터 수집 (기관 정보 보강용, 선택사항)"""
        try:
            # 2016년 데이터이므로 선택적으로 수집
            return self.job_collector.collect_all()
        except Exception as e:
            logger.warning(f"채용정보 수집 실패 (계속 진행): {e}")
            return []
    
    def _collect_kci_papers(self, max_count: Optional[int] = None) -> List[Dict]:
        """Step 1: KCI 논문 데이터 수집 (학술 점수 계산용)"""
        try:
            # 미술 관련 논문만 필터링하여 수집
            return self.kci_collector.collect_all(max_count=max_count, filter_art_related=True)
        except Exception as e:
            logger.warning(f"KCI 논문 정보 수집 실패 (계속 진행): {e}")
            return []
    
    def _collect_kci_citations(self, max_count: Optional[int] = None) -> List[Dict]:
        """Step 1: KCI 인용 정보 데이터 수집 (실제 인용 수 확인용)"""
        try:
            # 미술 관련 저자만 필터링하여 수집
            return self.kci_citation_collector.collect_author_citations(
                max_count=max_count, 
                filter_art_related=True
            )
        except Exception as e:
            logger.warning(f"KCI 인용 정보 수집 실패 (계속 진행): {e}")
            return []
    
    def _collect_cheongju_biennale(self, max_count: Optional[int] = None) -> List[Dict]:
        """Step 1: 청주공예비엔날레 데이터 수집 (비엔날레 참여 정보용)"""
        try:
            return self.cheongju_biennale_collector.collect_all_artist_works(max_count=max_count)
        except Exception as e:
            logger.warning(f"청주공예비엔날레 데이터 수집 실패 (계속 진행): {e}")
            return []
    
    def _collect_mmca_residency(self, max_count: Optional[int] = None) -> List[Dict]:
        """Step 1: MMCA 레지던시작가소식 데이터 수집 (레지던시 참여 정보용)"""
        try:
            return self.mmca_residency_collector.collect_all(max_count=max_count)
        except Exception as e:
            logger.warning(f"MMCA 레지던시작가소식 수집 실패 (계속 진행): {e}")
            return []
    
    def _collect_mmca_collection(self, max_count: Optional[int] = None) -> List[Dict]:
        """Step 1: MMCA 소장작품 데이터 수집 (소장작품 정보용)"""
        try:
            return self.mmca_collection_collector.collect_all(max_count=max_count)
        except Exception as e:
            logger.warning(f"MMCA 소장작품 수집 실패 (계속 진행): {e}")
            return []
    
    def _normalize_data(self, artists: List[Dict]) -> List[Dict]:
        """Step 2: 데이터 정규화"""
        normalized = []
        
        for idx, raw_artist in enumerate(artists):
            try:
                # ARKO 데이터 정규화
                argo_artist = self.arko_collector.normalize_artist_data(raw_artist)
                
                # 이름 정규화
                name_info = self.normalizer.normalize_name(
                    argo_artist.get("name", ""),
                    argo_artist.get("alternateName")
                )
                argo_artist.update(name_info)
                
                # segment_id 생성
                segment_id = self.normalizer.normalize_segment_id(argo_artist.get("genre"))
                if segment_id:
                    argo_artist["segment_id"] = segment_id
                
                # artist_id 생성
                artist_id = f"arko_{idx + 1:04d}"
                argo_artist["artist_id"] = artist_id
                argo_artist["id"] = f"argo://artist/{artist_id}"
                
                # identifier 생성
                argo_artist["identifier"] = self.normalizer.normalize_identifier(artist_id)
                
                normalized.append(argo_artist)
                
            except Exception as e:
                logger.error(f"데이터 정규화 실패 ({raw_artist.get('이름', 'Unknown')}): {e}")
                continue
        
        return normalized
    
    def _calculate_scores(
        self, 
        artists: List[Dict], 
        artworks: List[Dict] = None,
        papers: List[Dict] = None,
        citations: List[Dict] = None,
        biennale_works: List[Dict] = None,
        residency_news: List[Dict] = None,
        collection_works: List[Dict] = None
    ) -> List[Dict]:
        """Step 3: 점수 계산 (작품 정보 및 논문 정보 활용)"""
        scored = []
        
        # 작가별 작품 수 계산 (제도 점수에 활용)
        artist_artwork_count = {}
        if artworks:
            normalized_artworks = [self.artwork_collector.normalize_artwork_data(a) for a in artworks]
            artist_groups = self.artwork_collector.group_by_artist(normalized_artworks)
            artist_artwork_count = {name: len(artworks_list) for name, artworks_list in artist_groups.items()}
            logger.info(f"작가별 작품 수 계산 완료: {len(artist_artwork_count)}명")
        
        # 작가별 논문 수 계산 (학술 점수에 활용)
        artist_paper_count = {}
        artist_citation_count = {}
        if papers:
            # 논문 정규화
            normalized_papers = [self.kci_collector.normalize_paper_data(p) for p in papers]
            
            # 작가 이름 리스트 추출
            artist_names = [a.get("name", "").strip() for a in artists]
            artist_names.extend([a.get("name_ko", "").strip() for a in artists])
            artist_names = [n for n in artist_names if n]
            
            # 작가-논문 매칭
            matched_papers = self.kci_collector.match_artists_to_papers(artist_names, normalized_papers)
            
            # 작가별 논문 수 및 인용 수 집계
            for artist_name, matched_paper_list in matched_papers.items():
                if matched_paper_list:
                    artist_paper_count[artist_name] = len(matched_paper_list)
                    # 등재구분이 KCI 등재인 논문 수를 인용 수로 간주 (임시)
                    kci_registered_count = sum(
                        1 for p in matched_paper_list 
                        if p.get("is_kci_registered", False)
                    )
                    artist_citation_count[artist_name] = kci_registered_count
            
            logger.info(f"작가별 논문 수 계산 완료: {len(artist_paper_count)}명")
        
        for artist in artists:
            try:
                # 작가 이름으로 작품 수 매칭
                artist_name = artist.get("name", "").strip()
                artist_name_ko = artist.get("name_ko", "").strip()
                
                # 작품 수 찾기 (한글 이름 또는 영문 이름으로 매칭)
                artwork_count = 0
                for name_key, count in artist_artwork_count.items():
                    if name_key == artist_name or name_key == artist_name_ko:
                        artwork_count = count
                        break
                
                # 작품 수를 제도 점수 계산에 반영
                if artwork_count > 0:
                    artist["public_artwork_count"] = artwork_count
                    # 건축물 미술작품 설치 = 제도 레이어 활동
                    artist["museum_exhibitions"] = artwork_count  # 임시로 museum_exhibitions에 반영
                
                # 논문 수 및 인용 수 매칭
                paper_count = 0
                citation_count = 0
                h_index = 0
                
                # 한글 이름으로 매칭 시도
                if artist_name in artist_paper_count:
                    paper_count = artist_paper_count[artist_name]
                    citation_count = artist_citation_count.get(artist_name, 0)
                elif artist_name_ko in artist_paper_count:
                    paper_count = artist_paper_count[artist_name_ko]
                    citation_count = artist_citation_count.get(artist_name_ko, 0)
                
                # 논문 정보를 학술 점수 계산에 반영
                if paper_count > 0:
                    artist["academic_publications"] = paper_count
                    # KCI 등재 논문 수를 인용 수로 간주 (임시, 인용 정보가 없을 경우)
                    if citation_count > 0:
                        artist["citation_count"] = citation_count
                
                # KCI 인용 정보에서 실제 인용 수 매칭 (우선순위 높음)
                if citations:
                    normalized_citations = [
                        self.kci_citation_collector.normalize_author_citation_data(c) 
                        for c in citations
                    ]
                    artist_names = [artist_name, artist_name_ko]
                    matched_citations = self.kci_citation_collector.match_artists_to_citations(
                        artist_names, normalized_citations
                    )
                    
                    # 매칭된 인용 정보가 있으면 실제 인용 수 사용
                    for matched_name, citation_data in matched_citations.items():
                        if matched_name in [artist_name, artist_name_ko]:
                            # 실제 인용 수로 업데이트 (더 정확함)
                            actual_citations = citation_data.get("total_citations", 0)
                            if actual_citations > 0:
                                artist["citation_count"] = actual_citations
                                artist["h_index"] = citation_data.get("h_index", 0)
                                artist["average_citations"] = citation_data.get("average_citations", 0.0)
                                artist["self_citations"] = citation_data.get("self_citations", 0)
                                # 논문 수도 인용 정보에서 가져온 것이 더 정확할 수 있음
                                actual_papers = citation_data.get("total_papers", 0)
                                if actual_papers > 0:
                                    artist["academic_publications"] = actual_papers
                            break
                
                # KCI 데이터 소스 추가
                if paper_count > 0:
                    if "KCI" not in artist.get("data_source", []):
                        data_sources = artist.get("data_source", [])
                        data_sources.append("KCI")
                        artist["data_source"] = data_sources
                
                # 청주공예비엔날레 참여 정보 매칭 (제도 점수에 활용)
                biennale_participation_count = 0
                biennale_award_count = 0
                
                if biennale_works:
                    normalized_biennale_works = [
                        self.cheongju_biennale_collector.normalize_artist_work_data(w) 
                        for w in biennale_works
                    ]
                    artist_names = [artist_name, artist_name_ko]
                    matched_biennale = self.cheongju_biennale_collector.match_artists_to_biennale(
                        artist_names, normalized_biennale_works
                    )
                    
                    # 매칭된 비엔날레 정보가 있으면 참여 횟수 및 입상 횟수 사용
                    for matched_name, biennale_info in matched_biennale.items():
                        if matched_name in [artist_name, artist_name_ko]:
                            biennale_participation_count = biennale_info.get("participation_count", 0)
                            biennale_award_count = biennale_info.get("award_count", 0)
                            
                            # 비엔날레 참여 정보를 제도 점수 계산에 반영
                            if biennale_participation_count > 0:
                                artist["biennale_participation"] = biennale_participation_count
                                artist["biennale_awards"] = biennale_award_count
                            
                            # 청주공예비엔날레 데이터 소스 추가
                            if "CHEONGJU_BIENNALE" not in artist.get("data_source", []):
                                data_sources = artist.get("data_source", [])
                                data_sources.append("CHEONGJU_BIENNALE")
                                artist["data_source"] = data_sources
                            break
                
                # MMCA 레지던시 참여 정보 매칭 (제도 점수에 활용)
                residency_count = 0
                
                if residency_news:
                    normalized_residency_news = [
                        self.mmca_residency_collector.normalize_residency_data(n) 
                        for n in residency_news
                    ]
                    artist_names = [artist_name, artist_name_ko]
                    matched_residency = self.mmca_residency_collector.match_artists_to_residency(
                        artist_names, normalized_residency_news
                    )
                    
                    # 매칭된 레지던시 정보가 있으면 참여 횟수 사용
                    for matched_name, residency_info in matched_residency.items():
                        if matched_name in [artist_name, artist_name_ko]:
                            residency_count = residency_info.get("residency_count", 0)
                            
                            # 레지던시 참여 정보를 제도 점수 계산에 반영
                            if residency_count > 0:
                                artist["residency_count"] = residency_count
                                # 레지던시 참여는 제도 레이어 활동
                                # residency_count를 public_support_count에 반영 (임시)
                                current_support = artist.get("public_support_count", 0) or 0
                                artist["public_support_count"] = current_support + residency_count
                            
                            # MMCA 레지던시 데이터 소스 추가
                            if "MMCA_RESIDENCY" not in artist.get("data_source", []):
                                data_sources = artist.get("data_source", [])
                                data_sources.append("MMCA_RESIDENCY")
                                artist["data_source"] = data_sources
                            break
                
                # MMCA 소장작품 정보 매칭 (제도 점수에 활용)
                collection_count = 0
                
                if collection_works:
                    normalized_collection_works = [
                        self.mmca_collection_collector.normalize_collection_data(w) 
                        for w in collection_works
                    ]
                    artist_names = [artist_name, artist_name_ko]
                    matched_collection = self.mmca_collection_collector.match_artists_to_collection(
                        artist_names, normalized_collection_works
                    )
                    
                    # 매칭된 소장작품 정보가 있으면 소장작품 수 사용
                    for matched_name, collection_info in matched_collection.items():
                        if matched_name in [artist_name, artist_name_ko]:
                            collection_count = collection_info.get("collection_count", 0)
                            
                            # 소장작품 정보를 제도 점수 계산에 반영
                            if collection_count > 0:
                                artist["mmca_collection_count"] = collection_count
                                # 국립현대미술관 소장은 제도적 인정의 최고 지표
                                # 소장작품 수를 museum_exhibitions에 반영 (임시)
                                current_museum = artist.get("museum_exhibitions", 0) or 0
                                artist["museum_exhibitions"] = current_museum + collection_count
                            
                            # MMCA 소장작품 데이터 소스 추가
                            if "MMCA_COLLECTION" not in artist.get("data_source", []):
                                data_sources = artist.get("data_source", [])
                                data_sources.append("MMCA_COLLECTION")
                                artist["data_source"] = data_sources
                            break
                
                # 모든 점수 계산
                scores = self.score_calculator.calculate_all_scores(artist)
                artist.update(scores)
                
                scored.append(artist)
                
            except Exception as e:
                logger.error(f"점수 계산 실패 ({artist.get('name', 'Unknown')}): {e}")
                continue
        
        return scored
    
    def _validate_data(self, artists: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        """Step 4: 데이터 검증 (Pydantic 모델 사용)"""
        from app.models.artist import Artist
        from app.models.common import Scores, Coordinates3D, StructuralistAnalysis
        from app.services.coordinate_service import calculate_coordinates
        from pydantic import ValidationError
        
        passed = []
        failed = []
        
        for artist_data in artists:
            try:
                # 1. Scores 모델 검증
                scores = Scores(
                    inst_score=artist_data.get("inst_score", 0.0),
                    acad_score=artist_data.get("acad_score", 0.0),
                    media_score=artist_data.get("media_score", 0.0),
                    network_score=artist_data.get("network_score", 0.0),
                    composite_score=artist_data.get("composite_score", 0.0),
                    composite_confidence=artist_data.get("composite_confidence") or artist_data.get("confidence_score")
                )
                
                # 2. Coordinates3D 모델 검증 (좌표 계산)
                coords = calculate_coordinates(scores)
                coordinates_3d = Coordinates3D(**coords)
                
                # 3. StructuralistAnalysis 모델 검증 (있는 경우)
                structuralist_analysis = None
                if artist_data.get("structuralist_analysis") or artist_data.get("dominant_capital"):
                    # capital_composition 정규화
                    capital_comp = artist_data.get("capital_composition", {})
                    if isinstance(capital_comp, dict):
                        capital_comp_normalized = {
                            "institutional_ratio": capital_comp.get("institutional", capital_comp.get("institutional_ratio", 0.0)),
                            "academic_ratio": capital_comp.get("academic", capital_comp.get("academic_ratio", 0.0)),
                            "media_ratio": capital_comp.get("media", capital_comp.get("media_ratio", 0.0)),
                            "network_ratio": capital_comp.get("network", capital_comp.get("network_ratio", 0.0))
                        }
                    else:
                        capital_comp_normalized = {}
                    
                    # structural_position 정규화
                    structural_pos = artist_data.get("structural_position", {})
                    if not isinstance(structural_pos, dict):
                        structural_pos = {}
                    
                    structural_pos_normalized = {
                        "field_quadrant": artist_data.get("field_quadrant") or structural_pos.get("field_quadrant", "Q4_emerging"),
                        "community_id": artist_data.get("community_id") or structural_pos.get("community_id"),
                        "position_stability": structural_pos.get("position_stability"),
                        "mobility_potential": structural_pos.get("mobility_potential")
                    }
                    
                    structuralist_analysis = StructuralistAnalysis(
                        dominant_capital=artist_data.get("dominant_capital", "institutional"),
                        capital_composition=capital_comp_normalized,
                        structural_position=structural_pos_normalized,
                        algorithm_version=artist_data.get("algorithm_version", "v1.0.0"),
                        weights_applied=artist_data.get("weights_applied", {
                            "inst": 0.30, "acad": 0.20, "media": 0.25, "network": 0.25
                        }),
                        theoretical_basis=artist_data.get("theoretical_basis", "Bourdieu Field Theory + Meta-Analysis")
                    )
                
                # 4. identifier 준비
                identifier_data = artist_data.get("identifier")
                if isinstance(identifier_data, dict):
                    identifier = identifier_data
                else:
                    # identifier가 없으면 artist_id로 생성
                    artist_id = artist_data.get("artist_id") or artist_data.get("id", "").replace("argo://artist/", "")
                    identifier = {"@type": "PropertyValue", "value": artist_id}
                
                # 5. Artist 모델 전체 검증
                artist = Artist(
                    id=artist_data.get("id", f"argo://artist/{artist_data.get('artist_id', 'unknown')}"),
                    type="Person",
                    identifier=identifier,
                    name=artist_data.get("name", "Unknown"),
                    alternateName=artist_data.get("alternateName"),
                    alternativeName=artist_data.get("name_ko") or artist_data.get("alternateName"),
                    birthDate=artist_data.get("birthDate"),
                    url=artist_data.get("url"),
                    segment_id=artist_data.get("segment_id"),
                    career_stage=artist_data.get("career_stage"),
                    birth_year=artist_data.get("birth_year"),
                    artist_id=artist_data.get("artist_id"),
                    scores=scores,
                    coordinates_3d=coordinates_3d,
                    structuralist_analysis=structuralist_analysis,
                    collaborations=[],  # 관계는 별도 처리
                    institutions=[],
                    exhibitions=[],
                    collaborators=[]
                )
                
                # 검증 통과: Pydantic 모델을 dict로 변환하여 반환
                validated_dict = artist.model_dump(by_alias=True)
                # 원본 데이터의 추가 필드 유지 (Pydantic 모델에 없는 필드)
                for key, value in artist_data.items():
                    if key not in validated_dict:
                        validated_dict[key] = value
                passed.append(validated_dict)
                
            except ValidationError as e:
                logger.warning(f"Pydantic 검증 실패 ({artist_data.get('name', 'Unknown')}):")
                logger.warning(f"  오류: {e.errors()}")
                failed.append(artist_data)
            except Exception as e:
                logger.error(f"검증 중 오류 발생 ({artist_data.get('name', 'Unknown')}): {e}")
                import traceback
                logger.error(traceback.format_exc())
                failed.append(artist_data)
        
        logger.info(f"Pydantic 검증 완료: 통과 {len(passed)}명, 실패 {len(failed)}명")
        return passed, failed
    
    def _final_validation(self, artists: List[Dict]) -> List[Dict]:
        """Step 5: 최종 검증 (신뢰도 0.50 이상만, ARKO는 기본 정보만 있어도 0.95 신뢰도)"""
        return [
            a for a in artists 
            if (a.get("composite_confidence") or a.get("confidence_score", 0)) >= 0.50
        ]
    
    def _upload_to_neo4j(self, artists: List[Dict]) -> Dict[str, int]:
        """Step 6.1: Artist 노드 Neo4j 업로드"""
        return self.uploader.upload_artists(artists)
    
    def _upload_institutions_to_neo4j(self, institutions: List[Dict]) -> Dict[str, int]:
        """Step 6.2: Institution 노드 Neo4j 업로드"""
        success_count = 0
        failed_count = 0
        
        for inst in institutions:
            # 기본 정규화 (필요시 확장)
            normalized_inst = {
                "id": inst.get("id"),
                "name": inst.get("단체명") or inst.get("name"),
                "name_en": inst.get("name_en"),
                "type": inst.get("type", "arts_group"),
                "region": inst.get("region"),
                "address": inst.get("address"),
                "prestige_score": inst.get("prestige_score", 0.0),
                "data_source": "ARKO",
                "url": inst.get("관련페이지주소") or inst.get("url"),
                "representative": inst.get("대표명") or inst.get("representative")
            }
            
            if self.uploader.upload_institution(normalized_inst):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(institutions)
        }
    
    def _upload_exhibitions_to_neo4j(self, biennale_works: List[Dict]) -> Dict[str, int]:
        """Step 6.3: Exhibition 노드 Neo4j 업로드 (비엔날레 데이터에서)"""
        success_count = 0
        failed_count = 0
        
        # 비엔날레별로 그룹화하여 Exhibition 노드 생성
        biennale_years = {}
        for work in biennale_works:
            year = work.get("year") or work.get("비엔날레연도")
            if year:
                if year not in biennale_years:
                    biennale_years[year] = {
                        "id": f"exh_cheongju_biennale_{year}",
                        "title": f"청주공예비엔날레 {year}",
                        "type": "biennale",
                        "year": int(year) if isinstance(year, str) else year,
                        "venue": "청주",
                        "data_source": "CHEONGJU_BIENNALE"
                    }
                biennale_years[year]["participant_count"] = biennale_years[year].get("participant_count", 0) + 1
        
        for exh_data in biennale_years.values():
            if self.uploader.upload_exhibition(exh_data):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(biennale_years)
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ARGO 데이터 수집 파이프라인")
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="수집할 작가 수 (기본: 50)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 업로드 없이 테스트만 수행"
    )
    
    args = parser.parse_args()
    
    try:
        pipeline = DataCollectionPipeline()
        result = pipeline.run(target_count=args.count, dry_run=args.dry_run)
        
        print("\n" + "=" * 60)
        print("수집 결과 요약")
        print("=" * 60)
        print(f"수집: {result['collected']}명")
        print(f"정규화: {result['normalized']}명")
        print(f"점수 계산: {result['scored']}명")
        print(f"검증 통과: {result['validated']}명")
        print(f"최종: {result['final']}명")
        print(f"실패: {result['failed']}명")
        print(f"\n추가 데이터:")
        print(f"  작품 정보: {result.get('artworks_collected', 0)}개")
        print(f"  예술단체: {result.get('institutions_collected', 0)}개")
        print(f"  채용정보: {result.get('jobs_collected', 0)}개")
        print(f"\n결과 파일: {result['output_file']}")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"파이프라인 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

