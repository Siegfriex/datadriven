"""
Neo4j 데이터 상태 확인 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

print("=" * 60)
print("Neo4j 데이터 상태 확인")
print("=" * 60)

# 노드 타입별 카운트
print("\n=== 노드 타입별 카운트 ===")
query1 = """
MATCH (n)
RETURN labels(n) as labels, count(*) as count
ORDER BY count DESC
"""
result1 = neo4j_service.execute_query(query1)
for r in result1:
    label = r['labels'][0] if r['labels'] else 'Unknown'
    print(f"  {label}: {r['count']}개")

# Artist 노드 상세
print("\n=== Artist 노드 상세 ===")
query2 = "MATCH (a:Artist) RETURN count(a) as count"
result2 = neo4j_service.execute_query(query2)
artist_count = result2[0]['count'] if result2 else 0
print(f"  Artist: {artist_count}개")

# Artwork 노드 확인
print("\n=== Artwork 노드 확인 ===")
query3 = "MATCH (w:Artwork) RETURN count(w) as count"
result3 = neo4j_service.execute_query(query3)
artwork_count = result3[0]['count'] if result3 else 0
print(f"  Artwork: {artwork_count}개")

# Paper 노드 확인 (논문)
print("\n=== Paper 노드 확인 (논문) ===")
query4 = "MATCH (p:Paper) RETURN count(p) as count"
result4 = neo4j_service.execute_query(query4)
paper_count = result4[0]['count'] if result4 else 0
print(f"  Paper: {paper_count}개")

# Publication 노드 확인 (다른 이름일 수도)
print("\n=== Publication 노드 확인 ===")
query5 = "MATCH (p:Publication) RETURN count(p) as count"
result5 = neo4j_service.execute_query(query5)
publication_count = result5[0]['count'] if result5 else 0
print(f"  Publication: {publication_count}개")

# Institution 노드 확인
print("\n=== Institution 노드 확인 ===")
query6 = "MATCH (i:Institution) RETURN count(i) as count"
result6 = neo4j_service.execute_query(query6)
institution_count = result6[0]['count'] if result6 else 0
print(f"  Institution: {institution_count}개")

# Exhibition 노드 확인
print("\n=== Exhibition 노드 확인 ===")
query7 = "MATCH (e:Exhibition) RETURN count(e) as count"
result7 = neo4j_service.execute_query(query7)
exhibition_count = result7[0]['count'] if result7 else 0
print(f"  Exhibition: {exhibition_count}개")

# Artist 샘플 확인 (좌표 데이터 포함)
print("\n=== Artist 샘플 확인 (좌표 데이터) ===")
query8 = """
MATCH (a:Artist)
RETURN a.id as id, a.name as name, 
       a.coord_x as x, a.coord_y as y, a.coord_z as z,
       a.inst_score as inst, a.acad_score as acad,
       a.media_score as media, a.network_score as network
LIMIT 5
"""
result8 = neo4j_service.execute_query(query8)
if result8:
    for r in result8:
        print(f"  {r.get('name')}: x={r.get('x')}, y={r.get('y')}, z={r.get('z')}")
        print(f"    점수: inst={r.get('inst')}, acad={r.get('acad')}, media={r.get('media')}, network={r.get('network')}")
else:
    print("  샘플 없음")

# 모든 노드 타입 확인
print("\n=== 모든 노드 타입 확인 ===")
query9 = """
CALL db.labels() YIELD label
RETURN label
ORDER BY label
"""
result9 = neo4j_service.execute_query(query9)
print("  발견된 노드 타입:")
for r in result9:
    print(f"    - {r['label']}")

print("\n" + "=" * 60)
print("확인 완료")
print("=" * 60)

