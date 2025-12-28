"""
Artwork와 Publication 데이터 상세 확인
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

print("=" * 60)
print("Artwork 및 Publication 데이터 상세 확인")
print("=" * 60)

# Artwork 상세 확인
print("\n=== Artwork 상세 ===")
query1 = """
MATCH (w:Artwork)
RETURN w.id as id, w.title as title, w.artist_name as artist, 
       w.install_year as year, w.building_name as building
LIMIT 10
"""
result1 = neo4j_service.execute_query(query1)
print(f"총 {len(result1)}개 발견")
for i, r in enumerate(result1[:5], 1):
    print(f"{i}. ID: {r.get('id')}")
    print(f"   Title: {r.get('title')}")
    print(f"   Artist: {r.get('artist')}")
    print(f"   Year: {r.get('year')}")
    print(f"   Building: {r.get('building')}")

# Publication 상세 확인
print("\n=== Publication 상세 ===")
query2 = """
MATCH (p:Publication)
RETURN p.id as id, p.title_ko as title_ko, p.title_en as title_en,
       p.first_author as author, p.publication_year as year
LIMIT 10
"""
result2 = neo4j_service.execute_query(query2)
print(f"총 {len(result2)}개 발견")
for i, r in enumerate(result2[:5], 1):
    print(f"{i}. ID: {r.get('id')}")
    print(f"   Title_KO: {r.get('title_ko')}")
    print(f"   Title_EN: {r.get('title_en')}")
    print(f"   Author: {r.get('author')}")
    print(f"   Year: {r.get('year')}")

# 중복 ID 확인
print("\n=== 중복 ID 확인 ===")
query3 = """
MATCH (w:Artwork)
WITH w.id as id, count(*) as cnt
WHERE cnt > 1
RETURN id, cnt
"""
result3 = neo4j_service.execute_query(query3)
if result3:
    print(f"중복된 Artwork ID: {len(result3)}개")
    for r in result3:
        print(f"  {r.get('id')}: {r.get('cnt')}개")
else:
    print("중복된 Artwork ID 없음")

query4 = """
MATCH (p:Publication)
WITH p.id as id, count(*) as cnt
WHERE cnt > 1
RETURN id, cnt
"""
result4 = neo4j_service.execute_query(query4)
if result4:
    print(f"중복된 Publication ID: {len(result4)}개")
    for r in result4:
        print(f"  {r.get('id')}: {r.get('cnt')}개")
else:
    print("중복된 Publication ID 없음")

print("\n" + "=" * 60)



