"""
ARKO API 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.collectors.arko_collector import ARKOCollector
import json

def test_arko_api():
    """ARKO API 연결 테스트"""
    settings = get_settings()
    
    print("=" * 60)
    print("ARKO API 테스트")
    print("=" * 60)
    
    # API 키 확인
    if not settings.ARKO_API_KEY or not settings.ARKO_SERVICE_KEY:
        print("❌ ARKO API 키가 설정되지 않았습니다.")
        print("   .env 파일에 다음을 추가하세요:")
        print("   ARKO_API_KEY=1209")
        print("   ARKO_SERVICE_KEY=1209")
        return False
    
    print(f"✅ API 키 확인: Authorization={settings.ARKO_API_KEY[:4]}..., serviceKey={settings.ARKO_SERVICE_KEY[:4]}...")
    
    # Collector 생성
    collector = ARKOCollector(
        api_key=settings.ARKO_API_KEY,
        service_key=settings.ARKO_SERVICE_KEY
    )
    
    # 첫 페이지 테스트
    print("\n" + "-" * 60)
    print("첫 페이지 조회 테스트")
    print("-" * 60)
    
    try:
        first_page = collector.get_artists_page(page=1, per_page=10)
        
        print(f"✅ API 호출 성공")
        print(f"   전체 작가 수: {first_page.get('totalCount', 0)}명")
        print(f"   현재 페이지: {first_page.get('currentCount', 0)}명")
        print(f"   페이지 정보: {first_page.get('page', 1)}/{first_page.get('perPage', 10)}")
        
        # 샘플 데이터 출력
        if first_page.get('data'):
            sample = first_page['data'][0]
            print(f"\n   샘플 데이터:")
            print(f"   - 이름: {sample.get('이름', 'N/A')}")
            print(f"   - 이형표기: {sample.get('이형표기', 'N/A')}")
            print(f"   - 분야: {sample.get('분야', 'N/A')}")
            
            # 정규화 테스트
            normalized = collector.normalize_artist_data(sample)
            print(f"\n   정규화 결과:")
            print(f"   {json.dumps(normalized, ensure_ascii=False, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_arko_api()
    sys.exit(0 if success else 1)

