"""
Publication 데이터 구조 확인 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

print("=" * 60)
print("Publication 데이터 구조 확인")
print("=" * 60)

# Publication 샘플 확인
query = """
MATCH (p:Publication)
RETURN p.id as id, p.title_ko as title_ko, p.authors as authors, 
       p.publisher_ko as publisher, p.publication_year as year
LIMIT 5
"""

result = neo4j_service.execute_query(query)
print(f"\n발견된 Publication: {len(result)}개")
for i, r in enumerate(result, 1):
    print(f"\n{i}. ID: {r.get('id')}")
    print(f"   Title: {r.get('title_ko')}")
    print(f"   Authors: {r.get('authors')}")
    print(f"   Publisher: {r.get('publisher')}")
    print(f"   Year: {r.get('year')}")

# Artist 샘플 확인
query2 = """
MATCH (a:Artist)
RETURN a.id as id, a.name as name, a.alternateName as alt_name
LIMIT 5
"""

result2 = neo4j_service.execute_query(query2)
print(f"\n\n발견된 Artist: {len(result2)}개")
for i, r in enumerate(result2[:3], 1):
    print(f"{i}. {r.get('name')} (alt: {r.get('alt_name')})")

print("\n" + "=" * 60)



