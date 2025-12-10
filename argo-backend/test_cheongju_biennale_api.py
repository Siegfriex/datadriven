"""
청주공예비엔날레 API 테스트 스크립트

사용법:
    python test_cheongju_biennale_api.py
"""

import os
import sys
import json
from dotenv import load_dotenv

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.collectors.cheongju_biennale_collector import CheongjuBiennaleCollector

# 환경변수 로드
load_dotenv()

def test_cheongju_biennale_api():
    """청주공예비엔날레 API 기본 테스트"""
    print("=" * 60)
    print("청주공예비엔날레 API 테스트 시작")
    print("=" * 60)
    
    settings = get_settings()
    
    if not settings.ARKO_SERVICE_KEY:
        print("❌ ARKO_SERVICE_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 ARKO_SERVICE_KEY를 설정하세요.")
        return
    
    # 청주공예비엔날레 수집기 생성
    collector = CheongjuBiennaleCollector(service_key=settings.ARKO_SERVICE_KEY)
    
    # 1. 작가별 작품 조회 테스트
    print("\n[1] 작가별 작품 조회 테스트...")
    try:
        first_page = collector.get_artist_works(page_no=1, num_of_rows=10)
        print(f"✅ 성공: {len(first_page.get('items', []))}개 작품 조회")
        print(f"   전체 작품 수: {first_page.get('totalCount', 0)}개")
        
        if first_page.get('items'):
            print("\n   샘플 작품:")
            sample = first_page['items'][0]
            print(f"   - 작가명(한글): {sample.get('artistNameKo', 'N/A')}")
            print(f"   - 작가명(영문): {sample.get('artistNameEn', 'N/A')}")
            print(f"   - 작품명(한글): {sample.get('workNameKo', 'N/A')}")
            print(f"   - 행사명: {sample.get('eventNameKo', 'N/A')}")
            print(f"   - 입상명: {sample.get('awardName', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. 데이터 정규화 테스트
    print("\n[2] 데이터 정규화 테스트...")
    try:
        if first_page.get('items'):
            raw_work = first_page['items'][0]
            normalized = collector.normalize_artist_work_data(raw_work)
            print("✅ 정규화 성공")
            print(f"   - 작가명(한글): {normalized.get('artist_name_ko', 'N/A')}")
            print(f"   - 작품명(한글): {normalized.get('work_name_ko', 'N/A')}")
            print(f"   - 행사명: {normalized.get('event_name_ko', 'N/A')}")
            print(f"   - 입상명: {normalized.get('award_name', 'N/A')}")
            print(f"   - 기법: {normalized.get('work_technique', 'N/A')}")
            print(f"   - 재질: {normalized.get('work_material', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 작가별 그룹화 테스트
    print("\n[3] 작가별 그룹화 테스트...")
    try:
        # 샘플 50개 수집
        works = collector.collect_all_artist_works(max_count=50)
        print(f"✅ 수집 완료: {len(works)}개 작품")
        
        if works:
            normalized_works = [collector.normalize_artist_work_data(w) for w in works]
            artist_groups = collector.group_by_artist(normalized_works)
            print(f"✅ 그룹화 완료: {len(artist_groups)}명의 작가")
            
            # 작품이 많은 작가 상위 5명
            top_artists = sorted(
                artist_groups.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )[:5]
            
            print("\n   작품 수가 많은 작가 (상위 5명):")
            for artist, artist_works in top_artists:
                print(f"   - {artist}: {len(artist_works)}개 작품")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 작가-비엔날레 매칭 테스트
    print("\n[4] 작가-비엔날레 매칭 테스트...")
    try:
        # 테스트용 작가 이름
        test_artist_names = ["강경구", "김환기", "이중섭", "박수근", "백남준"]
        
        if works:
            normalized_works = [collector.normalize_artist_work_data(w) for w in works]
            matched = collector.match_artists_to_biennale(test_artist_names, normalized_works)
            
            print(f"✅ 매칭 완료")
            print("\n   매칭 결과:")
            for artist_name, biennale_info in matched.items():
                print(f"   - {artist_name}:")
                print(f"     참여 횟수: {biennale_info.get('participation_count', 0)}")
                print(f"     입상 횟수: {biennale_info.get('award_count', 0)}")
                print(f"     참여 행사: {', '.join(biennale_info.get('events', [])[:3])}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_cheongju_biennale_api()







