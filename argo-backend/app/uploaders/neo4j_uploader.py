"""
Neo4j 데이터 업로드 모듈

수집 및 정규화된 데이터를 Neo4j에 업로드
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from app.services.neo4j_service import neo4j_service
from app.services.coordinate_service import calculate_coordinates
from app.models.common import Scores

logger = logging.getLogger(__name__)


class Neo4jUploader:
    """
    Neo4j 데이터 업로드 클래스
    """
    
    @staticmethod
    def generate_artist_id(name: str, index: int) -> str:
        """
        작가 ID 생성
        
        Args:
            name: 작가 이름
            index: 인덱스 번호
            
        Returns:
            artist_id (예: "artist_001")
        """
        # 이름에서 영문자/숫자만 추출하여 ID 생성
        import re
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        if not clean_name:
            clean_name = "artist"
        
        return f"{clean_name}_{index:03d}"
    
    @staticmethod
    def upload_artist(artist_data: Dict[str, Any]) -> bool:
        """
        단일 작가 데이터 업로드 (Pydantic 검증 필수)
        
        Args:
            artist_data: 정규화된 작가 데이터 (Pydantic Artist 모델로 검증됨)
            
        Returns:
            업로드 성공 여부
        """
        from app.models.artist import Artist
        from app.models.common import Coordinates3D, StructuralistAnalysis
        from pydantic import ValidationError
        
        try:
            # Pydantic 모델로 검증 (업로드 전)
            # 1. Scores 검증
            scores = Scores(
                inst_score=artist_data.get("inst_score", 0.0),
                acad_score=artist_data.get("acad_score", 0.0),
                media_score=artist_data.get("media_score", 0.0),
                network_score=artist_data.get("network_score", 0.0),
                composite_score=artist_data.get("composite_score", 0.0),
                composite_confidence=artist_data.get("composite_confidence") or artist_data.get("confidence_score")
            )
            
            # 2. Coordinates3D 검증
            coords = calculate_coordinates(scores)
            coordinates_3d = Coordinates3D(**coords)
            
            # 3. StructuralistAnalysis 검증 (있는 경우)
            structuralist_analysis_data = None
            if artist_data.get("structuralist_analysis") or artist_data.get("dominant_capital"):
                capital_comp = artist_data.get("capital_composition", {})
                if isinstance(capital_comp, dict):
                    capital_comp_normalized = {
                        "institutional_ratio": capital_comp.get("institutional", capital_comp.get("institutional_ratio", 0.0)),
                        "academic_ratio": capital_comp.get("academic", capital_comp.get("academic_ratio", 0.0)),
                        "media_ratio": capital_comp.get("media", capital_comp.get("media_ratio", 0.0)),
                        "network_ratio": capital_comp.get("network", capital_comp.get("network_ratio", 0.0))
                    }
                else:
                    capital_comp_normalized = {}
                
                structural_pos = artist_data.get("structural_position", {})
                if not isinstance(structural_pos, dict):
                    structural_pos = {}
                
                structural_pos_normalized = {
                    "field_quadrant": artist_data.get("field_quadrant") or structural_pos.get("field_quadrant", "Q4_emerging"),
                    "community_id": artist_data.get("community_id") or structural_pos.get("community_id"),
                    "position_stability": structural_pos.get("position_stability"),
                    "mobility_potential": structural_pos.get("mobility_potential")
                }
                
                structuralist_analysis_data = StructuralistAnalysis(
                    dominant_capital=artist_data.get("dominant_capital", "institutional"),
                    capital_composition=capital_comp_normalized,
                    structural_position=structural_pos_normalized,
                    algorithm_version=artist_data.get("algorithm_version", "v1.0.0"),
                    weights_applied=artist_data.get("weights_applied", {
                        "inst": 0.30, "acad": 0.20, "media": 0.25, "network": 0.25
                    }),
                    theoretical_basis=artist_data.get("theoretical_basis", "Bourdieu Field Theory + Meta-Analysis")
                )
            
            # 4. identifier 준비
            identifier_data = artist_data.get("identifier")
            if isinstance(identifier_data, dict):
                identifier = identifier_data
            else:
                artist_id = artist_data.get("artist_id") or artist_data.get("id", "").replace("argo://artist/", "")
                identifier = {"@type": "PropertyValue", "value": artist_id}
            
            # 5. Artist 모델 전체 검증
            artist = Artist(
                id=artist_data.get("id", f"argo://artist/{artist_data.get('artist_id', 'unknown')}"),
                type="Person",
                identifier=identifier,
                name=artist_data.get("name", "Unknown"),
                alternateName=artist_data.get("alternateName"),
                alternativeName=artist_data.get("name_ko") or artist_data.get("alternateName"),
                birthDate=artist_data.get("birthDate"),
                url=artist_data.get("url"),
                segment_id=artist_data.get("segment_id"),
                career_stage=artist_data.get("career_stage"),
                birth_year=artist_data.get("birth_year"),
                artist_id=artist_data.get("artist_id"),
                scores=scores,
                coordinates_3d=coordinates_3d,
                structuralist_analysis=structuralist_analysis_data,
                collaborations=[],
                institutions=[],
                exhibitions=[],
                collaborators=[]
            )
            
            # 검증 통과: Neo4j 업로드 진행
            # 작가 ID 생성 또는 사용
            artist_id = artist_data.get("artist_id") or artist_data.get("id")
            if not artist_id:
                # 이름 기반 ID 생성
                artist_id = Neo4jUploader.generate_artist_id(
                    artist_data.get("name", "unknown"),
                    hash(artist_data.get("name", "")) % 10000
                )
            
            # ISO 형식 타임스탬프 생성 (datetime() 함수 대신)
            now_iso = datetime.utcnow().isoformat() + "Z"
            collected_at = artist_data.get("collected_at", now_iso)
            
            # Neo4j 쿼리 생성
            query = """
            MERGE (a:Artist {id: $artist_id})
            SET a.name = $name,
                a.name_ko = $name_ko,
                a.alternateName = $alternateName,
                a.birth_year = $birth_year,
                a.birthDate = $birthDate,
                a.url = $url,
                a.segment_id = $segment_id,
                a.career_stage = $career_stage,
                a.genre = $genre,
                a.inst_score = $inst_score,
                a.acad_score = $acad_score,
                a.media_score = $media_score,
                a.network_score = $network_score,
                a.composite_score = $composite_score,
                a.composite_confidence = $composite_confidence,
                a.coordinates_3d = $coordinates_3d,
                a.structuralist_analysis = $structuralist_analysis,
                a.metadata = $metadata,
                a.updated_at = $updated_at
            RETURN a
            """
            
            params = {
                "artist_id": artist_id,
                "name": artist_data.get("name"),
                "name_ko": artist_data.get("name_ko") or artist_data.get("name"),
                "alternateName": artist_data.get("alternateName"),
                "birth_year": artist_data.get("birth_year"),
                "birthDate": artist_data.get("birthDate"),
                "url": artist_data.get("url"),
                "segment_id": artist_data.get("segment_id"),
                "career_stage": artist_data.get("career_stage"),
                "genre": artist_data.get("genre"),
                "inst_score": scores.inst_score,
                "acad_score": scores.acad_score,
                "media_score": scores.media_score,
                "network_score": scores.network_score,
                "composite_score": scores.composite_score,
                "composite_confidence": scores.composite_confidence,
                "coordinates_3d": coords,
                "structuralist_analysis": artist_data.get("structuralist_analysis"),
                "metadata": {
                    "data_source": artist_data.get("data_sources", [artist_data.get("source", "ARKO")]),
                    "confidence_score": artist_data.get("composite_confidence") or artist_data.get("confidence_score", 0.95),
                    "collected_at": collected_at,
                    "verified": artist_data.get("is_verified", False)
                },
                "updated_at": now_iso
            }
            
            result = neo4j_service.execute_query(query, params)
            
            if result:
                logger.info(f"작가 업로드 성공: {artist_id} ({artist_data.get('name')})")
                return True
            else:
                logger.warning(f"작가 업로드 실패: {artist_id}")
                return False
                
        except ValidationError as e:
            logger.error(f"업로드 전 Pydantic 검증 실패 ({artist_data.get('name', 'Unknown')}): {e.errors()}")
            return False
        except Exception as e:
            logger.error(f"작가 업로드 중 오류 발생 ({artist_data.get('name')}): {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def upload_artists(artists: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        배치 작가 데이터 업로드 (Pydantic 검증 포함)
        
        Args:
            artists: 정규화된 작가 데이터 리스트
            
        Returns:
            {
                "success": int,              # 업로드 성공 수
                "validation_failed": int,     # 검증 실패 수
                "upload_failed": int,         # 업로드 실패 수
                "total": int                  # 전체 수
            }
        """
        from app.models.artist import Artist
        from app.models.common import Scores, Coordinates3D, StructuralistAnalysis
        from app.services.coordinate_service import calculate_coordinates
        from pydantic import ValidationError
        
        validated = []
        validation_failed = []
        
        # 1단계: 배치 검증 (검증 실패 데이터 사전 필터링)
        logger.info(f"배치 검증 시작: {len(artists)}명")
        for artist_data in artists:
            try:
                # Scores 검증
                scores = Scores(
                    inst_score=artist_data.get("inst_score", 0.0),
                    acad_score=artist_data.get("acad_score", 0.0),
                    media_score=artist_data.get("media_score", 0.0),
                    network_score=artist_data.get("network_score", 0.0),
                    composite_score=artist_data.get("composite_score", 0.0),
                    composite_confidence=artist_data.get("composite_confidence") or artist_data.get("confidence_score")
                )
                
                # Coordinates3D 검증
                coords = calculate_coordinates(scores)
                coordinates_3d = Coordinates3D(**coords)
                
                # StructuralistAnalysis 검증 (있는 경우)
                structuralist_analysis_data = None
                if artist_data.get("structuralist_analysis") or artist_data.get("dominant_capital"):
                    capital_comp = artist_data.get("capital_composition", {})
                    if isinstance(capital_comp, dict):
                        capital_comp_normalized = {
                            "institutional_ratio": capital_comp.get("institutional", capital_comp.get("institutional_ratio", 0.0)),
                            "academic_ratio": capital_comp.get("academic", capital_comp.get("academic_ratio", 0.0)),
                            "media_ratio": capital_comp.get("media", capital_comp.get("media_ratio", 0.0)),
                            "network_ratio": capital_comp.get("network", capital_comp.get("network_ratio", 0.0))
                        }
                    else:
                        capital_comp_normalized = {}
                    
                    structural_pos = artist_data.get("structural_position", {})
                    if not isinstance(structural_pos, dict):
                        structural_pos = {}
                    
                    structural_pos_normalized = {
                        "field_quadrant": artist_data.get("field_quadrant") or structural_pos.get("field_quadrant", "Q4_emerging"),
                        "community_id": artist_data.get("community_id") or structural_pos.get("community_id"),
                        "position_stability": structural_pos.get("position_stability"),
                        "mobility_potential": structural_pos.get("mobility_potential")
                    }
                    
                    structuralist_analysis_data = StructuralistAnalysis(
                        dominant_capital=artist_data.get("dominant_capital", "institutional"),
                        capital_composition=capital_comp_normalized,
                        structural_position=structural_pos_normalized,
                        algorithm_version=artist_data.get("algorithm_version", "v1.0.0"),
                        weights_applied=artist_data.get("weights_applied", {
                            "inst": 0.30, "acad": 0.20, "media": 0.25, "network": 0.25
                        }),
                        theoretical_basis=artist_data.get("theoretical_basis", "Bourdieu Field Theory + Meta-Analysis")
                    )
                
                # identifier 준비
                identifier_data = artist_data.get("identifier")
                if isinstance(identifier_data, dict):
                    identifier = identifier_data
                else:
                    artist_id = artist_data.get("artist_id") or artist_data.get("id", "").replace("argo://artist/", "")
                    identifier = {"@type": "PropertyValue", "value": artist_id}
                
                # Artist 모델 전체 검증
                artist = Artist(
                    id=artist_data.get("id", f"argo://artist/{artist_data.get('artist_id', 'unknown')}"),
                    type="Person",
                    identifier=identifier,
                    name=artist_data.get("name", "Unknown"),
                    alternateName=artist_data.get("alternateName"),
                    alternativeName=artist_data.get("name_ko") or artist_data.get("alternateName"),
                    birthDate=artist_data.get("birthDate"),
                    url=artist_data.get("url"),
                    segment_id=artist_data.get("segment_id"),
                    career_stage=artist_data.get("career_stage"),
                    birth_year=artist_data.get("birth_year"),
                    artist_id=artist_data.get("artist_id"),
                    scores=scores,
                    coordinates_3d=coordinates_3d,
                    structuralist_analysis=structuralist_analysis_data,
                    collaborations=[],
                    institutions=[],
                    exhibitions=[],
                    collaborators=[]
                )
                
                # 검증 통과: dict로 변환하여 저장
                validated_dict = artist.model_dump(by_alias=True)
                # 원본 데이터의 추가 필드 유지
                for key, value in artist_data.items():
                    if key not in validated_dict:
                        validated_dict[key] = value
                validated.append(validated_dict)
                
            except ValidationError as e:
                logger.warning(f"배치 검증 실패 ({artist_data.get('name', 'Unknown')}): {e.errors()}")
                validation_failed.append(artist_data)
            except Exception as e:
                logger.error(f"배치 검증 중 오류 발생 ({artist_data.get('name', 'Unknown')}): {e}")
                validation_failed.append(artist_data)
        
        logger.info(f"배치 검증 완료: 통과 {len(validated)}명, 실패 {len(validation_failed)}명")
        
        # 검증 실패 데이터 저장 (디버깅용)
        if validation_failed:
            import os
            import json
            failed_file = f"data/upload_validation_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("data", exist_ok=True)
            with open(failed_file, "w", encoding="utf-8") as f:
                json.dump(validation_failed, f, ensure_ascii=False, indent=2)
            logger.warning(f"업로드 검증 실패 데이터 저장: {failed_file}")
        
        # 2단계: 업로드 (검증 통과 데이터만)
        success_count = 0
        upload_failed = 0
        
        logger.info(f"배치 업로드 시작: {len(validated)}명")
        for artist_data in validated:
            if Neo4jUploader.upload_artist(artist_data):
                success_count += 1
            else:
                upload_failed += 1
        
        logger.info(f"배치 업로드 완료: 성공 {success_count}명, 실패 {upload_failed}명")
        
        return {
            "success": success_count,
            "validation_failed": len(validation_failed),
            "upload_failed": upload_failed,
            "total": len(artists)
        }
    
    @staticmethod
    def upload_institution(inst_data: Dict[str, Any]) -> bool:
        """
        단일 Institution 노드 업로드
        
        Args:
            inst_data: 정규화된 기관 데이터
            
        Returns:
            업로드 성공 여부
        """
        try:
            inst_id = inst_data.get("id") or inst_data.get("inst_id")
            if not inst_id:
                import re
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', inst_data.get("name", "unknown").lower())
                inst_id = f"inst_{clean_name}_{hash(inst_data.get('name', '')) % 10000:03d}"
            
            now_iso = datetime.utcnow().isoformat() + "Z"
            
            query = """
            MERGE (i:Institution {id: $id})
            SET i.name = $name,
                i.name_en = $name_en,
                i.type = $type,
                i.region = $region,
                i.address = $address,
                i.prestige_score = $prestige_score,
                i.data_source = $data_source,
                i.url = $url,
                i.representative = $representative,
                i.collected_at = $collected_at
            RETURN i
            """
            
            params = {
                "id": inst_id,
                "name": inst_data.get("name"),
                "name_en": inst_data.get("name_en"),
                "type": inst_data.get("type") or inst_data.get("institution_type"),
                "region": inst_data.get("region"),
                "address": inst_data.get("address"),
                "prestige_score": inst_data.get("prestige_score", 0.0),
                "data_source": inst_data.get("data_source", "ARKO"),
                "url": inst_data.get("url"),
                "representative": inst_data.get("representative"),
                "collected_at": inst_data.get("collected_at", now_iso)
            }
            
            result = neo4j_service.execute_query(query, params)
            
            if result:
                logger.info(f"Institution 업로드 성공: {inst_id} ({inst_data.get('name')})")
                return True
            else:
                logger.warning(f"Institution 업로드 실패: {inst_id}")
                return False
                
        except Exception as e:
            logger.error(f"Institution 업로드 중 오류 발생 ({inst_data.get('name')}): {e}")
            return False
    
    @staticmethod
    def upload_exhibition(exh_data: Dict[str, Any]) -> bool:
        """
        단일 Exhibition 노드 업로드
        
        Args:
            exh_data: 정규화된 전시 데이터
            
        Returns:
            업로드 성공 여부
        """
        try:
            exh_id = exh_data.get("id") or exh_data.get("exh_id")
            if not exh_id:
                import re
                clean_title = re.sub(r'[^a-zA-Z0-9]', '', exh_data.get("title", "unknown").lower())
                year = exh_data.get("year", datetime.now().year)
                exh_id = f"exh_{clean_title}_{year}_{hash(exh_data.get('title', '')) % 1000:03d}"
            
            now_iso = datetime.utcnow().isoformat() + "Z"
            
            query = """
            MERGE (e:Exhibition {id: $id})
            SET e.title = $title,
                e.type = $type,
                e.year = $year,
                e.start_date = $start_date,
                e.end_date = $end_date,
                e.venue = $venue,
                e.participant_count = $participant_count,
                e.significance = $significance,
                e.data_source = $data_source,
                e.collected_at = $collected_at
            RETURN e
            """
            
            params = {
                "id": exh_id,
                "title": exh_data.get("title") or exh_data.get("name"),
                "type": exh_data.get("type") or exh_data.get("exhibition_type"),
                "year": exh_data.get("year"),
                "start_date": exh_data.get("start_date"),
                "end_date": exh_data.get("end_date"),
                "venue": exh_data.get("venue"),
                "participant_count": exh_data.get("participant_count", 0),
                "significance": exh_data.get("significance"),
                "data_source": exh_data.get("data_source", "ARKO"),
                "collected_at": exh_data.get("collected_at", now_iso)
            }
            
            result = neo4j_service.execute_query(query, params)
            
            if result:
                logger.info(f"Exhibition 업로드 성공: {exh_id} ({exh_data.get('title')})")
                return True
            else:
                logger.warning(f"Exhibition 업로드 실패: {exh_id}")
                return False
                
        except Exception as e:
            logger.error(f"Exhibition 업로드 중 오류 발생 ({exh_data.get('title')}): {e}")
            return False
    
    @staticmethod
    def upload_cluster(cluster_data: Dict[str, Any]) -> bool:
        """
        단일 Cluster 노드 업로드
        
        Args:
            cluster_data: 클러스터 데이터
            
        Returns:
            업로드 성공 여부
        """
        try:
            cluster_id = cluster_data.get("id") or cluster_data.get("cluster_id")
            if not cluster_id:
                cluster_id = f"cluster_{cluster_data.get('type', 'louvain')}_{hash(cluster_data.get('name', '')) % 10000:03d}"
            
            now_iso = datetime.utcnow().isoformat() + "Z"
            
            query = """
            MERGE (c:Cluster {id: $id})
            SET c.name = $name,
                c.type = $type,
                c.size = $size,
                c.avg_composite_score = $avg_composite_score,
                c.dominant_genre = $dominant_genre,
                c.center_x = $center_x,
                c.center_y = $center_y,
                c.center_z = $center_z,
                c.algorithm_version = $algorithm_version,
                c.created_at = $created_at
            RETURN c
            """
            
            center = cluster_data.get("center", {})
            
            params = {
                "id": cluster_id,
                "name": cluster_data.get("name"),
                "type": cluster_data.get("type", "louvain"),
                "size": cluster_data.get("size", 0),
                "avg_composite_score": cluster_data.get("avg_composite_score", 0.0),
                "dominant_genre": cluster_data.get("dominant_genre"),
                "center_x": center.get("x", 0.0),
                "center_y": center.get("y", 0.0),
                "center_z": center.get("z", 0.0),
                "algorithm_version": cluster_data.get("algorithm_version", "v1.0.0"),
                "created_at": cluster_data.get("created_at", now_iso)
            }
            
            result = neo4j_service.execute_query(query, params)
            
            if result:
                logger.info(f"Cluster 업로드 성공: {cluster_id} ({cluster_data.get('name')})")
                return True
            else:
                logger.warning(f"Cluster 업로드 실패: {cluster_id}")
                return False
                
        except Exception as e:
            logger.error(f"Cluster 업로드 중 오류 발생 ({cluster_data.get('name')}): {e}")
            return False
    
    @staticmethod
    def create_collaboration(artist_id_1: str, artist_id_2: str,
                            strength: float = 0.5,
                            collaboration_count: int = 1,
                            collaboration_type: str = "co_exhibition",
                            years: Optional[List[int]] = None,
                            last_collaboration: Optional[int] = None) -> bool:
        """
        작가 간 협력 관계 생성
        
        Args:
            artist_id_1: 첫 번째 작가 ID
            artist_id_2: 두 번째 작가 ID
            strength: 관계 강도 (0.0-1.0)
            collaboration_count: 협업 횟수
            collaboration_type: 협업 유형
            years: 협업 연도 리스트
            last_collaboration: 마지막 협업 연도
            
        Returns:
            생성 성공 여부
        """
        try:
            query = """
            MATCH (a1:Artist {id: $artist_id_1})
            MATCH (a2:Artist {id: $artist_id_2})
            WHERE a1.id < a2.id
            MERGE (a1)-[r:COLLABORATED_WITH]->(a2)
            SET r.strength = $strength,
                r.collaboration_count = $collaboration_count,
                r.collaboration_type = $collaboration_type,
                r.years = $years,
                r.last_collaboration = $last_collaboration
            RETURN r
            """
            
            params = {
                "artist_id_1": artist_id_1,
                "artist_id_2": artist_id_2,
                "strength": strength,
                "collaboration_count": collaboration_count,
                "collaboration_type": collaboration_type,
                "years": years or [],
                "last_collaboration": last_collaboration
            }
            
            result = neo4j_service.execute_query(query, params)
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"협력 관계 생성 중 오류 발생 ({artist_id_1} <-> {artist_id_2}): {e}")
            return False
    
    @staticmethod
    def create_affiliation(artist_id: str, institution_id: str,
                          role: str = "affiliated_artist",
                          start_year: Optional[int] = None,
                          end_year: Optional[int] = None,
                          is_current: bool = False) -> bool:
        """
        작가-기관 소속 관계 생성
        
        Args:
            artist_id: 작가 ID
            institution_id: 기관 ID
            role: 역할
            start_year: 시작 연도
            end_year: 종료 연도
            is_current: 현재 소속 여부
            
        Returns:
            생성 성공 여부
        """
        try:
            query = """
            MATCH (a:Artist {id: $artist_id})
            MATCH (i:Institution {id: $institution_id})
            MERGE (a)-[r:AFFILIATED_WITH]->(i)
            SET r.role = $role,
                r.start_year = $start_year,
                r.end_year = $end_year,
                r.is_current = $is_current,
                r.tenure_years = CASE WHEN $start_year IS NOT NULL AND $end_year IS NOT NULL 
                                     THEN $end_year - $start_year 
                                     ELSE NULL END
            RETURN r
            """
            
            params = {
                "artist_id": artist_id,
                "institution_id": institution_id,
                "role": role,
                "start_year": start_year,
                "end_year": end_year,
                "is_current": is_current
            }
            
            result = neo4j_service.execute_query(query, params)
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"소속 관계 생성 중 오류 발생 ({artist_id} -> {institution_id}): {e}")
            return False
    
    @staticmethod
    def create_participation(artist_id: str, exhibition_id: str,
                            role: str = "artist",
                            artworks_count: int = 1,
                            award: Optional[str] = None) -> bool:
        """
        작가-전시 참여 관계 생성
        
        Args:
            artist_id: 작가 ID
            exhibition_id: 전시 ID
            role: 역할
            artworks_count: 작품 수
            award: 수상 정보
            
        Returns:
            생성 성공 여부
        """
        try:
            query = """
            MATCH (a:Artist {id: $artist_id})
            MATCH (e:Exhibition {id: $exhibition_id})
            MERGE (a)-[r:PARTICIPATED_IN]->(e)
            SET r.role = $role,
                r.artworks_count = $artworks_count,
                r.award = $award
            RETURN r
            """
            
            params = {
                "artist_id": artist_id,
                "exhibition_id": exhibition_id,
                "role": role,
                "artworks_count": artworks_count,
                "award": award
            }
            
            result = neo4j_service.execute_query(query, params)
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"참여 관계 생성 중 오류 발생 ({artist_id} -> {exhibition_id}): {e}")
            return False
    
    @staticmethod
    def create_belongs_to(artist_id: str, cluster_id: str,
                          membership_strength: float = 0.5,
                          distance_to_center: float = 0.0) -> bool:
        """
        작가-클러스터 소속 관계 생성
        
        Args:
            artist_id: 작가 ID
            cluster_id: 클러스터 ID
            membership_strength: 소속 강도 (0.0-1.0)
            distance_to_center: 중심까지 거리
            
        Returns:
            생성 성공 여부
        """
        try:
            query = """
            MATCH (a:Artist {id: $artist_id})
            MATCH (c:Cluster {id: $cluster_id})
            MERGE (a)-[r:BELONGS_TO]->(c)
            SET r.membership_strength = $membership_strength,
                r.distance_to_center = $distance_to_center
            RETURN r
            """
            
            params = {
                "artist_id": artist_id,
                "cluster_id": cluster_id,
                "membership_strength": membership_strength,
                "distance_to_center": distance_to_center
            }
            
            result = neo4j_service.execute_query(query, params)
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"소속 관계 생성 중 오류 발생 ({artist_id} -> {cluster_id}): {e}")
            return False
    
    @staticmethod
    def sync_clusters_from_gds() -> Dict[str, Any]:
        """
        GDS Louvain 결과로 Cluster 노드 및 BELONGS_TO 관계 생성
        
        Returns:
            생성 통계
        """
        try:
            # 1. community_id 별 통계 계산 및 Cluster 노드 생성
            query_clusters = """
            MATCH (a:Artist)
            WHERE a.community_id IS NOT NULL
            WITH a.community_id AS community_id,
                 count(a) AS size,
                 avg(a.composite_score) AS avg_score,
                 collect(DISTINCT a.genre)[0..1] AS genres
            MERGE (c:Cluster {id: 'cluster_' + toString(community_id)})
            SET c.name = 'Community ' + toString(community_id),
                c.type = 'louvain',
                c.size = size,
                c.avg_composite_score = round(avg_score, 2),
                c.dominant_genre = genres[0],
                c.algorithm_version = 'v1.0.0',
                c.created_at = toString(datetime())
            RETURN c.id AS cluster_id, size
            """
            
            cluster_results = neo4j_service.execute_query(query_clusters)
            
            # 2. BELONGS_TO 관계 생성
            query_belongs = """
            MATCH (a:Artist)
            WHERE a.community_id IS NOT NULL
            MATCH (c:Cluster {id: 'cluster_' + toString(a.community_id)})
            MERGE (a)-[r:BELONGS_TO]->(c)
            SET r.membership_strength = 1.0,
                r.distance_to_center = 0.0
            RETURN count(r) AS relationships_created
            """
            
            belongs_results = neo4j_service.execute_query(query_belongs)
            
            cluster_count = len(cluster_results)
            relationship_count = belongs_results[0].get("relationships_created", 0) if belongs_results else 0
            
            logger.info(f"Cluster 동기화 완료: {cluster_count}개 클러스터, {relationship_count}개 관계")
            
            return {
                "clusters_created": cluster_count,
                "relationships_created": relationship_count
            }
            
        except Exception as e:
            logger.error(f"Cluster 동기화 중 오류 발생: {e}")
            return {"clusters_created": 0, "relationships_created": 0}

