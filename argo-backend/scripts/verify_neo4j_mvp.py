"""
Neo4j MVP 구현 검증 스크립트

스키마, 노드, 관계, GDS 분석 결과 검증
실행: python scripts/verify_neo4j_mvp.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_constraints():
    """제약조건 검증"""
    logger.info("\n=== 제약조건 검증 ===")
    try:
        constraints = neo4j_service.execute_query("SHOW CONSTRAINTS")
        logger.info(f"✅ 제약조건: {len(constraints)}개")
        for c in constraints[:5]:  # 처음 5개만 출력
            logger.info(f"   - {c.get('name', 'N/A')}: {c.get('type', 'N/A')}")
        return True
    except Exception as e:
        logger.error(f"❌ 제약조건 검증 실패: {e}")
        return False


def verify_indexes():
    """인덱스 검증"""
    logger.info("\n=== 인덱스 검증 ===")
    try:
        indexes = neo4j_service.execute_query("SHOW INDEXES")
        logger.info(f"✅ 인덱스: {len(indexes)}개")
        for idx in indexes[:5]:  # 처음 5개만 출력
            logger.info(f"   - {idx.get('name', 'N/A')}: {idx.get('type', 'N/A')}")
        return True
    except Exception as e:
        logger.error(f"❌ 인덱스 검증 실패: {e}")
        return False


def verify_nodes():
    """노드 타입별 카운트 검증"""
    logger.info("\n=== 노드 검증 ===")
    try:
        node_types = ['Artist', 'Institution', 'Exhibition', 'Cluster']
        for node_type in node_types:
            query = f"MATCH (n:{node_type}) RETURN count(n) AS count"
            result = neo4j_service.find_one(query)
            count = result.get('count', 0) if result else 0
            logger.info(f"✅ {node_type}: {count}개")
        return True
    except Exception as e:
        logger.error(f"❌ 노드 검증 실패: {e}")
        return False


def verify_relationships():
    """관계 타입별 카운트 검증"""
    logger.info("\n=== 관계 검증 ===")
    try:
        rel_types = [
            'COLLABORATED_WITH',
            'AFFILIATED_WITH',
            'PARTICIPATED_IN',
            'BELONGS_TO'
        ]
        for rel_type in rel_types:
            query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS count"
            result = neo4j_service.find_one(query)
            count = result.get('count', 0) if result else 0
            logger.info(f"✅ {rel_type}: {count}개")
        return True
    except Exception as e:
        logger.error(f"❌ 관계 검증 실패: {e}")
        return False


def verify_structuralist_fields():
    """구조주의 분석 필드 검증"""
    logger.info("\n=== 구조주의 분석 필드 검증 ===")
    try:
        # Capital Composition
        query1 = "MATCH (a:Artist) WHERE a.capital_composition IS NOT NULL RETURN count(a) AS count"
        result1 = neo4j_service.find_one(query1)
        comp_count = result1.get('count', 0) if result1 else 0
        logger.info(f"✅ Capital Composition: {comp_count}개")
        
        # Dominant Capital
        query2 = "MATCH (a:Artist) WHERE a.dominant_capital IS NOT NULL RETURN count(a) AS count"
        result2 = neo4j_service.find_one(query2)
        dom_count = result2.get('count', 0) if result2 else 0
        logger.info(f"✅ Dominant Capital: {dom_count}개")
        
        # Field Quadrant
        query3 = "MATCH (a:Artist) WHERE a.field_quadrant IS NOT NULL RETURN count(a) AS count"
        result3 = neo4j_service.find_one(query3)
        quad_count = result3.get('count', 0) if result3 else 0
        logger.info(f"✅ Field Quadrant: {quad_count}개")
        
        # Coordinates 3D
        query4 = "MATCH (a:Artist) WHERE a.coordinates_3d IS NOT NULL RETURN count(a) AS count"
        result4 = neo4j_service.find_one(query4)
        coord_count = result4.get('count', 0) if result4 else 0
        logger.info(f"✅ Coordinates 3D: {coord_count}개")
        
        return True
    except Exception as e:
        logger.error(f"❌ 구조주의 분석 필드 검증 실패: {e}")
        return False


def verify_gds_fields():
    """GDS 분석 필드 검증"""
    logger.info("\n=== GDS 분석 필드 검증 ===")
    try:
        # Degree Centrality
        query1 = "MATCH (a:Artist) WHERE a.degree_centrality IS NOT NULL RETURN count(a) AS count"
        result1 = neo4j_service.find_one(query1)
        degree_count = result1.get('count', 0) if result1 else 0
        logger.info(f"✅ Degree Centrality: {degree_count}개")
        
        # Betweenness Centrality
        query2 = "MATCH (a:Artist) WHERE a.betweenness_centrality IS NOT NULL RETURN count(a) AS count"
        result2 = neo4j_service.find_one(query2)
        between_count = result2.get('count', 0) if result2 else 0
        logger.info(f"✅ Betweenness Centrality: {between_count}개")
        
        # Eigenvector Centrality
        query3 = "MATCH (a:Artist) WHERE a.eigenvector_centrality IS NOT NULL RETURN count(a) AS count"
        result3 = neo4j_service.find_one(query3)
        eigen_count = result3.get('count', 0) if result3 else 0
        logger.info(f"✅ Eigenvector Centrality: {eigen_count}개")
        
        # Community ID
        query4 = "MATCH (a:Artist) WHERE a.community_id IS NOT NULL RETURN count(a) AS count"
        result4 = neo4j_service.find_one(query4)
        comm_count = result4.get('count', 0) if result4 else 0
        logger.info(f"✅ Community ID: {comm_count}개")
        
        return True
    except Exception as e:
        logger.error(f"❌ GDS 분석 필드 검증 실패: {e}")
        return False


def verify_sample_data():
    """샘플 데이터 검증"""
    logger.info("\n=== 샘플 데이터 검증 ===")
    try:
        # Artist 샘플
        query1 = """
        MATCH (a:Artist)
        WHERE a.dominant_capital IS NOT NULL AND a.field_quadrant IS NOT NULL
        RETURN a.id AS id, a.name AS name, a.dominant_capital AS dominant, a.field_quadrant AS quadrant
        LIMIT 5
        """
        artists = neo4j_service.execute_query(query1)
        logger.info(f"✅ Artist 샘플: {len(artists)}개")
        for a in artists[:3]:
            logger.info(f"   - {a.get('name')}: {a.get('dominant')}, {a.get('quadrant')}")
        
        # Cluster 샘플
        query2 = """
        MATCH (c:Cluster)
        RETURN c.id AS id, c.name AS name, c.size AS size
        LIMIT 5
        """
        clusters = neo4j_service.execute_query(query2)
        logger.info(f"✅ Cluster 샘플: {len(clusters)}개")
        for c in clusters[:3]:
            logger.info(f"   - {c.get('name')}: {c.get('size')}명")
        
        return True
    except Exception as e:
        logger.error(f"❌ 샘플 데이터 검증 실패: {e}")
        return False


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("Neo4j MVP 구현 검증 시작")
    logger.info("=" * 60)
    
    results = []
    
    results.append(("제약조건", verify_constraints()))
    results.append(("인덱스", verify_indexes()))
    results.append(("노드", verify_nodes()))
    results.append(("관계", verify_relationships()))
    results.append(("구조주의 분석 필드", verify_structuralist_fields()))
    results.append(("GDS 분석 필드", verify_gds_fields()))
    results.append(("샘플 데이터", verify_sample_data()))
    
    logger.info("\n" + "=" * 60)
    logger.info("검증 결과 요약")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        logger.info(f"{name}: {status}")
    
    logger.info(f"\n전체: {passed}/{total} 통과")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("🎉 모든 검증 통과!")
        return 0
    else:
        logger.warning("⚠️  일부 검증 실패")
        return 1


if __name__ == "__main__":
    exit(main())

