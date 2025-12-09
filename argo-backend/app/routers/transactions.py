from fastapi import APIRouter
from app.utils.jsonld import to_jsonld
from app.services.neo4j_service import neo4j_service
from app.utils.errors import create_error_response

router = APIRouter(prefix="/v1/api/transactions", tags=["transactions"])

@router.get("", response_model=dict)
async def get_transactions(limit: int = 20, skip: int = 0):
    query = "MATCH (t:Transaction) RETURN t SKIP $skip LIMIT $limit"
    results = neo4j_service.execute_query(query, {"skip": skip, "limit": limit})
    data = [r['t'] for r in results]
    return to_jsonld(data)

@router.get("/{trans_id}", response_model=dict)
async def get_transaction_detail(trans_id: str):
    """
    Get transaction detail by transaction ID.
    Includes related artist and artwork information.
    """
    query = """
    MATCH (t:Transaction {id: $trans_id})
    OPTIONAL MATCH (t)-[:SOLD_IN]->(a:Artist)
    OPTIONAL MATCH (t)-[:FOR_WORK]->(w:Artwork)
    RETURN {
        transaction: {
            id: t.id,
            date: t.date,
            price: t.price,
            currency: t.currency,
            auction_house: t.auction_house
        },
        artist: CASE WHEN a IS NOT NULL THEN {id: a.id, name: a.name} ELSE null END,
        artwork: CASE WHEN w IS NOT NULL THEN {id: w.id, title: w.title} ELSE null END
    } as detail
    """
    result = neo4j_service.find_one(query, {"trans_id": trans_id})
    
    if not result or not result.get("detail") or not result["detail"].get("transaction"):
        return create_error_response(
            "TRANSACTION_NOT_FOUND",
            f"Transaction with ID {trans_id} not found",
            status_code=404
        )
    
    return to_jsonld(result["detail"])

@router.get("/price-history/{artist_id}", response_model=dict)
async def get_artist_price_history(artist_id: str):
    query = """
    MATCH (a:Artist {id: $artist_id})<-[:SOLD_IN]-(t:Transaction)
    RETURN t.date as date, t.price as price, t.currency as currency
    ORDER BY t.date ASC
    """
    results = neo4j_service.execute_query(query, {"artist_id": artist_id})
    # Transform for frontend charting
    history = [
        {"date": r["date"], "price": r["price"], "currency": r["currency"]}
        for r in results
    ]
    return to_jsonld(history)
