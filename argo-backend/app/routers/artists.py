from fastapi import APIRouter, Query, Path, HTTPException
from typing import List, Optional, Dict, Any
from app.services.artist_service import artist_service
from app.models.artist import Artist
from app.utils.errors import create_error_response
from app.utils.jsonld import to_jsonld
from pydantic import BaseModel

router = APIRouter(
    prefix="/v1/api/artists",
    tags=["artists"]
)

@router.get("", response_model=dict)
async def get_artists(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    artists = await artist_service.get_all_artists(limit, skip)
    return to_jsonld([a.model_dump(by_alias=True) for a in artists])

@router.get("/{artist_id}", response_model=dict)
async def get_artist_detail(
    artist_id: str = Path(..., description=" The ID of the artist to retrieve")
):
    artist = await artist_service.get_artist_by_id(artist_id)
    if not artist:
        return create_error_response(
            "ARTIST_NOT_FOUND", 
            f"Artist with ID {artist_id} not found", 
            status_code=404
        )
    
    return to_jsonld(
        artist.model_dump(by_alias=True), 
        type_name="Person",
        id_uri=artist.id
    )

@router.get("/{artist_id}/artworks", response_model=dict)
async def get_artist_artworks(artist_id: str):
    artworks = await artist_service.get_artist_artworks(artist_id)
    return to_jsonld(artworks)

@router.get("/{artist_id}/structural-equivalents", response_model=dict)
async def get_structural_equivalents(artist_id: str):
    equivalents = await artist_service.get_structural_equivalents(artist_id)
    return to_jsonld(equivalents)

@router.get("/{artist_id}/capital-composition", response_model=dict)
async def get_capital_composition(artist_id: str):
    cap = await artist_service.get_capital_composition(artist_id)
    return to_jsonld(cap)

@router.get("/{artist_id}/market", response_model=dict)
async def get_market_info(artist_id: str):
    market = await artist_service.get_market_info(artist_id)
    return to_jsonld(market)

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None

@router.post("/search", response_model=dict)
async def search_artists(request: SearchRequest):
    results = await artist_service.search_artists(request.query, request.filters)
    return to_jsonld([a.model_dump(by_alias=True) for a in results])

@router.get("/{artist_id}/network", response_model=dict)
async def get_artist_network(artist_id: str):
    # TODO: Implement specific network graph Query
    return {"message": "Not implemented yet"}

@router.get("/{artist_id}/exhibitions", response_model=dict)
async def get_artist_exhibitions(artist_id: str):
     # TODO: Resolve this overlap with detail view or make it paginated full list
    return {"message": "Not implemented yet"}
