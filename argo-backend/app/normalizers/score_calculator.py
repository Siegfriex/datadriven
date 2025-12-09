"""
4개 레이어 점수 계산 모듈

- inst_score: 제도 레이어
- acad_score: 학술 레이어
- media_score: 담론 레이어
- network_score: 네트워크 레이어
- composite_score: 복합 점수
- composite_confidence: 신뢰도 점수
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ScoreCalculator:
    """
    4개 레이어 점수 계산기
    """
    
    @staticmethod
    def calculate_inst_score(artist_data: Dict) -> float:
        """
        제도 점수 계산
        
        계산식: (museum_count * 20) + (biennale_count * 30) + (support_count * 10)
        범위: 0~100
        """
        museum_count = artist_data.get("museum_exhibitions", 0) or 0
        biennale_count = artist_data.get("biennale_participation", 0) or 0
        support_count = artist_data.get("public_support_count", 0) or 0
        residency_count = artist_data.get("residency_count", 0) or 0
        
        # 비엔날레 참여 횟수는 청주공예비엔날레 등에서 수집한 정보 활용
        # 레지던시 참여 횟수는 MMCA 레지던시작가소식에서 수집한 정보 활용
        # 입상 횟수는 추가 점수로 반영 가능 (향후)
        # 레지던시 참여는 제도적 지원으로 간주 (참여 1회당 10점)
        
        score = (museum_count * 20) + (biennale_count * 30) + (support_count * 10) + (residency_count * 10)
        return min(max(score, 0.0), 100.0)
    
    @staticmethod
    def calculate_acad_score(artist_data: Dict) -> float:
        """
        학술 점수 계산
        
        계산식: (citation_count * 2) + (catalog_count * 5) + (academic_publications * 3)
        범위: 0~100
        
        KCI 논문 정보 반영:
        - academic_publications: KCI 등재 논문 수
        - citation_count: KCI 등재 논문 수 (임시, 향후 실제 인용 수로 대체)
        """
        citation_count = artist_data.get("citation_count", 0) or 0
        catalog_count = artist_data.get("catalog_mentions", 0) or 0
        academic_publications = artist_data.get("academic_publications", 0) or 0
        
        # 논문 수를 학술 점수에 반영 (논문 1개당 3점)
        # 인용 수는 별도로 계산 (인용 1회당 2점)
        score = (citation_count * 2) + (catalog_count * 5) + (academic_publications * 3)
        return min(max(score, 0.0), 100.0)
    
    @staticmethod
    def calculate_media_score(artist_data: Dict) -> float:
        """
        담론 점수 계산
        
        계산식: (article_count * 1) + (sentiment_score * 20)
        범위: 0~100 (음수값은 0으로 절사)
        """
        article_count = artist_data.get("article_count", 0) or 0
        sentiment_score = artist_data.get("sentiment_score", 0.0) or 0.0
        
        score = (article_count * 1) + (sentiment_score * 20)
        return min(max(score, 0.0), 100.0)
    
    @staticmethod
    def calculate_network_score(artist_data: Dict) -> float:
        """
        네트워크 점수 계산
        
        계산식: (collaborators * 5) + (centrality * 40)
        범위: 0~100
        """
        collaborators = artist_data.get("collaborator_count", 0) or 0
        centrality = artist_data.get("centrality", 0.0) or 0.0
        
        score = (collaborators * 5) + (centrality * 40)
        return min(max(score, 0.0), 100.0)
    
    @staticmethod
    def calculate_composite_score(
        inst_score: float,
        acad_score: float,
        media_score: float,
        network_score: float
    ) -> float:
        """
        복합 점수 계산 (가중 평균)
        
        계산식: inst*0.3 + acad*0.2 + media*0.25 + network*0.25
        """
        return round(
            (inst_score * 0.30) +
            (acad_score * 0.20) +
            (media_score * 0.25) +
            (network_score * 0.25),
            2
        )
    
    @staticmethod
    def calculate_confidence_score(artist_data: Dict) -> float:
        """
        신뢰도 점수 계산
        
        구성 요소:
        - source_credibility: 60% (데이터 출처 품질) - 가장 중요
        - data_availability: 25% (기본 정보 존재 여부)
        - verification_level: 15% (수동/자동 검증 여부)
        
        ARKO 데이터는 공식 데이터 소스이므로 기본 정보만 있어도 높은 신뢰도 부여
        """
        # 소스 신뢰도 (가장 중요)
        SOURCE_WEIGHTS = {
            'ARKO': 0.95,  # 공식 데이터 소스
            'MMCA': 0.92,
            'KCI': 0.85,
            'auction': 0.88,
            'web_crawl': 0.70,
        }
        sources = artist_data.get("data_sources", [])
        if not sources:
            sources = [artist_data.get("source", "web_crawl")]
        
        source_scores = [SOURCE_WEIGHTS.get(s, 0.5) for s in sources]
        source_credibility = sum(source_scores) / len(source_scores) if source_scores else 0.5
        
        # 데이터 가용성 (기본 정보 존재 여부)
        # ARKO 데이터는 기본 정보(이름, 분야)만 있어도 충분히 유효
        has_basic_info = bool(artist_data.get("name"))
        # 점수 데이터가 있으면 추가 점수
        has_scores = any([
            artist_data.get("inst_score", 0) > 0,
            artist_data.get("acad_score", 0) > 0,
            artist_data.get("media_score", 0) > 0,
            artist_data.get("network_score", 0) > 0,
        ])
        
        data_availability = 0.5 if has_basic_info else 0.0
        if has_scores:
            data_availability = 1.0
        
        # 검증 수준
        verification_level = 1.0 if artist_data.get("is_verified", False) else 0.8  # ARKO는 공식 소스이므로 기본 0.8
        
        # 복합 신뢰도 (소스 신뢰도 중심)
        confidence = (
            source_credibility * 0.60 +
            data_availability * 0.25 +
            verification_level * 0.15
        )
        
        return round(confidence, 2)
    
    @staticmethod
    def calculate_all_scores(artist_data: Dict) -> Dict:
        """
        모든 점수 계산 (일괄)
        
        Returns:
            {
                "inst_score": float,
                "acad_score": float,
                "media_score": float,
                "network_score": float,
                "composite_score": float,
                "composite_confidence": float
            }
        """
        inst_score = ScoreCalculator.calculate_inst_score(artist_data)
        acad_score = ScoreCalculator.calculate_acad_score(artist_data)
        media_score = ScoreCalculator.calculate_media_score(artist_data)
        network_score = ScoreCalculator.calculate_network_score(artist_data)
        
        composite_score = ScoreCalculator.calculate_composite_score(
            inst_score, acad_score, media_score, network_score
        )
        
        composite_confidence = ScoreCalculator.calculate_confidence_score(artist_data)
        
        return {
            "inst_score": inst_score,
            "acad_score": acad_score,
            "media_score": media_score,
            "network_score": network_score,
            "composite_score": composite_score,
            "composite_confidence": composite_confidence
        }

