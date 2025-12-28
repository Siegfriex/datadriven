"""
MMCA 소장작품 API 테스트 스크립트

사용법:
    python test_mmca_collection_api.py
"""

import os
import sys
import json
from dotenv import load_dotenv

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.collectors.mmca_collection_collector import MMCACollectionCollector

# 환경변수 로드
load_dotenv()

def test_mmca_collection_api():
    """MMCA 소장작품 API 기본 테스트"""
    print("=" * 60)
    print("MMCA 소장작품 API 테스트 시작")
    print("=" * 60)
    
    # MMCA 소장작품 API 키 (별도 키 사용)
    service_key = "c080ac2b-93ba-4300-af2d-8cc0ff71dda7"
    
    # MMCA 소장작품 수집기 생성
    collector = MMCACollectionCollector(service_key=service_key)
    
    # 1. 첫 페이지 테스트
    print("\n[1] 첫 페이지 조회 테스트...")
    try:
        first_page = collector.get_collection_page(page_no=1, num_of_rows=10)
        print(f"✅ 성공: {len(first_page.get('items', []))}개 작품 조회")
        print(f"   전체 작품 수: {first_page.get('totalCount', 0)}개")
        
        if first_page.get('items'):
            print("\n   샘플 소장작품:")
            sample = first_page['items'][0]
            print(f"   - 제목: {sample.get('title', 'N/A')[:50]}...")
            print(f"   - 작가: {sample.get('creator', 'N/A')}")
            print(f"   - 제작연도: {sample.get('temporalCoverage', 'N/A')}")
            print(f"   - 주제분류: {sample.get('subjectCategory', 'N/A')}")
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
            normalized = collector.normalize_collection_data(raw_work)
            print("✅ 정규화 성공")
            print(f"   - 제목: {normalized.get('title', 'N/A')[:50]}...")
            print(f"   - 작가 수: {len(normalized.get('creators', []))}")
            print(f"   - 첫 작가: {normalized.get('first_creator', 'N/A')}")
            print(f"   - 제작연도: {normalized.get('creation_year', 'N/A')}")
            print(f"   - 주제분류: {normalized.get('subject_category', 'N/A')}")
            print(f"   - 썸네일: {normalized.get('reference_identifier', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 작가별 그룹화 테스트
    print("\n[3] 작가별 그룹화 테스트...")
    try:
        # 샘플 50개 수집
        works = collector.collect_all(max_count=50)
        print(f"✅ 수집 완료: {len(works)}개 작품")
        
        if works:
            normalized_works = [collector.normalize_collection_data(w) for w in works]
            creator_groups = collector.group_by_creator(normalized_works)
            print(f"✅ 그룹화 완료: {len(creator_groups)}명의 작가")
            
            # 작품이 많은 작가 상위 5명
            top_creators = sorted(
                creator_groups.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )[:5]
            
            print("\n   소장작품 수가 많은 작가 (상위 5명):")
            for creator, creator_works in top_creators:
                print(f"   - {creator}: {len(creator_works)}개 작품")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 작가-소장작품 매칭 테스트
    print("\n[4] 작가-소장작품 매칭 테스트...")
    try:
        # 테스트용 작가 이름
        test_artist_names = ["홍길동", "김철수", "이영희", "박수근", "이중섭"]
        
        if works:
            normalized_works = [collector.normalize_collection_data(w) for w in works]
            matched = collector.match_artists_to_collection(test_artist_names, normalized_works)
            
            print(f"✅ 매칭 완료")
            print("\n   매칭 결과:")
            for artist_name, collection_info in matched.items():
                print(f"   - {artist_name}:")
                print(f"     소장작품 수: {collection_info.get('collection_count', 0)}")
                if collection_info.get('works'):
                    print(f"     예시 작품: {collection_info['works'][0].get('title', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_mmca_collection_api()








