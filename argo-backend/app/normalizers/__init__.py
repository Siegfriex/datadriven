"""
데이터 정규화 모듈
수집된 데이터를 ARGO 스키마 형식으로 정규화
"""

from .artist_normalizer import ArtistNormalizer
from .score_calculator import ScoreCalculator

__all__ = ["ArtistNormalizer", "ScoreCalculator"]

