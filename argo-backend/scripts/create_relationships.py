"""
관계 생성 스크립트 (APOC 기반)

Cypher 쿼리 파일을 실행하여 관계를 생성합니다.
대상 파일: neo4j/queries/01_relationship_creation.cypher
"""

import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_cypher_file(file_path):
    """Cypher 파일의 쿼리들을 실행"""
    logger.info(f"쿼리 파일 실행: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"파일을 찾을 수 없습니다: {file_path}")
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 주석 제거 및 빈 줄 제거
    lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('//'):
            lines.append(line)
    
    # 세미콜론으로 쿼리 분리 (APOC 프로시저 호출 고려)
    queries = []
    current_query = []
    
    for line in lines:
        current_query.append(line)
        # 세미콜론으로 끝나는 경우 쿼리 완성
        if line.rstrip().endswith(';'):
            query_text = '\n'.join(current_query).strip()
            if query_text:
                queries.append(query_text)
            current_query = []
    
    # 마지막 쿼리 처리
    if current_query:
        query_text = '\n'.join(current_query).strip()
        if query_text:
            queries.append(query_text)
    
    logger.info(f"파싱된 쿼리 수: {len(queries)}")
    
    success_count = 0
    for i, query in enumerate(queries, 1):
        try:
            logger.info(f"쿼리 {i}/{len(queries)} 실행 중...")
            logger.debug(f"쿼리 내용 (처음 100자): {query[:100]}...")
            result = neo4j_service.execute_query(query)
            logger.info(f"쿼리 {i} 성공 (결과: {len(result) if result else 0}개)")
            success_count += 1
        except Exception as e:
            logger.error(f"쿼리 {i} 실패: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
    logger.info(f"실행 완료: {success_count}/{len(queries)} 성공")
    return success_count > 0

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query_file = os.path.join(base_dir, "neo4j", "queries", "01_relationship_creation.cypher")
    
    if run_cypher_file(query_file):
        logger.info("모든 관계 생성 작업 완료")
    else:
        logger.error("관계 생성 작업 중 오류 발생")

if __name__ == "__main__":
    main()
