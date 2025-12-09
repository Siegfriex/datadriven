from fastapi import APIRouter, Path, Query
from app.utils.jsonld import to_jsonld
from app.services.neo4j_service import neo4j_service

router = APIRouter(prefix="/v1/api/institutions", tags=["institutions"])

@router.get("", response_model=dict)
async def get_institutions(limit: int = 20, skip: int = 0):
    query = "MATCH (i:Institution) RETURN i SKIP $skip LIMIT $limit"
    results = neo4j_service.execute_query(query, {"skip": skip, "limit": limit})
    # Basic mapping
    data = [r['i'] for r in results]
    return to_jsonld(data)

from app.utils.errors import create_error_response

@router.get("/{inst_id}", response_model=dict)
async def get_institution_detail(inst_id: str):
    query = "MATCH (i:Institution {id: $id}) RETURN i"
    result = neo4j_service.find_one(query, {"id": inst_id})
    if not result:
        return create_error_response(
            "INSTITUTION_NOT_FOUND",
            f"Institution with ID {inst_id} not found",
            status_code=404
        )
    return to_jsonld(result['i'], type_name="Organization", id_uri=f"argo://institution/{inst_id}")

@router.get("/{inst_id}/affiliated-artists", response_model=dict)
async def get_affiliated_artists(inst_id: str):
    query = """
    MATCH (i:Institution {id: $id})<-[:AFFILIATED_WITH]-(a:Artist)
    RETURN a LIMIT 50
    """
    results = neo4j_service.execute_query(query, {"id": inst_id})
    data = [r['a'] for r in results]
    return to_jsonld(data)

@router.get("/{inst_id}/exhibitions", response_model=dict)
async def get_institution_exhibitions(inst_id: str):
    query = """
    MATCH (i:Institution {id: $id})-[:HOSTED]->(e:Exhibition)
    RETURN e ORDER BY e.year DESC LIMIT 50
    """
    results = neo4j_service.execute_query(query, {"id": inst_id})
    data = [r['e'] for r in results]
    return to_jsonld(data)

@router.get("/{inst_id}/benchmarking", response_model=dict)
async def get_institution_benchmarking(inst_id: str):
    """
    Get institution benchmarking compared to similar institutions.
    Returns ranking, percentile, and comparison statistics.
    """
    # Check existence
    inst_check = neo4j_service.find_one(
        "MATCH (i:Institution {id: $id}) RETURN i.id as id, i.type as type, i.score as score",
        {"id": inst_id}
    )
    if not inst_check:
        return create_error_response(
            "INSTITUTION_NOT_FOUND",
            f"Institution with ID {inst_id} not found",
            status_code=404
        )
    
    query = """
    MATCH (i:Institution {id: $id})
    MATCH (other:Institution) 
    WHERE other.type = i.type AND other.id <> i.id
    WITH i, collect(other.score) as peer_scores, count(other) as peer_count
    WITH i, peer_scores, peer_count,
         size([s IN peer_scores WHERE s < i.score]) as rank,
         avg(peer_scores) as avg_score,
         max(peer_scores) as max_score,
         min(peer_scores) as min_score
    RETURN {
        institution: {
            id: i.id,
            name: i.name,
            score: i.score
        },
        benchmarking: {
            rank: rank + 1,
            total_peers: peer_count,
            percentile: CASE WHEN peer_count > 0 
                THEN round((rank * 100.0 / peer_count), 2) 
                ELSE 0 END,
            average_score: avg_score,
            max_score: max_score,
            min_score: min_score
        }
    } as result
    """
    result = neo4j_service.find_one(query, {"id": inst_id})
    return to_jsonld(result.get("result", {}) if result else {})
