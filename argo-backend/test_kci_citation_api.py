"""
KCI 인용 정보 API 테스트 스크립트

사용법:
    python test_kci_citation_api.py
"""

import os
import sys
import json
from dotenv import load_dotenv

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.collectors.kci_citation_collector import KCICitationCollector

# 환경변수 로드
load_dotenv()

def test_kci_citation_api():
    """KCI 인용 정보 API 기본 테스트"""
    print("=" * 60)
    print("KCI 인용 정보 API 테스트 시작")
    print("=" * 60)
    
    settings = get_settings()
    
    if not settings.ARKO_SERVICE_KEY:
        print("❌ ARKO_SERVICE_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 ARKO_SERVICE_KEY를 설정하세요.")
        return
    
    # KCI 인용 정보 수집기 생성
    collector = KCICitationCollector(service_key=settings.ARKO_SERVICE_KEY)
    
    # 1. 첫 페이지 테스트
    print("\n[1] 첫 페이지 조회 테스트...")
    try:
        first_page = collector.get_author_citations_page(page=1, per_page=10)
        print(f"✅ 성공: {len(first_page.get('items', []))}개 저자 조회")
        print(f"   전체 저자 수: {first_page.get('totalCount', 0)}명")
        print(f"   결과 코드: {first_page.get('resultCode', 'N/A')}")
        print(f"   결과 메시지: {first_page.get('resultMsg', 'N/A')}")
        
        if first_page.get('items'):
            print("\n   샘플 저자 인용지수:")
            sample = first_page['items'][0]
            print(f"   - 저자ID: {sample.get('CRET_ID', 'N/A')}")
            print(f"   - 저자명(한글): {sample.get('CRET_KOR_NM', 'N/A')}")
            print(f"   - 저자명(영문): {sample.get('CRET_ENG_NM', 'N/A')}")
            print(f"   - 전체년도 피인용수: {sample.get('TOT_SERE_CNT', 'N/A')}")
            print(f"   - 전체년도 논문수: {sample.get('TOT_ARTI_CNT', 'N/A')}")
            print(f"   - H지수: {sample.get('H_IDX', 'N/A')}")
            print(f"   - 평균 피인용 횟수: {sample.get('SERE_AVG', 'N/A')}")
            print(f"   - 연구분야명: {sample.get('SPCL_NM', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. 데이터 정규화 테스트
    print("\n[2] 데이터 정규화 테스트...")
    try:
        if first_page.get('items'):
            raw_author = first_page['items'][0]
            normalized = collector.normalize_author_citation_data(raw_author)
            print("✅ 정규화 성공")
            print(f"   - 저자명(한글): {normalized.get('author_name_ko', 'N/A')}")
            print(f"   - 전체 인용 수: {normalized.get('total_citations', 'N/A')}")
            print(f"   - 전체 논문 수: {normalized.get('total_papers', 'N/A')}")
            print(f"   - H지수: {normalized.get('h_index', 'N/A')}")
            print(f"   - 평균 인용 수: {normalized.get('average_citations', 'N/A')}")
            print(f"   - 자기 인용 수: {normalized.get('self_citations', 'N/A')}")
            print(f"   - 연구분야: {normalized.get('research_field_name', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 미술 관련 필터링 테스트
    print("\n[3] 미술 관련 저자 필터링 테스트...")
    try:
        # 샘플 100개 수집
        authors = collector.collect_author_citations(max_count=100, filter_art_related=True)
        print(f"✅ 필터링 완료: {len(authors)}명의 미술 관련 저자")
        
        if authors:
            print("\n   샘플 미술 관련 저자:")
            for i, author in enumerate(authors[:3], 1):
                normalized = collector.normalize_author_citation_data(author)
                print(f"   {i}. {normalized.get('author_name_ko', 'N/A')}")
                print(f"      인용 수: {normalized.get('total_citations', 0)}")
                print(f"      논문 수: {normalized.get('total_papers', 0)}")
                print(f"      H지수: {normalized.get('h_index', 0)}")
                print(f"      연구분야: {normalized.get('research_field_name', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 작가-인용지수 매칭 테스트
    print("\n[4] 작가-인용지수 매칭 테스트...")
    try:
        # 테스트용 작가 이름
        test_artist_names = ["강경구", "김환기", "이중섭", "박수근", "백남준"]
        
        if authors:
            normalized_authors = [collector.normalize_author_citation_data(a) for a in authors[:200]]
            matched = collector.match_artists_to_citations(test_artist_names, normalized_authors)
            
            print(f"✅ 매칭 완료")
            print("\n   매칭 결과:")
            for artist_name, citation_data in matched.items():
                print(f"   - {artist_name}:")
                print(f"     인용 수: {citation_data.get('total_citations', 0)}")
                print(f"     논문 수: {citation_data.get('total_papers', 0)}")
                print(f"     H지수: {citation_data.get('h_index', 0)}")
                print(f"     평균 인용 수: {citation_data.get('average_citations', 0.0):.2f}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_kci_citation_api()









