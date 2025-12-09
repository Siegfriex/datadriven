"""
GDS 분석 실행 스크립트

GDS 중심성 분석 및 Louvain 커뮤니티 탐지 실행
실행: python scripts/run_gds_analysis.py
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.analysis_service import analysis_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("GDS 분석 실행 시작")
    logger.info("=" * 60)
    
    # 1. 중심성 분석 실행
    logger.info("\n1. 중심성 분석 실행 중...")
    centrality_result = await analysis_service.run_gds_centrality()
    if "error" in centrality_result:
        logger.error(f"❌ 중심성 분석 실패: {centrality_result['error']}")
        return
    else:
        logger.info(f"✅ 중심성 분석 완료:")
        logger.info(f"   - Degree: {centrality_result.get('degree_updated', 0)}개 노드 업데이트")
        logger.info(f"   - Betweenness: {centrality_result.get('betweenness_updated', 0)}개 노드 업데이트")
        logger.info(f"   - Eigenvector: {centrality_result.get('eigenvector_updated', 0)}개 노드 업데이트")
    
    # 2. Louvain 커뮤니티 탐지 실행
    logger.info("\n2. Louvain 커뮤니티 탐지 실행 중...")
    louvain_result = await analysis_service.run_louvain_community()
    if "error" in louvain_result:
        logger.error(f"❌ Louvain 실패: {louvain_result['error']}")
        return
    else:
        logger.info(f"✅ Louvain 완료:")
        logger.info(f"   - 커뮤니티 수: {louvain_result.get('communities_detected', 0)}개")
        logger.info(f"   - 노드 업데이트: {louvain_result.get('nodes_updated', 0)}개")
        logger.info(f"   - Cluster 노드 생성: {louvain_result.get('clusters_created', 0)}개")
        logger.info(f"   - BELONGS_TO 관계 생성: {louvain_result.get('relationships_created', 0)}개")
    
    # 3. 구조주의 분석 필드 계산
    logger.info("\n3. 구조주의 분석 필드 계산 중...")
    structuralist_result = await analysis_service.calculate_structuralist_fields()
    if "error" in structuralist_result:
        logger.error(f"❌ 구조주의 분석 실패: {structuralist_result['error']}")
        return
    else:
        logger.info(f"✅ 구조주의 분석 완료:")
        logger.info(f"   - Capital Composition: {structuralist_result.get('capital_composition_updated', 0)}개")
        logger.info(f"   - Dominant Capital: {structuralist_result.get('dominant_capital_updated', 0)}개")
        logger.info(f"   - Field Quadrant: {structuralist_result.get('field_quadrant_updated', 0)}개")
        logger.info(f"   - Network Score: {structuralist_result.get('network_score_updated', 0)}개")
    
    logger.info("=" * 60)
    logger.info("GDS 분석 완료!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

