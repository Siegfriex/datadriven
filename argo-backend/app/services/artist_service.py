from typing import List, Optional, Dict, Any, Tuple
from app.services.neo4j_service import neo4j_service
from app.services.coordinate_service import calculate_coordinates
from app.models.artist import Artist, Collaboration, InstitutionLink, ExhibitionLink
from app.models.common import Scores, StructuralistAnalysis, Coordinates3D
from app.utils.errors import create_error_response
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class ArtistService:
    def _map_to_artist(self, data: dict) -> Optional[Artist]:
        """
        Maps raw Neo4j result to Artist Pydantic model.
        Assumes data contains 'a' (Artist node) and optional relationships.
        
        Returns:
            Artist 모델 인스턴스 또는 None (검증 실패 시)
        """
        node = data.get('a', {})
        artist_id = node.get('id') or node.get('artist_id')
        
        try:
            # safely extract scores
            scores = Scores(
                inst_score=node.get('inst_score', 0.0),
                acad_score=node.get('acad_score', 0.0),
                media_score=node.get('media_score', 0.0),
                network_score=node.get('network_score', 0.0),
                composite_score=node.get('composite_score', 0.0),
                composite_confidence=node.get('composite_confidence')
            )
            
            # coordinates_3d: Neo4j에서 객체로 저장된 경우 그대로 사용, 없으면 계산
            coords_data = node.get('coordinates_3d')
            if coords_data and isinstance(coords_data, dict):
                coords = coords_data
            else:
                coords = calculate_coordinates(scores)
            
            # Parse relationships
            collaborations = []
            for c in data.get('collaborations', []):
                try:
                    if c.get('strength', 0) >= 0.3:
                        collaborations.append(Collaboration(artist_id=c['id'], strength=c['strength']))
                except ValidationError as e:
                    logger.warning(f"Collaboration 검증 실패 (artist_id={artist_id}): {e.errors()}")
                    continue
            
            institutions = []
            for i in data.get('institutions', []):
                try:
                    institutions.append(InstitutionLink(institution_id=i['id'], name=i['name'], type=i.get('type')))
                except ValidationError as e:
                    logger.warning(f"InstitutionLink 검증 실패 (artist_id={artist_id}): {e.errors()}")
                    continue
            
            exhibitions = []
            for e in data.get('exhibitions', []):
                try:
                    exhibitions.append(ExhibitionLink(exhibition_id=e['id'], name=e['name'], year=e.get('year')))
                except ValidationError as e:
                    logger.warning(f"ExhibitionLink 검증 실패 (artist_id={artist_id}): {e.errors()}")
                    continue

            full_id = f"argo://artist/{artist_id}"

            # Structuralist Analysis
            # Neo4j에서 직접 필드로 저장된 경우와 객체로 저장된 경우 모두 처리
            analysis_data = node.get('structuralist_analysis', {})
            
            # capital_composition: Neo4j에서 MAP으로 저장되거나 객체로 저장됨
            capital_comp = node.get('capital_composition') or analysis_data.get('capital_composition', {})
            if isinstance(capital_comp, dict):
                # Neo4j MAP 형식을 Pydantic이 기대하는 형식으로 변환
                capital_comp_normalized = {
                    "institutional_ratio": capital_comp.get("institutional", 0.0),
                    "academic_ratio": capital_comp.get("academic", 0.0),
                    "media_ratio": capital_comp.get("media", 0.0),
                    "network_ratio": capital_comp.get("network", 0.0)
                }
            else:
                capital_comp_normalized = {}
            
            # structural_position: field_quadrant, community_id 포함
            structural_pos = node.get('structural_position') or analysis_data.get('structural_position', {})
            if not isinstance(structural_pos, dict):
                structural_pos = {}
            
            structural_pos_normalized = {
                "field_quadrant": node.get('field_quadrant') or structural_pos.get('field_quadrant', 'Q4_emerging'),
                "community_id": node.get('community_id') or structural_pos.get('community_id'),
                "position_stability": structural_pos.get('position_stability'),
                "mobility_potential": structural_pos.get('mobility_potential')
            }
            
            structuralist_analysis = StructuralistAnalysis(
                dominant_capital=node.get('dominant_capital') or analysis_data.get('dominant_capital', 'institutional'),
                capital_composition=capital_comp_normalized,
                structural_position=structural_pos_normalized,
                algorithm_version=node.get('algorithm_version') or analysis_data.get('algorithm_version', 'v1.0.0'),
                weights_applied=node.get('weights_applied') or analysis_data.get('weights_applied', {
                    'inst': 0.30, 'acad': 0.20, 'media': 0.25, 'network': 0.25
                }),
                theoretical_basis=node.get('theoretical_basis') or analysis_data.get('theoretical_basis', 'Bourdieu Field Theory + Meta-Analysis')
            )

            return Artist(
                id=full_id,
                type="Person",
                identifier={"@type": "PropertyValue", "value": artist_id},
                name=node.get('name', 'Unknown'),
                # Populate both for compatibility
                alternateName=node.get('name_ko') or node.get('alternateName'),
                alternativeName=node.get('name_ko') or node.get('alternateName'),
                
                birthDate=node.get('birthDate') or (f"{node.get('birth_year')}-01-01" if node.get('birth_year') else None),
                url=node.get('url'),
                
                segment_id=node.get('segment_id'),
                career_stage=node.get('career_stage'),
                
                scores=scores,
                # Init Coordinates3D model from dict (Neo4j에서 객체로 저장된 경우 그대로 사용)
                coordinates_3d=Coordinates3D(**coords) if isinstance(coords, dict) else Coordinates3D(**calculate_coordinates(scores)),
                structuralist_analysis=structuralist_analysis,
                
                collaborations=collaborations,
                institutions=institutions,
                exhibitions=exhibitions,
                
                # Legacy/Frontend comp
                birth_year=node.get('birth_year'),
                artist_id=artist_id,
                collaborators=[c.artist_id for c in collaborations]
            )
        except ValidationError as e:
            logger.error(f"Artist 모델 검증 실패 (artist_id={artist_id}): {e.errors()}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        except Exception as e:
            logger.error(f"Artist 매핑 중 오류 발생 (artist_id={artist_id}): {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    async def get_all_artists(self, limit: int = 20, skip: int = 0) -> List[Artist]:
        query = """
        MATCH (a:Artist)
        RETURN a
        SKIP $skip LIMIT $limit
        """
        results = neo4j_service.execute_query(query, {"skip": skip, "limit": limit})
        
        # For list view, we might not need deep relationships to save perf, 
        # but requirements say coordinates are needed, so we at least need scores (on node).
        artists = [self._map_to_artist(r) for r in results]
        # None 값 필터링 (검증 실패 데이터 제외)
        return [a for a in artists if a is not None]

    async def get_artist_by_id(self, artist_id: str) -> Optional[Artist]:
        """
        Get a single artist by ID with full relationship data.
        """
        query = """
        MATCH (a:Artist {id: $artist_id})
        
        // Get collaborations (COLLABORATED_WITH relationship)
        OPTIONAL MATCH (a)-[r1:COLLABORATED_WITH]->(collab:Artist)
        WITH a, collect({id: collab.id, strength: r1.strength}) as collaborations
        
        // Get institutions (AFFILIATED_WITH relationship)
        OPTIONAL MATCH (a)-[:AFFILIATED_WITH]->(inst:Institution)
        WITH a, collaborations, collect({
            id: inst.id, 
            name: inst.name, 
            type: inst.type 
        }) as institutions
        
        // Get exhibitions (PARTICIPATED_IN relationship)
        OPTIONAL MATCH (a)-[:PARTICIPATED_IN]->(exh:Exhibition)
        WITH a, collaborations, institutions, collect({
            id: exh.id, 
            name: exh.name, 
            year: exh.year
        }) as exhibitions
        
        RETURN a, collaborations, institutions, exhibitions
        """
        result = neo4j_service.find_one(query, {"artist_id": artist_id})
        
        if not result:
            return None
        
        # Merge lists into main result logic
        # The _map_to_artist expects 'a' and optional list keys with specific structures
        # current _map_to_artist definition uses: 
        # data.get('collaborations', []) -> list of objects with 'id'/'strength'
        # data.get('institutions', []) -> list of objects with 'id'/'name'/'type'
        # data.get('exhibitions', []) -> list of objects with 'id'/'name'/'year'
        # The query above returns these exactly as needed.
        return self._map_to_artist(result)

    async def get_artist_artworks(self, artist_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (a:Artist {id: $artist_id})-[:CREATED]->(w:Artwork)
        RETURN w
        """
        results = neo4j_service.execute_query(query, {"artist_id": artist_id})
        return [r['w'] for r in results]

    async def get_structural_equivalents(self, artist_id: str) -> List[Dict[str, Any]]:
        """
        Finds structurally equivalent artists based on shared collaboration patterns.
        Uses Jaccard similarity of neighbors + score proximity.
        """
        query = """
        MATCH (a:Artist {id: $artist_id})
        
        // 1. Get Target Artist's Neighbors
        OPTIONAL MATCH (a)-[r1:COLLABORATED_WITH]->(n)
        WITH a, collect(n.id) as a_neighbors, size(collect(n.id)) as a_degree
        
        // 2. Find Candidates (artists who are not target)
        MATCH (b:Artist) WHERE b.id <> $artist_id
        OPTIONAL MATCH (b)-[r2:COLLABORATED_WITH]->(m)
        WITH a, b, a_neighbors, a_degree, collect(m.id) as b_neighbors, size(collect(m.id)) as b_degree
        
        // 3. Compare Neighborhoods (Jaccard Index)
        WITH a, b, a_neighbors, b_neighbors, a_degree, b_degree,
             size([x IN a_neighbors WHERE x IN b_neighbors]) as intersection
        
        WITH a, b, 
             CASE WHEN (a_degree + b_degree - intersection) > 0 
                  THEN toFloat(intersection) / (a_degree + b_degree - intersection)
                  ELSE 0.0 END as structural_similarity,
             abs(a.composite_score - b.composite_score) as score_diff
        
        // 4. Filter & Sort
        WHERE structural_similarity > 0.1 OR score_diff < 10 // Relaxed threshold for demo
        RETURN b, structural_similarity
        ORDER BY structural_similarity DESC, score_diff ASC
        LIMIT 5
        """
        results = neo4j_service.execute_query(query, {"artist_id": artist_id})
        return [
            {**r['b'], "similarity_score": r['structural_similarity']} 
            for r in results
        ]

    async def get_capital_composition(self, artist_id: str) -> Dict[str, Any]:
        """
        Calculates the ratio of each capital type relative to the total.
        """
        query = """
        MATCH (a:Artist {id: $artist_id})
        RETURN a.inst_score as inst,
               a.acad_score as acad,
               a.media_score as media,
               a.network_score as network,
               a.composite_score as composite
        """
        result = neo4j_service.find_one(query, {"artist_id": artist_id})
        
        if not result:
            return {}
            
        total = sum([
            result.get("inst", 0) or 0,
            result.get("acad", 0) or 0,
            result.get("media", 0) or 0,
            result.get("network", 0) or 0
        ])
        
        if total == 0:
            return {
                "institutional_ratio": 0.0,
                "academic_ratio": 0.0,
                "media_ratio": 0.0,
                "network_ratio": 0.0,
                "composite_score": result.get("composite", 0)
            }
            
        return {
            "institutional_ratio": round((result.get("inst", 0) or 0) / total, 3),
            "academic_ratio": round((result.get("acad", 0) or 0) / total, 3),
            "media_ratio": round((result.get("media", 0) or 0) / total, 3),
            "network_ratio": round((result.get("network", 0) or 0) / total, 3),
            "composite_score": result.get("composite", 0)
        }

    async def get_market_info(self, artist_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (a:Artist {id: $artist_id})<-[:SOLD_IN]-(t:Transaction) 
        RETURN t ORDER BY t.date DESC
        """
        results = neo4j_service.execute_query(query, {"artist_id": artist_id})
        return [r['t'] for r in results]

    async def search_artists(self, query_str: str, filters: Dict[str, Any] = None) -> List[Artist]:
        # Advanced Search with Filters
        where_clauses = [
            "(toLower(a.name) CONTAINS toLower($q) OR toLower(a.name_ko) CONTAINS toLower($q))"
        ]
        params = {"q": query_str}
        
        if filters:
            if filters.get("segment_id"):
                where_clauses.append("a.segment_id = $segment_id")
                params["segment_id"] = filters["segment_id"]
            if filters.get("career_stage"):
                where_clauses.append("a.career_stage = $career_stage")
                params["career_stage"] = filters["career_stage"]
            if filters.get("min_score"):
                where_clauses.append("a.composite_score >= $min_score")
                params["min_score"] = float(filters["min_score"])
            if filters.get("max_score"):
                where_clauses.append("a.composite_score <= $max_score")
                params["max_score"] = float(filters["max_score"])
        
        cypher = f"""
        MATCH (a:Artist)
        WHERE {" AND ".join(where_clauses)}
        RETURN a
        ORDER BY a.composite_score DESC
        LIMIT 20
        """
        results = neo4j_service.execute_query(cypher, params)
        artists = [self._map_to_artist(r) for r in results]
        # None 값 필터링 (검증 실패 데이터 제외)
        return [a for a in artists if a is not None]

artist_service = ArtistService()
