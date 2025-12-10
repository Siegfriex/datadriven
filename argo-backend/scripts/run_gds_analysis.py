"""
GDS 분석 실행 스크립트
"""
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_gds_analysis():
    """GDS 분석 쿼리 실행"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    query_file = os.path.join(base_dir, "neo4j", "queries", "03_gds_execution.cypher")
    
    logger.info(f"GDS 분석 쿼리 파일 실행: {query_file}")
    
    if not os.path.exists(query_file):
        logger.error(f"파일을 찾을 수 없습니다: {query_file}")
        return False
        
    with open(query_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 쿼리 파싱 (세미콜론 기준)
    lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('//'):
            lines.append(line)
    
    queries = []
    current_query = []
    
    for line in lines:
        current_query.append(line)
        if line.rstrip().endswith(';'):
            query_text = '\n'.join(current_query).strip()
            if query_text:
                queries.append(query_text)
            current_query = []
    
    if current_query:
        query_text = '\n'.join(current_query).strip()
        if query_text:
            queries.append(query_text)
    
    logger.info(f"파싱된 쿼리 수: {len(queries)}")
    
    success_count = 0
    for i, query in enumerate(queries, 1):
        try:
            logger.info(f"GDS 쿼리 {i}/{len(queries)} 실행 중...")
            result = neo4j_service.execute_query(query)
            logger.info(f"GDS 쿼리 {i} 성공")
            if result:
                logger.info(f"  결과: {result}")
            success_count += 1
        except Exception as e:
            logger.error(f"GDS 쿼리 {i} 실패: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    logger.info(f"GDS 분석 완료: {success_count}/{len(queries)} 성공")
    return success_count > 0

if __name__ == "__main__":
    run_gds_analysis()
