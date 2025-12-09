from fastapi import APIRouter, Query
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.services.neo4j_service import neo4j_service
from app.services.artist_service import artist_service
from app.models.artist import Artist
from app.models.entities import Cluster
from app.utils.jsonld import to_jsonld
from app.utils.errors import create_error_response

router = APIRouter(tags=["galaxy"])

class PageMetadata(BaseModel):
    limit: int
    skip: int
    has_more: bool

class GalaxyMetadata(BaseModel):
    version: str
    timestamp: str
    total_artists: int
    page: PageMetadata

class GalaxySnapshot(BaseModel):
    artists: List[Dict[str, Any]]  # Artist 모델의 dict 표현
    clusters: List[Dict[str, Any]]  # Cluster 모델의 dict 표현
    metadata: GalaxyMetadata

@router.get("/v1/api/galaxy-snapshot", response_model=GalaxySnapshot)
async def get_galaxy_snapshot(
    limit: int = Query(100, ge=1, le=1000), 
    skip: int = Query(0, ge=0)
):
    """
    Get a snapshot of the galaxy, primarily for 3D visualization.
    Returns a collection of artists (with coordinates) and clusters.
    """
    # Optimized count query
    count_query = "MATCH (a:Artist) RETURN count(a) as total"
    total_result = neo4j_service.find_one(count_query)
    total_artists = total_result.get("total", 0) if total_result else 0

    # Fetch artists 
    artists = await artist_service.get_all_artists(limit=limit, skip=skip)
    
    # Fetch clusters with member count (Optimized)
    cluster_query = """
    MATCH (c:Cluster)
    OPTIONAL MATCH (c)<-[:BELONGS_TO]-(a:Artist)
    RETURN c, count(a) as member_count
    ORDER BY member_count DESC LIMIT 50
    """
    cluster_results = neo4j_service.execute_query(cluster_query)
    clusters = [
        {**r['c'], "member_count": r['member_count']} 
        for r in cluster_results
    ]

    return {
        "artists": [a.model_dump(by_alias=True) for a in artists],
        "clusters": clusters,
        "metadata": {
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_artists": total_artists,
            "page": {
                "limit": limit,
                "skip": skip,
                "has_more": (skip + limit) < total_artists
            }
        }
    }

@router.get("/v1/api/metadata/sources", response_model=Dict[str, Any])
async def get_metadata_sources():
    """
    Get statistics about data sources.
    """
    query = """
    MATCH (a:Artist)
    WHERE a.source IS NOT NULL
    RETURN a.source as source, count(a) as count
    ORDER BY count DESC
    """
    results = neo4j_service.execute_query(query)
    
    # Fallback if empty (e.g. init state)
    if not results:
        sources = [
            {"name": "ARKO", "count": 0, "last_updated": datetime.utcnow().isoformat() + "Z"},
            {"name": "KCI", "count": 0, "last_updated": datetime.utcnow().isoformat() + "Z"},
            {"name": "web_crawl", "count": 0, "last_updated": datetime.utcnow().isoformat() + "Z"}
        ]
    else:
        sources = [
            {
                "name": r["source"], 
                "count": r["count"], 
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
            for r in results
        ]
    
    return to_jsonld(sources, type_name="DataSources")
