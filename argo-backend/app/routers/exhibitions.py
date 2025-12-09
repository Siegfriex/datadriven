from fastapi import APIRouter
from app.utils.jsonld import to_jsonld
from app.services.neo4j_service import neo4j_service

router = APIRouter(prefix="/v1/api/exhibitions", tags=["exhibitions"])

@router.get("", response_model=dict)
async def get_exhibitions(limit: int = 20, skip: int = 0):
    query = "MATCH (e:Exhibition) RETURN e SKIP $skip LIMIT $limit"
    results = neo4j_service.execute_query(query, {"skip": skip, "limit": limit})
    data = [r['e'] for r in results]
    return to_jsonld(data)

from app.utils.errors import create_error_response

@router.get("/{exh_id}", response_model=dict)
async def get_exhibition_detail(exh_id: str):
    query = "MATCH (e:Exhibition {id: $id}) RETURN e"
    result = neo4j_service.find_one(query, {"id": exh_id})
    if not result:
        return create_error_response(
            "EXHIBITION_NOT_FOUND",
            f"Exhibition with ID {exh_id} not found",
            status_code=404
        )
    return to_jsonld(result['e'], type_name="Event", id_uri=f"argo://exhibition/{exh_id}")
