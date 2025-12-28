"""
관계 생성 실패 원인 분석 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

print("=" * 60)
print("관계 생성 실패 원인 분석")
print("=" * 60)

# 1. Publication 데이터 확인
print("\n=== Publication 데이터 확인 ===")
query1 = """
MATCH (p:Publication)
RETURN count(p) as total,
       sum(CASE WHEN size(p.authors) > 1 THEN 1 ELSE 0 END) as with_multiple_authors,
       sum(CASE WHEN p.publisher_ko IS NOT NULL THEN 1 ELSE 0 END) as with_publisher
"""
result1 = neo4j_service.execute_query(query1)
if result1:
    r = result1[0]
    print(f"  총 Publication: {r.get('total')}개")
    print(f"  공동저자 있는 논문: {r.get('with_multiple_authors')}개")
    print(f"  발행기관 있는 논문: {r.get('with_publisher')}개")

# 2. Artist segment_id 확인
print("\n=== Artist segment_id 확인 ===")
query2 = """
MATCH (a:Artist)
RETURN count(a) as total,
       sum(CASE WHEN a.segment_id IS NOT NULL THEN 1 ELSE 0 END) as with_segment
"""
result2 = neo4j_service.execute_query(query2)
if result2:
    r = result2[0]
    print(f"  총 Artist: {r.get('total')}개")
    print(f"  segment_id 있는 작가: {r.get('with_segment')}개")

# 3. Institution 타입 확인
print("\n=== Institution 타입 확인 ===")
query3 = """
MATCH (i:Institution)
RETURN i.type as type, count(*) as count
ORDER BY count DESC
LIMIT 10
"""
result3 = neo4j_service.execute_query(query3)
print("  Institution 타입 분포:")
for r in result3:
    print(f"    {r.get('type')}: {r.get('count')}개")

# 4. Artwork building_name 확인
print("\n=== Artwork building_name 확인 ===")
query4 = """
MATCH (w:Artwork)
RETURN count(w) as total,
       sum(CASE WHEN w.building_name IS NOT NULL THEN 1 ELSE 0 END) as with_building
"""
result4 = neo4j_service.execute_query(query4)
if result4:
    r = result4[0]
    print(f"  총 Artwork: {r.get('total')}개")
    print(f"  building_name 있는 작품: {r.get('with_building')}개")

print("\n" + "=" * 60)



