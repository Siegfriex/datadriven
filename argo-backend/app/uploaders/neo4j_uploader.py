"""
Neo4j 데이터 업로드 모듈

수집 및 정규화된 데이터를 Neo4j에 업로드
"""

from typing import List, Dict, Any
import logging
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
        단일 작가 데이터 업로드
        
        Args:
            artist_data: 정규화된 작가 데이터
            
        Returns:
            업로드 성공 여부
        """
        try:
            # 작가 ID 생성 또는 사용
            artist_id = artist_data.get("artist_id") or artist_data.get("id")
            if not artist_id:
                # 이름 기반 ID 생성
                artist_id = Neo4jUploader.generate_artist_id(
                    artist_data.get("name", "unknown"),
                    hash(artist_data.get("name", "")) % 10000
                )
            
            # 점수 데이터 준비
            scores = Scores(
                inst_score=artist_data.get("inst_score", 0.0),
                acad_score=artist_data.get("acad_score", 0.0),
                media_score=artist_data.get("media_score", 0.0),
                network_score=artist_data.get("network_score", 0.0),
                composite_score=artist_data.get("composite_score", 0.0),
                composite_confidence=artist_data.get("composite_confidence")
            )
            
            # 좌표 계산
            coords = calculate_coordinates(scores)
            
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
                a.updated_at = datetime()
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
                    "collected_at": artist_data.get("collected_at"),
                    "verified": artist_data.get("is_verified", False)
                }
            }
            
            result = neo4j_service.execute_query(query, params)
            
            if result:
                logger.info(f"작가 업로드 성공: {artist_id} ({artist_data.get('name')})")
                return True
            else:
                logger.warning(f"작가 업로드 실패: {artist_id}")
                return False
                
        except Exception as e:
            logger.error(f"작가 업로드 중 오류 발생 ({artist_data.get('name')}): {e}")
            return False
    
    @staticmethod
    def upload_artists(artists: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        배치 작가 데이터 업로드
        
        Args:
            artists: 정규화된 작가 데이터 리스트
            
        Returns:
            {"success": int, "failed": int}
        """
        success_count = 0
        failed_count = 0
        
        for artist in artists:
            if Neo4jUploader.upload_artist(artist):
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(f"배치 업로드 완료: 성공 {success_count}명, 실패 {failed_count}명")
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(artists)
        }

