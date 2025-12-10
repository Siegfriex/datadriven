"""
KCI API 테스트 스크립트

사용법:
    python test_kci_api.py
"""

import os
import sys
import json
from dotenv import load_dotenv

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.collectors.kci_collector import KCICollector

# 환경변수 로드
load_dotenv()

def test_kci_api():
    """KCI API 기본 테스트"""
    print("=" * 60)
    print("KCI API 테스트 시작")
    print("=" * 60)
    
    settings = get_settings()
    
    if not settings.ARKO_SERVICE_KEY:
        print("❌ ARKO_SERVICE_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 ARKO_SERVICE_KEY를 설정하세요.")
        return
    
    # KCI 수집기 생성
    collector = KCICollector(service_key=settings.ARKO_SERVICE_KEY)
    
    # 1. 첫 페이지 테스트
    print("\n[1] 첫 페이지 조회 테스트...")
    try:
        first_page = collector.get_papers_page(page=1, per_page=10)
        print(f"✅ 성공: {first_page.get('currentCount', 0)}개 논문 조회")
        print(f"   전체 논문 수: {first_page.get('totalCount', 0)}개")
        
        if first_page.get('data'):
            print("\n   샘플 논문:")
            sample = first_page['data'][0]
            print(f"   - 논문명(국문): {sample.get('논문명(국문)', 'N/A')}")
            print(f"   - 저자: {sample.get('저자', 'N/A')}")
            print(f"   - 학술지명: {sample.get('학술지명(국문)', 'N/A')}")
            print(f"   - 발행년: {sample.get('발행년', 'N/A')}")
            print(f"   - 주제분야: {sample.get('주제분야', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. 데이터 정규화 테스트
    print("\n[2] 데이터 정규화 테스트...")
    try:
        if first_page.get('data'):
            raw_paper = first_page['data'][0]
            normalized = collector.normalize_paper_data(raw_paper)
            print("✅ 정규화 성공")
            print(f"   - 제목(한글): {normalized.get('title_ko', 'N/A')}")
            print(f"   - 저자 수: {len(normalized.get('authors', []))}")
            print(f"   - 첫 저자: {normalized.get('first_author', 'N/A')}")
            print(f"   - 발행년: {normalized.get('publication_year', 'N/A')}")
            print(f"   - 등재구분: {normalized.get('registration_type', 'N/A')}")
            print(f"   - 주제분야: {normalized.get('subject_area', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 미술 관련 필터링 테스트
    print("\n[3] 미술 관련 논문 필터링 테스트...")
    try:
        # 샘플 100개 수집
        papers = collector.collect_all(max_count=100, filter_art_related=True)
        print(f"✅ 필터링 완료: {len(papers)}개 미술 관련 논문")
        
        if papers:
            print("\n   샘플 미술 관련 논문:")
            for i, paper in enumerate(papers[:3], 1):
                normalized = collector.normalize_paper_data(paper)
                print(f"   {i}. {normalized.get('title_ko', 'N/A')}")
                print(f"      저자: {', '.join(normalized.get('authors', [])[:3])}")
                print(f"      주제분야: {normalized.get('subject_area', 'N/A')}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 저자별 그룹화 테스트
    print("\n[4] 저자별 그룹화 테스트...")
    try:
        if papers:
            normalized_papers = [collector.normalize_paper_data(p) for p in papers[:50]]
            author_groups = collector.group_by_author(normalized_papers)
            print(f"✅ 그룹화 완료: {len(author_groups)}명의 저자")
            
            # 논문이 많은 저자 상위 5명
            top_authors = sorted(
                author_groups.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )[:5]
            
            print("\n   논문 수가 많은 저자 (상위 5명):")
            for author, author_papers in top_authors:
                print(f"   - {author}: {len(author_papers)}개 논문")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. 작가-논문 매칭 테스트
    print("\n[5] 작가-논문 매칭 테스트...")
    try:
        # 테스트용 작가 이름 (ARKO 작가 목록에서 가져온 샘플)
        test_artist_names = ["강경구", "김환기", "이중섭", "박수근", "백남준"]
        
        if papers:
            normalized_papers = [collector.normalize_paper_data(p) for p in papers[:100]]
            matched = collector.match_artists_to_papers(test_artist_names, normalized_papers)
            
            print(f"✅ 매칭 완료")
            print("\n   매칭 결과:")
            for artist_name, matched_papers in matched.items():
                print(f"   - {artist_name}: {len(matched_papers)}개 논문 매칭")
                if matched_papers:
                    print(f"     예시: {matched_papers[0].get('title_ko', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_kci_api()







