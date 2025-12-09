from fastapi import APIRouter, Query
from typing import List
from app.services.analysis_service import analysis_service
from app.utils.jsonld import to_jsonld

router = APIRouter(prefix="/v1/api/analysis", tags=["analysis"])

@router.post("/centrality", response_model=dict)
async def calculate_centrality(limit: int = Query(10, ge=1, le=100)):
    results = await analysis_service.get_centrality(limit)
    return to_jsonld(results)

@router.post("/community-detection", response_model=dict)
async def detect_communities():
    results = await analysis_service.get_communities()
    return to_jsonld(results)

@router.get("/correlation", response_model=dict)
async def get_correlation():
    results = await analysis_service.get_correlation_matrix()
    return to_jsonld(results)

@router.post("/compare", response_model=dict)
async def compare_artists(artist_ids: List[str]):
    results = await analysis_service.compare_artists(artist_ids)
    return to_jsonld(results)

@router.get("/field-quadrants", response_model=dict)
async def get_field_quadrants():
    results = await analysis_service.get_field_quadrants()
    return to_jsonld(results)
