"""
Neo4j 스키마 초기화 스크립트

제약조건 및 인덱스 생성
실행: python scripts/init_neo4j_schema.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_cypher_file(file_path: str) -> str:
    """Cypher 파일 읽기"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def execute_cypher_statements(cypher_content: str):
    """Cypher 문장들을 개별 실행"""
    # 주석 제거 및 문장 분리
    statements = []
    current_statement = []
    
    for line in cypher_content.split('\n'):
        stripped = line.strip()
        # 주석 건너뛰기
        if stripped.startswith('//') or not stripped:
            continue
        
        current_statement.append(line)
        
        # 세미콜론으로 문장 종료
        if stripped.endswith(';'):
            statement = '\n'.join(current_statement)
            if statement.strip():
                statements.append(statement.strip())
            current_statement = []
    
    # 마지막 문장 처리
    if current_statement:
        statement = '\n'.join(current_statement)
        if statement.strip():
            statements.append(statement.strip())
    
    # 각 문장 실행
    for i, stmt in enumerate(statements, 1):
        try:
            logger.info(f"실행 중 ({i}/{len(statements)}): {stmt[:50]}...")
            result = neo4j_service.execute_query(stmt)
            logger.info(f"✅ 성공: {len(result)} 결과")
        except Exception as e:
            logger.warning(f"⚠️  실행 실패 (계속 진행): {e}")
            logger.debug(f"실패한 쿼리: {stmt}")


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("Neo4j 스키마 초기화 시작")
    logger.info("=" * 60)
    
    # init_schema.cypher 실행
    schema_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'neo4j',
        'init_schema.cypher'
    )
    
    if not os.path.exists(schema_file):
        logger.error(f"스키마 파일을 찾을 수 없습니다: {schema_file}")
        return
    
    logger.info(f"스키마 파일 읽기: {schema_file}")
    cypher_content = read_cypher_file(schema_file)
    
    logger.info("제약조건 및 인덱스 생성 중...")
    execute_cypher_statements(cypher_content)
    
    logger.info("=" * 60)
    logger.info("스키마 초기화 완료!")
    logger.info("=" * 60)
    
    # 검증 쿼리 실행
    logger.info("\n검증 중...")
    try:
        constraints = neo4j_service.execute_query("SHOW CONSTRAINTS")
        indexes = neo4j_service.execute_query("SHOW INDEXES")
        
        logger.info(f"✅ 제약조건: {len(constraints)}개")
        logger.info(f"✅ 인덱스: {len(indexes)}개")
        
        # Artist 노드 카운트
        artist_count = neo4j_service.find_one("MATCH (a:Artist) RETURN count(a) AS count")
        logger.info(f"✅ Artist 노드: {artist_count.get('count', 0) if artist_count else 0}개")
        
    except Exception as e:
        logger.warning(f"검증 쿼리 실행 실패: {e}")


if __name__ == "__main__":
    main()

