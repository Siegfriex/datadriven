from fastapi import APIRouter
from app.utils.jsonld import to_jsonld
from app.services.neo4j_service import neo4j_service
from app.utils.errors import create_error_response

router = APIRouter(prefix="/v1/api/clusters", tags=["clusters"])

@router.get("", response_model=dict)
async def get_clusters(limit: int = 20, skip: int = 0):
    query = "MATCH (c:Cluster) RETURN c SKIP $skip LIMIT $limit"
    results = neo4j_service.execute_query(query, {"skip": skip, "limit": limit})
    data = [r['c'] for r in results]
    return to_jsonld(data)

@router.get("/{cluster_id}", response_model=dict)
async def get_cluster_detail(cluster_id: str):
    return create_error_response(
        "NOT_IMPLEMENTED",
        "Cluster detail endpoint is not implemented yet",
        status_code=501
    )
