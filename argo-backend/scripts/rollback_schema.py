"""
스키마 롤백 스크립트

제약조건 및 인덱스 삭제 (배포 실패 시 롤백용)
실행: python scripts/rollback_schema.py
주의: 이 스크립트는 모든 제약조건과 인덱스를 삭제합니다. 신중하게 사용하세요.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def drop_constraints():
    """제약조건 삭제"""
    logger.info("\n=== 제약조건 삭제 ===")
    
    constraints_to_drop = [
        "artist_id_unique",
        "institution_id_unique",
        "exhibition_id_unique",
        "cluster_id_unique",
        "artwork_id_unique",
        "transaction_id_unique"
    ]
    
    dropped_count = 0
    
    for constraint_name in constraints_to_drop:
        try:
            # 제약조건 존재 확인
            check_query = f"SHOW CONSTRAINTS WHERE name = '{constraint_name}'"
            exists = neo4j_service.execute_query(check_query)
            
            if exists:
                # 제약조건 삭제
                drop_query = f"DROP CONSTRAINT {constraint_name} IF EXISTS"
                neo4j_service.execute_query(drop_query)
                logger.info(f"   ✅ 제약조건 삭제: {constraint_name}")
                dropped_count += 1
            else:
                logger.info(f"   ⚠️  제약조건 없음: {constraint_name}")
        except Exception as e:
            logger.error(f"   ❌ 제약조건 삭제 실패 ({constraint_name}): {e}")
    
    logger.info(f"총 {dropped_count}개 제약조건 삭제 완료")
    return dropped_count


def drop_indexes():
    """인덱스 삭제"""
    logger.info("\n=== 인덱스 삭제 ===")
    
    indexes_to_drop = [
        "artist_composite_score",
        "artist_segment",
        "artist_field_quadrant",
        "artist_community",
        "institution_type",
        "institution_prestige",
        "exhibition_year",
        "exhibition_type"
    ]
    
    dropped_count = 0
    
    for index_name in indexes_to_drop:
        try:
            # 인덱스 존재 확인
            check_query = f"SHOW INDEXES WHERE name = '{index_name}'"
            exists = neo4j_service.execute_query(check_query)
            
            if exists:
                # 인덱스 삭제
                drop_query = f"DROP INDEX {index_name} IF EXISTS"
                neo4j_service.execute_query(drop_query)
                logger.info(f"   ✅ 인덱스 삭제: {index_name}")
                dropped_count += 1
            else:
                logger.info(f"   ⚠️  인덱스 없음: {index_name}")
        except Exception as e:
            logger.error(f"   ❌ 인덱스 삭제 실패 ({index_name}): {e}")
    
    logger.info(f"총 {dropped_count}개 인덱스 삭제 완료")
    return dropped_count


def drop_fulltext_indexes():
    """Fulltext 인덱스 삭제"""
    logger.info("\n=== Fulltext 인덱스 삭제 ===")
    
    fulltext_indexes_to_drop = [
        "artist_name_fulltext",
        "institution_name_fulltext",
        "exhibition_title_fulltext"
    ]
    
    dropped_count = 0
    
    for index_name in fulltext_indexes_to_drop:
        try:
            # Fulltext 인덱스 존재 확인
            check_query = f"SHOW INDEXES WHERE name = '{index_name}'"
            exists = neo4j_service.execute_query(check_query)
            
            if exists:
                # Fulltext 인덱스 삭제
                drop_query = f"DROP INDEX {index_name} IF EXISTS"
                neo4j_service.execute_query(drop_query)
                logger.info(f"   ✅ Fulltext 인덱스 삭제: {index_name}")
                dropped_count += 1
            else:
                logger.info(f"   ⚠️  Fulltext 인덱스 없음: {index_name}")
        except Exception as e:
            logger.error(f"   ❌ Fulltext 인덱스 삭제 실패 ({index_name}): {e}")
    
    logger.info(f"총 {dropped_count}개 Fulltext 인덱스 삭제 완료")
    return dropped_count


def drop_gds_projections():
    """GDS 프로젝션 삭제"""
    logger.info("\n=== GDS 프로젝션 삭제 ===")
    
    try:
        # 모든 GDS 프로젝션 목록 조회
        list_query = "CALL gds.graph.list() YIELD graphName"
        projections = neo4j_service.execute_query(list_query)
        
        dropped_count = 0
        
        for proj in projections:
            graph_name = proj.get('graphName')
            try:
                drop_query = f"CALL gds.graph.drop('{graph_name}') YIELD graphName"
                neo4j_service.execute_query(drop_query)
                logger.info(f"   ✅ GDS 프로젝션 삭제: {graph_name}")
                dropped_count += 1
            except Exception as e:
                logger.error(f"   ❌ GDS 프로젝션 삭제 실패 ({graph_name}): {e}")
        
        if dropped_count == 0:
            logger.info("   ⚠️  삭제할 GDS 프로젝션 없음")
        
        return dropped_count
        
    except Exception as e:
        logger.warning(f"⚠️  GDS 프로젝션 삭제 실패 (GDS 라이브러리 없을 수 있음): {e}")
        return 0


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("스키마 롤백 시작")
    logger.info("=" * 60)
    logger.warning("⚠️  주의: 이 스크립트는 모든 제약조건과 인덱스를 삭제합니다.")
    logger.warning("⚠️  신중하게 사용하세요. 데이터는 삭제되지 않습니다.")
    
    # 사용자 확인 (실제 배포 시에는 주석 처리하거나 자동화)
    # response = input("계속하시겠습니까? (yes/no): ")
    # if response.lower() != "yes":
    #     logger.info("롤백 취소됨")
    #     return 0
    
    results = []
    
    results.append(("제약조건", drop_constraints()))
    results.append(("인덱스", drop_indexes()))
    results.append(("Fulltext 인덱스", drop_fulltext_indexes()))
    results.append(("GDS 프로젝션", drop_gds_projections()))
    
    logger.info("\n" + "=" * 60)
    logger.info("롤백 결과 요약")
    logger.info("=" * 60)
    
    for name, count in results:
        logger.info(f"{name}: {count}개 삭제")
    
    logger.info("=" * 60)
    logger.info("✅ 스키마 롤백 완료")
    logger.info("=" * 60)
    logger.warning("⚠️  데이터는 삭제되지 않았습니다.")
    logger.warning("⚠️  데이터 롤백이 필요하면 Neo4j 백업에서 복원하세요.")
    
    return 0


if __name__ == "__main__":
    exit(main())


