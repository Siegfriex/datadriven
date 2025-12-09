from typing import List, Optional, Dict, Any
import logging
from app.services.neo4j_service import neo4j_service
from app.uploaders.neo4j_uploader import Neo4jUploader

logger = logging.getLogger(__name__)

class AnalysisService:
    async def run_gds_centrality(self) -> Dict[str, Any]:
        """
        GDS 중심성 분석 실행 (degree, betweenness, eigenvector)
        
        Returns:
            실행 결과 통계
        """
        try:
            # GDS 프로젝션 및 알고리즘 실행 (gds_projections.cypher 내용)
            # 프로젝션 생성
            projection_query = """
            CALL gds.graph.drop('artist-collaboration-graph', false) YIELD graphName;
            """
            neo4j_service.execute_query(projection_query)
            
            projection_create = """
            CALL gds.graph.project(
              'artist-collaboration-graph',
              'Artist',
              {
                COLLABORATED_WITH: {
                  type: 'COLLABORATED_WITH',
                  orientation: 'UNDIRECTED',
                  properties: ['strength']
                }
              },
              {
                nodeProperties: ['composite_score', 'inst_score', 'acad_score', 'network_score']
              }
            ) YIELD graphName, nodeCount, relationshipCount
            """
            projection_result = neo4j_service.execute_query(projection_create)
            
            if not projection_result:
                return {"error": "Failed to create graph projection"}
            
            # Degree Centrality
            degree_query = """
            CALL gds.degree.write(
              'artist-collaboration-graph',
              {
                writeProperty: 'degree_centrality',
                relationshipWeightProperty: 'strength'
              }
            ) YIELD nodePropertiesWritten
            """
            degree_result = neo4j_service.execute_query(degree_query)
            
            # Betweenness Centrality
            betweenness_query = """
            CALL gds.betweenness.write(
              'artist-collaboration-graph',
              {
                writeProperty: 'betweenness_centrality'
              }
            ) YIELD nodePropertiesWritten
            """
            betweenness_result = neo4j_service.execute_query(betweenness_query)
            
            # Eigenvector Centrality
            eigenvector_query = """
            CALL gds.eigenvector.write(
              'artist-collaboration-graph',
              {
                writeProperty: 'eigenvector_centrality',
                maxIterations: 100
              }
            ) YIELD nodePropertiesWritten
            """
            eigenvector_result = neo4j_service.execute_query(eigenvector_query)
            
            return {
                "projection": projection_result[0] if projection_result else {},
                "degree_updated": degree_result[0].get("nodePropertiesWritten", 0) if degree_result else 0,
                "betweenness_updated": betweenness_result[0].get("nodePropertiesWritten", 0) if betweenness_result else 0,
                "eigenvector_updated": eigenvector_result[0].get("nodePropertiesWritten", 0) if eigenvector_result else 0
            }
            
        except Exception as e:
            logger.error(f"GDS 중심성 분석 실행 중 오류: {e}")
            return {"error": str(e)}
    
    async def run_louvain_community(self) -> Dict[str, Any]:
        """
        Louvain 커뮤니티 탐지 실행
        
        Returns:
            실행 결과 통계
        """
        try:
            # 그래프 프로젝션 확인 (없으면 생성)
            check_projection = """
            CALL gds.graph.exists('artist-collaboration-graph') YIELD exists
            """
            exists_result = neo4j_service.execute_query(check_projection)
            
            if not exists_result or not exists_result[0].get("exists", False):
                # 프로젝션 생성
                await self.run_gds_centrality()
            
            # Louvain 실행
            louvain_query = """
            CALL gds.louvain.write(
              'artist-collaboration-graph',
              {
                writeProperty: 'community_id',
                relationshipWeightProperty: 'strength'
              }
            ) YIELD nodePropertiesWritten, communityCount
            """
            louvain_result = neo4j_service.execute_query(louvain_query)
            
            if louvain_result:
                # Cluster 노드 및 BELONGS_TO 관계 생성
                cluster_sync = Neo4jUploader.sync_clusters_from_gds()
                
                return {
                    "communities_detected": louvain_result[0].get("communityCount", 0),
                    "nodes_updated": louvain_result[0].get("nodePropertiesWritten", 0),
                    "clusters_created": cluster_sync.get("clusters_created", 0),
                    "relationships_created": cluster_sync.get("relationships_created", 0)
                }
            else:
                return {"error": "Louvain algorithm failed"}
                
        except Exception as e:
            logger.error(f"Louvain 커뮤니티 탐지 실행 중 오류: {e}")
            return {"error": str(e)}
    
    async def calculate_structuralist_fields(self) -> Dict[str, Any]:
        """
        구조주의 분석 필드 계산 (capital_composition, dominant_capital, field_quadrant)
        
        Returns:
            계산 결과 통계
        """
        try:
            # structuralist_analysis.cypher 쿼리들을 순차 실행
            
            # 1. Capital Composition
            capital_query = """
            MATCH (a:Artist)
            WHERE a.inst_score IS NOT NULL
              AND a.acad_score IS NOT NULL
              AND a.media_score IS NOT NULL
              AND a.network_score IS NOT NULL
            WITH a,
                 (a.inst_score + a.acad_score + a.media_score + a.network_score) AS total
            WHERE total > 0
            SET a.capital_composition = {
              institutional: round(a.inst_score / total, 4),
              academic: round(a.acad_score / total, 4),
              media: round(a.media_score / total, 4),
              network: round(a.network_score / total, 4)
            }
            RETURN count(a) AS updated_artists
            """
            capital_result = neo4j_service.execute_query(capital_query)
            
            # 2. Dominant Capital
            dominant_query = """
            MATCH (a:Artist)
            WHERE a.capital_composition IS NOT NULL
            WITH a,
                 a.capital_composition.institutional AS inst_ratio,
                 a.capital_composition.academic AS acad_ratio,
                 a.capital_composition.media AS media_ratio,
                 a.capital_composition.network AS network_ratio
            SET a.dominant_capital =
              CASE
                WHEN inst_ratio >= acad_ratio AND inst_ratio >= media_ratio AND inst_ratio >= network_ratio
                  THEN 'institutional'
                WHEN acad_ratio >= inst_ratio AND acad_ratio >= media_ratio AND acad_ratio >= network_ratio
                  THEN 'academic'
                WHEN media_ratio >= inst_ratio AND media_ratio >= acad_ratio AND media_ratio >= network_ratio
                  THEN 'media'
                ELSE 'network'
              END
            RETURN count(a) AS updated_artists
            """
            dominant_result = neo4j_service.execute_query(dominant_query)
            
            # 3. Field Quadrant
            quadrant_query = """
            MATCH (a:Artist)
            WHERE a.inst_score IS NOT NULL AND a.acad_score IS NOT NULL
            WITH percentileDisc(a.inst_score, 0.5) AS inst_median,
                 percentileDisc(a.acad_score, 0.5) AS acad_median
            MATCH (a:Artist)
            WHERE a.inst_score IS NOT NULL AND a.acad_score IS NOT NULL
            SET a.field_quadrant =
              CASE
                WHEN a.inst_score >= inst_median AND a.acad_score >= acad_median
                  THEN 'Q1_established'
                WHEN a.inst_score < inst_median AND a.acad_score >= acad_median
                  THEN 'Q2_academic_elite'
                WHEN a.inst_score >= inst_median AND a.acad_score < acad_median
                  THEN 'Q3_media_star'
                ELSE 'Q4_emerging'
              END
            RETURN count(a) AS updated_artists
            """
            quadrant_result = neo4j_service.execute_query(quadrant_query)
            
            # 4. Network Score 업데이트 (GDS 중심성 기반)
            network_query = """
            MATCH (a:Artist)
            WHERE a.degree_centrality IS NOT NULL
              AND a.betweenness_centrality IS NOT NULL
              AND a.eigenvector_centrality IS NOT NULL
            WITH a,
                 (a.degree_centrality * 0.25 +
                  a.betweenness_centrality * 0.35 +
                  a.eigenvector_centrality * 0.40) * 100 AS raw_network_score
            SET a.network_score = round(CASE
              WHEN raw_network_score > 100 THEN 100
              WHEN raw_network_score < 0 THEN 0
              ELSE raw_network_score
            END, 2)
            RETURN count(a) AS updated_artists
            """
            network_result = neo4j_service.execute_query(network_query)
            
            return {
                "capital_composition_updated": capital_result[0].get("updated_artists", 0) if capital_result else 0,
                "dominant_capital_updated": dominant_result[0].get("updated_artists", 0) if dominant_result else 0,
                "field_quadrant_updated": quadrant_result[0].get("updated_artists", 0) if quadrant_result else 0,
                "network_score_updated": network_result[0].get("updated_artists", 0) if network_result else 0
            }
            
        except Exception as e:
            logger.error(f"구조주의 분석 필드 계산 중 오류: {e}")
            return {"error": str(e)}
    
    async def get_centrality(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Returns top nodes by centrality measures (실제 GDS 계산 결과 사용).
        """
        query = """
        MATCH (a:Artist)
        WHERE a.eigenvector_centrality IS NOT NULL
        RETURN a.id AS id, 
               a.name AS name,
               a.degree_centrality AS degree,
               a.betweenness_centrality AS betweenness,
               a.eigenvector_centrality AS eigenvector
        ORDER BY a.eigenvector_centrality DESC
        LIMIT $limit
        """
        results = neo4j_service.execute_query(query, {"limit": limit})
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "degree": r.get("degree", 0),
                "betweenness": r.get("betweenness", 0),
                "eigenvector": r.get("eigenvector", 0)
            }
            for r in results
        ]

    async def get_communities(self) -> List[Dict[str, Any]]:
        """
        Returns detected communities (Louvain/Leiden).
        """
        query = """
        MATCH (c:Cluster)
        WHERE c.type = 'louvain'
        RETURN c.id AS id, c.name AS name, c.size AS size, c.avg_composite_score AS avg_score
        ORDER BY c.size DESC
        LIMIT 20
        """
        results = neo4j_service.execute_query(query)
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "size": r.get("size", 0),
                "avg_score": r.get("avg_score", 0.0)
            }
            for r in results
        ]

    async def get_field_quadrants(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Segments artists into Bourdieusian field quadrants.
        """
        query = """
        MATCH (a:Artist)
        WHERE a.field_quadrant IS NOT NULL
        RETURN a.field_quadrant AS quadrant,
               a.id AS id,
               a.name AS name,
               a.composite_score AS score,
               a.dominant_capital AS dominant_capital
        ORDER BY a.composite_score DESC
        """
        results = neo4j_service.execute_query(query)
        
        # Quadrant별로 그룹화
        quadrants = {
            "Q1_established": [],
            "Q2_academic_elite": [],
            "Q3_media_star": [],
            "Q4_emerging": []
        }
        
        for r in results:
            quadrant = r.get("quadrant", "Q4_emerging")
            if quadrant in quadrants:
                quadrants[quadrant].append({
                    "id": r["id"],
                    "name": r["name"],
                    "score": r.get("score", 0),
                    "dominant_capital": r.get("dominant_capital", "institutional")
                })
        
        return quadrants

    async def get_correlation_matrix(self) -> Dict[str, Any]:
        """
        Returns correlation matrix of capital types.
        """
        # Mock logic or pre-calculated stats
        return {
            "labels": ["Institutional", "Academic", "Media", "Market"],
            "matrix": [
                [1.0, 0.4, 0.2, 0.1],
                [0.4, 1.0, 0.3, 0.05],
                [0.2, 0.3, 1.0, 0.6],
                [0.1, 0.05, 0.6, 1.0]
            ]
        }

    async def compare_artists(self, artist_ids: List[str]) -> Dict[str, Any]:
        if not artist_ids:
            return {}
        
        query = """
        MATCH (a:Artist)
        WHERE a.id IN $ids
        RETURN a
        """
        results = neo4j_service.execute_query(query, {"ids": artist_ids})
        # Basic comparison return
        return {
            "artists": [r['a'] for r in results],
            "comparison": "Comparison logic placeholder"
        }

analysis_service = AnalysisService()
