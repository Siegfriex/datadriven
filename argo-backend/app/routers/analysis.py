from fastapi import APIRouter, Query
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.analysis_service import analysis_service
from app.utils.jsonld import to_jsonld
from app.utils.errors import create_error_response

router = APIRouter(prefix="/v1/api/analysis", tags=["analysis"])

# Analysis 응답 모델들
class AnalysisResult(BaseModel):
    """분석 결과 기본 모델"""
    pass

class GDSCentralityResult(BaseModel):
    """GDS 중심성 분석 결과"""
    projection: Dict[str, Any] = {}
    degree_updated: int = 0
    betweenness_updated: int = 0
    eigenvector_updated: int = 0

class LouvainResult(BaseModel):
    """Louvain 커뮤니티 탐지 결과"""
    communities_detected: int = 0
    clusters_created: int = 0
    artists_assigned: int = 0

class StructuralistResult(BaseModel):
    """구조주의 분석 결과"""
    artists_updated: int = 0
    capital_composition_calculated: int = 0
    field_quadrants_assigned: int = 0

@router.post("/centrality", response_model=List[Dict[str, Any]])
async def calculate_centrality(limit: int = Query(10, ge=1, le=100)):
    results = await analysis_service.get_centrality(limit)
    return results

@router.post("/community-detection", response_model=List[Dict[str, Any]])
async def detect_communities():
    results = await analysis_service.get_communities()
    return results

@router.get("/correlation", response_model=Dict[str, Any])
async def get_correlation():
    results = await analysis_service.get_correlation_matrix()
    return results

@router.post("/compare", response_model=Dict[str, Any])
async def compare_artists(artist_ids: List[str]):
    results = await analysis_service.compare_artists(artist_ids)
    return results

@router.get("/field-quadrants", response_model=Dict[str, Any])
async def get_field_quadrants():
    results = await analysis_service.get_field_quadrants()
    return results

@router.post("/run-gds-centrality", response_model=GDSCentralityResult)
async def run_gds_centrality():
    """
    GDS 중심성 분석 실행 (degree, betweenness, eigenvector)
    """
    result = await analysis_service.run_gds_centrality()
    if "error" in result:
        return create_error_response(
            "GDS_CENTRALITY_FAILED",
            result["error"],
            status_code=500
        )
    return result

@router.post("/run-louvain", response_model=LouvainResult)
async def run_louvain():
    """
    Louvain 커뮤니티 탐지 실행 및 Cluster 노드 생성
    """
    result = await analysis_service.run_louvain_community()
    if "error" in result:
        return create_error_response(
            "LOUVAIN_FAILED",
            result["error"],
            status_code=500
        )
    return result

@router.post("/calculate-structuralist", response_model=StructuralistResult)
async def calculate_structuralist():
    """
    구조주의 분석 필드 계산 (capital_composition, dominant_capital, field_quadrant)
    """
    result = await analysis_service.calculate_structuralist_fields()
    if "error" in result:
        return create_error_response(
            "STRUCTURALIST_CALCULATION_FAILED",
            result["error"],
            status_code=500
        )
    return result
