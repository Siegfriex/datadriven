"""
MMCA 레지던시작가소식 API 테스트 스크립트

사용법:
    python test_mmca_residency_api.py
"""

import os
import sys
import json
from dotenv import load_dotenv

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.collectors.mmca_residency_collector import MMCAResidencyCollector

# 환경변수 로드
load_dotenv()

def test_mmca_residency_api():
    """MMCA 레지던시작가소식 API 기본 테스트"""
    print("=" * 60)
    print("MMCA 레지던시작가소식 API 테스트 시작")
    print("=" * 60)
    
    # MMCA 레지던시 API 키 (별도 키 사용)
    service_key = "0cc9c852-cd3b-417c-91b4-15722d964013"
    
    # MMCA 레지던시 수집기 생성
    collector = MMCAResidencyCollector(service_key=service_key)
    
    # 1. 첫 페이지 테스트
    print("\n[1] 첫 페이지 조회 테스트...")
    try:
        first_page = collector.get_residency_news_page(page_no=1, num_of_rows=10)
        print(f"✅ 성공: {len(first_page.get('items', []))}개 소식 조회")
        print(f"   전체 소식 수: {first_page.get('totalCount', 0)}개")
        
        if first_page.get('items'):
            print("\n   샘플 레지던시 소식:")
            sample = first_page['items'][0]
            print(f"   - 제목: {sample.get('TITLE', 'N/A')[:50]}...")
            print(f"   - 원천기관등록일: {sample.get('ISSUED_DATE', 'N/A')}")
            print(f"   - 설명: {sample.get('DESCRIPTION', 'N/A')[:50]}...")
            print(f"   - URL: {sample.get('URL', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. 데이터 정규화 테스트
    print("\n[2] 데이터 정규화 테스트...")
    try:
        if first_page.get('items'):
            raw_news = first_page['items'][0]
            normalized = collector.normalize_residency_data(raw_news)
            print("✅ 정규화 성공")
            print(f"   - 제목: {normalized.get('title', 'N/A')[:50]}...")
            print(f"   - 추출된 작가명: {normalized.get('artist_name', 'N/A')}")
            print(f"   - 원천기관등록일: {normalized.get('issued_date', 'N/A')}")
            print(f"   - URL: {normalized.get('url', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 작가 이름 추출 테스트
    print("\n[3] 작가 이름 추출 테스트...")
    try:
        test_titles = [
            "홍길동 작가 레지던시 소식",
            "김철수 레지던시 프로그램 참여",
            "이영희 아티스트 레지던시 소식"
        ]
        
        for title in test_titles:
            artist_name = collector.extract_artist_name(title, "")
            print(f"   - '{title}' → 작가명: {artist_name}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 작가별 그룹화 테스트
    print("\n[4] 작가별 그룹화 테스트...")
    try:
        # 샘플 50개 수집
        news_items = collector.collect_all(max_count=50)
        print(f"✅ 수집 완료: {len(news_items)}개 소식")
        
        if news_items:
            normalized_news = [collector.normalize_residency_data(n) for n in news_items]
            artist_groups = collector.group_by_artist(normalized_news)
            print(f"✅ 그룹화 완료: {len(artist_groups)}명의 작가")
            
            # 소식이 많은 작가 상위 5명
            top_artists = sorted(
                artist_groups.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )[:5]
            
            print("\n   소식 수가 많은 작가 (상위 5명):")
            for artist, artist_news in top_artists:
                print(f"   - {artist}: {len(artist_news)}개 소식")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. 작가-레지던시 매칭 테스트
    print("\n[5] 작가-레지던시 매칭 테스트...")
    try:
        # 테스트용 작가 이름
        test_artist_names = ["홍길동", "김철수", "이영희"]
        
        if news_items:
            normalized_news = [collector.normalize_residency_data(n) for n in news_items]
            matched = collector.match_artists_to_residency(test_artist_names, normalized_news)
            
            print(f"✅ 매칭 완료")
            print("\n   매칭 결과:")
            for artist_name, residency_info in matched.items():
                print(f"   - {artist_name}:")
                print(f"     레지던시 참여 횟수: {residency_info.get('residency_count', 0)}")
                if residency_info.get('news_items'):
                    print(f"     예시 소식: {residency_info['news_items'][0].get('title', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_mmca_residency_api()

