"""
ARKO 예술단체 및 예술인 목록 API 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.collectors.institution_collector import InstitutionCollector
import json

def test_institution_api():
    """ARKO 예술단체 API 연결 테스트"""
    settings = get_settings()
    
    print("=" * 60)
    print("ARKO 예술단체 및 예술인 목록 API 테스트")
    print("=" * 60)
    
    # API 키 확인
    if not settings.ARKO_SERVICE_KEY:
        print("❌ ARKO API 키가 설정되지 않았습니다.")
        print("   .env 파일에 ARKO_SERVICE_KEY를 설정하세요.")
        return False
    
    print(f"✅ API 키 확인: serviceKey={settings.ARKO_SERVICE_KEY[:8]}...")
    
    # Collector 생성
    collector = InstitutionCollector(service_key=settings.ARKO_SERVICE_KEY)
    
    # 첫 페이지 테스트
    print("\n" + "-" * 60)
    print("첫 페이지 조회 테스트")
    print("-" * 60)
    
    try:
        first_page = collector.get_institutions_page(page=1, per_page=10)
        
        print(f"✅ API 호출 성공")
        print(f"   전체 단체 수: {first_page.get('totalCount', 0)}개")
        print(f"   현재 페이지: {first_page.get('currentCount', 0)}개")
        print(f"   페이지 정보: {first_page.get('page', 1)}/{first_page.get('perPage', 10)}")
        
        # 샘플 데이터 출력
        if first_page.get('data'):
            sample = first_page['data'][0]
            print(f"\n   샘플 데이터:")
            print(f"   - 단체명: {sample.get('단체명', 'N/A')}")
            print(f"   - 대표명: {sample.get('대표명', 'N/A')}")
            print(f"   - 관련페이지주소: {sample.get('관련페이지주소', 'N/A')}")
            
            # 정규화 테스트
            normalized = collector.normalize_institution_data(sample)
            print(f"\n   정규화 결과:")
            print(f"   {json.dumps(normalized, ensure_ascii=False, indent=2)}")
        
        # 대표자별 그룹화 테스트
        if first_page.get('data'):
            normalized_institutions = [collector.normalize_institution_data(i) for i in first_page['data']]
            rep_groups = collector.group_by_representative(normalized_institutions)
            
            print(f"\n   대표자별 그룹화:")
            for rep_name, institutions in list(rep_groups.items())[:5]:
                print(f"   - {rep_name}: {len(institutions)}개 단체")
        
        return True
        
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_institution_api()
    sys.exit(0 if success else 1)

