"""
쿼리 성능 테스트 스크립트

작가 목록 조회, 작가 상세 조회, 구조적 등가성 계산, Galaxy snapshot 조회 성능 측정
실행: python scripts/test_query_performance.py
주의: API 서버가 실행 중이어야 함
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
import logging
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
PERFORMANCE_THRESHOLD_MS = 500  # 성능 기준: 500ms


def measure_endpoint_time(method: str, path: str, data: Dict = None) -> tuple:
    """엔드포인트 응답 시간 측정"""
    url = f"{BASE_URL}{path}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            return False, 0.0
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            return True, elapsed_ms
        else:
            return False, elapsed_ms
            
    except Exception as e:
        logger.error(f"   오류: {e}")
        return False, 0.0


def test_artists_list_performance():
    """작가 목록 조회 성능 테스트"""
    logger.info("\n=== 작가 목록 조회 성능 테스트 ===")
    
    times = []
    for i in range(5):
        success, elapsed = measure_endpoint_time("GET", "/v1/api/artists?limit=50")
        if success:
            times.append(elapsed)
            logger.info(f"   시도 {i+1}: {elapsed:.2f}ms")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        logger.info(f"   평균: {avg_time:.2f}ms, 최소: {min_time:.2f}ms, 최대: {max_time:.2f}ms")
        
        if avg_time < PERFORMANCE_THRESHOLD_MS:
            logger.info(f"   ✅ 성능 기준 충족 ({PERFORMANCE_THRESHOLD_MS}ms 이하)")
            return True
        else:
            logger.warning(f"   ⚠️  성능 기준 미충족 ({PERFORMANCE_THRESHOLD_MS}ms 초과)")
            return False
    
    return False


def test_artist_detail_performance():
    """작가 상세 조회 성능 테스트"""
    logger.info("\n=== 작가 상세 조회 성능 테스트 ===")
    
    # 작가 ID 가져오기
    _, artists_data = requests.get(f"{BASE_URL}/v1/api/artists?limit=1").json()
    items = artists_data.get("items", []) or artists_data.get("@graph", [])
    
    if not items:
        logger.warning("   ⚠️  작가 ID를 찾을 수 없어 테스트 건너뜀")
        return True
    
    artist_id = items[0].get("id") or items[0].get("@id", "").split("/")[-1]
    
    times = []
    for i in range(5):
        success, elapsed = measure_endpoint_time("GET", f"/v1/api/artists/{artist_id}")
        if success:
            times.append(elapsed)
            logger.info(f"   시도 {i+1}: {elapsed:.2f}ms")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        logger.info(f"   평균: {avg_time:.2f}ms, 최소: {min_time:.2f}ms, 최대: {max_time:.2f}ms")
        
        if avg_time < PERFORMANCE_THRESHOLD_MS:
            logger.info(f"   ✅ 성능 기준 충족 ({PERFORMANCE_THRESHOLD_MS}ms 이하)")
            return True
        else:
            logger.warning(f"   ⚠️  성능 기준 미충족 ({PERFORMANCE_THRESHOLD_MS}ms 초과)")
            return False
    
    return False


def test_structural_equivalents_performance():
    """구조적 등가성 계산 성능 테스트"""
    logger.info("\n=== 구조적 등가성 계산 성능 테스트 ===")
    
    # 작가 ID 가져오기
    _, artists_data = requests.get(f"{BASE_URL}/v1/api/artists?limit=1").json()
    items = artists_data.get("items", []) or artists_data.get("@graph", [])
    
    if not items:
        logger.warning("   ⚠️  작가 ID를 찾을 수 없어 테스트 건너뜀")
        return True
    
    artist_id = items[0].get("id") or items[0].get("@id", "").split("/")[-1]
    
    times = []
    for i in range(3):  # 계산이 무거울 수 있으므로 3회만
        success, elapsed = measure_endpoint_time("GET", f"/v1/api/artists/{artist_id}/structural-equivalents")
        if success:
            times.append(elapsed)
            logger.info(f"   시도 {i+1}: {elapsed:.2f}ms")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        logger.info(f"   평균: {avg_time:.2f}ms, 최소: {min_time:.2f}ms, 최대: {max_time:.2f}ms")
        
        # 구조적 등가성은 계산이 무거울 수 있으므로 기준을 2초로 완화
        if avg_time < 2000:
            logger.info(f"   ✅ 성능 기준 충족 (2초 이하)")
            return True
        else:
            logger.warning(f"   ⚠️  성능 기준 미충족 (2초 초과)")
            return False
    
    return False


def test_galaxy_snapshot_performance():
    """Galaxy snapshot 조회 성능 테스트"""
    logger.info("\n=== Galaxy Snapshot 조회 성능 테스트 ===")
    
    times = []
    for i in range(5):
        success, elapsed = measure_endpoint_time("GET", "/v1/api/galaxy-snapshot")
        if success:
            times.append(elapsed)
            logger.info(f"   시도 {i+1}: {elapsed:.2f}ms")
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        logger.info(f"   평균: {avg_time:.2f}ms, 최소: {min_time:.2f}ms, 최대: {max_time:.2f}ms")
        
        # Galaxy snapshot은 데이터가 많을 수 있으므로 기준을 1초로 완화
        if avg_time < 1000:
            logger.info(f"   ✅ 성능 기준 충족 (1초 이하)")
            return True
        else:
            logger.warning(f"   ⚠️  성능 기준 미충족 (1초 초과)")
            return False
    
    return False


def test_concurrency():
    """동시성 테스트 (동시 10개 요청)"""
    logger.info("\n=== 동시성 테스트 (동시 10개 요청) ===")
    
    def make_request(i: int) -> tuple[int, bool]:
        success, elapsed = measure_endpoint_time("GET", "/v1/api/artists?limit=10")
        return i, success
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        results = []
        
        for future in as_completed(futures):
            try:
                req_id, success = future.result()
                results.append((req_id, success))
            except Exception as e:
                logger.error(f"   요청 실패: {e}")
                results.append((0, False))
    
    total_time = (time.time() - start_time) * 1000
    
    success_count = sum(1 for _, success in results if success)
    logger.info(f"   성공: {success_count}/10, 총 소요 시간: {total_time:.2f}ms")
    
    if success_count == 10:
        logger.info("   ✅ 모든 동시 요청 성공")
        return True
    else:
        logger.warning(f"   ⚠️  일부 요청 실패 ({success_count}/10)")
        return False


def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("쿼리 성능 테스트 시작")
    logger.info("=" * 60)
    logger.info(f"테스트 대상 서버: {BASE_URL}")
    logger.info(f"성능 기준: {PERFORMANCE_THRESHOLD_MS}ms")
    
    results = []
    
    results.append(("작가 목록 조회", test_artists_list_performance()))
    results.append(("작가 상세 조회", test_artist_detail_performance()))
    results.append(("구조적 등가성 계산", test_structural_equivalents_performance()))
    results.append(("Galaxy Snapshot 조회", test_galaxy_snapshot_performance()))
    results.append(("동시성 테스트", test_concurrency()))
    
    logger.info("\n" + "=" * 60)
    logger.info("성능 테스트 결과 요약")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        logger.info(f"{name}: {status}")
    
    logger.info(f"\n전체: {passed}/{total} 통과")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("🎉 모든 성능 테스트 통과!")
        return 0
    else:
        logger.warning("⚠️  일부 성능 테스트 실패")
        return 1


if __name__ == "__main__":
    exit(main())

