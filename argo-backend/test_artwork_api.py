"""
ARKO 미술작품 정보 API 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.collectors.artwork_collector import ArtworkCollector
import json

def test_artwork_api():
    """ARKO 미술작품 API 연결 테스트"""
    settings = get_settings()
    
    print("=" * 60)
    print("ARKO 미술작품 정보 API 테스트")
    print("=" * 60)
    
    # API 키 확인
    if not settings.ARKO_SERVICE_KEY:
        print("❌ ARKO API 키가 설정되지 않았습니다.")
        print("   .env 파일에 ARKO_SERVICE_KEY를 설정하세요.")
        return False
    
    print(f"✅ API 키 확인: serviceKey={settings.ARKO_SERVICE_KEY[:8]}...")
    
    # Collector 생성
    collector = ArtworkCollector(service_key=settings.ARKO_SERVICE_KEY)
    
    # 첫 페이지 테스트
    print("\n" + "-" * 60)
    print("첫 페이지 조회 테스트")
    print("-" * 60)
    
    try:
        first_page = collector.get_artworks_page(page=1, per_page=10)
        
        print(f"✅ API 호출 성공")
        print(f"   전체 작품 수: {first_page.get('totalCount', 0)}개")
        print(f"   현재 페이지: {first_page.get('currentCount', 0)}개")
        print(f"   페이지 정보: {first_page.get('page', 1)}/{first_page.get('perPage', 10)}")
        
        # 샘플 데이터 출력
        if first_page.get('data'):
            sample = first_page['data'][0]
            print(f"\n   샘플 데이터:")
            print(f"   - 작품명: {sample.get('작품명', 'N/A')}")
            print(f"   - 작가명: {sample.get('작가명', 'N/A')}")
            print(f"   - 분류: {sample.get('분류', 'N/A')}")
            print(f"   - 설치일자: {sample.get('설치일자', 'N/A')}")
            print(f"   - 지역: {sample.get('지역', 'N/A')}")
            print(f"   - 건축물명: {sample.get('건축물명', 'N/A')}")
            print(f"   - 건축물용도: {sample.get('건축물용도', 'N/A')}")
            
            # 정규화 테스트
            normalized = collector.normalize_artwork_data(sample)
            print(f"\n   정규화 결과:")
            print(f"   {json.dumps(normalized, ensure_ascii=False, indent=2)}")
        
        # 작가별 그룹화 테스트
        if first_page.get('data'):
            normalized_artworks = [collector.normalize_artwork_data(a) for a in first_page['data']]
            artist_groups = collector.group_by_artist(normalized_artworks)
            
            print(f"\n   작가별 그룹화:")
            for artist_name, artworks in list(artist_groups.items())[:5]:
                print(f"   - {artist_name}: {len(artworks)}개 작품")
        
        return True
        
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_artwork_api()
    sys.exit(0 if success else 1)

