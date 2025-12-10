"""
현재 진행 상황 파악 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.neo4j_service import neo4j_service

print("=" * 60)
print("ARGO Neo4j 진행 상황 파악")
print("=" * 60)

# 1. 노드 카운트 확인
print("\n=== 노드 카운트 ===")
queries = {
    "Artist": "MATCH (a:Artist) RETURN count(a) as count",
    "Institution": "MATCH (i:Institution) RETURN count(i) as count",
    "Artwork": "MATCH (w:Artwork) RETURN count(w) as count",
    "Publication": "MATCH (p:Publication) RETURN count(p) as count",
    "Exhibition": "MATCH (e:Exhibition) RETURN count(e) as count",
    "Cluster": "MATCH (c:Cluster) RETURN count(c) as count"
}

for label, query in queries.items():
    try:
        result = neo4j_service.execute_query(query)
        count = result[0]['count'] if result else 0
        print(f"  {label}: {count}개")
    except Exception as e:
        print(f"  {label}: 오류 - {e}")

# 2. 관계 카운트 확인
print("\n=== 관계 카운트 ===")
rel_queries = {
    "COLLABORATED_WITH": "MATCH ()-[r:COLLABORATED_WITH]->() RETURN count(r) as count",
    "AFFILIATED_WITH": "MATCH ()-[r:AFFILIATED_WITH]->() RETURN count(r) as count",
    "PARTICIPATED_IN": "MATCH ()-[r:PARTICIPATED_IN]->() RETURN count(r) as count",
    "BELONGS_TO": "MATCH ()-[r:BELONGS_TO]->() RETURN count(r) as count"
}

for rel_type, query in rel_queries.items():
    try:
        result = neo4j_service.execute_query(query)
        count = result[0]['count'] if result else 0
        print(f"  {rel_type}: {count}개")
    except Exception as e:
        print(f"  {rel_type}: 오류 - {e}")

# 3. GDS 분석 결과 확인
print("\n=== GDS 분석 결과 확인 ===")
gds_checks = {
    "community_id": "MATCH (a:Artist) WHERE a.community_id IS NOT NULL RETURN count(a) as count",
    "degree_centrality": "MATCH (a:Artist) WHERE a.degree_centrality IS NOT NULL RETURN count(a) as count",
    "pagerank_score": "MATCH (a:Artist) WHERE a.pagerank_score IS NOT NULL RETURN count(a) as count"
}

for prop, query in gds_checks.items():
    try:
        result = neo4j_service.execute_query(query)
        count = result[0]['count'] if result else 0
        print(f"  {prop}: {count}개")
    except Exception as e:
        print(f"  {prop}: 오류 - {e}")

# 4. 구조주의 분석 필드 확인
print("\n=== 구조주의 분석 필드 확인 ===")
structural_checks = {
    "capital_composition": "MATCH (a:Artist) WHERE a.capital_inst_ratio IS NOT NULL RETURN count(a) as count",
    "field_quadrant": "MATCH (a:Artist) WHERE a.field_quadrant IS NOT NULL RETURN count(a) as count",
    "coordinates_3d": "MATCH (a:Artist) WHERE a.coord_x IS NOT NULL AND a.coord_x <> -30.0 RETURN count(a) as count"
}

for prop, query in structural_checks.items():
    try:
        result = neo4j_service.execute_query(query)
        count = result[0]['count'] if result else 0
        print(f"  {prop}: {count}개")
    except Exception as e:
        print(f"  {prop}: 오류 - {e}")

print("\n" + "=" * 60)

