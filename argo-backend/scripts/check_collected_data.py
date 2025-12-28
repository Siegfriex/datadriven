"""
수집된 데이터 확인 스크립트
"""
import json
import os
from datetime import datetime

# 최신 파일 찾기
data_dir = "data"
files = [f for f in os.listdir(data_dir) if f.startswith("collected_artists_")]
if not files:
    print("수집된 데이터 파일이 없습니다.")
    exit(1)

latest_file = sorted(files)[-1]
print(f"최신 파일: {latest_file}")

# 데이터 로드
with open(os.path.join(data_dir, latest_file), "r", encoding="utf-8") as f:
    artists_data = json.load(f)

print(f"\n작가 수: {len(artists_data)}")

# 작가별 작품 데이터 확인
print("\n=== 작가별 작품 데이터 확인 ===")
artwork_count = 0
for artist in artists_data[:3]:
    name = artist.get("name", "Unknown")
    metadata = artist.get("metadata", {})
    artworks = metadata.get("artworks", [])
    print(f"{name}: 작품 {len(artworks)}개")
    if artworks:
        print(f"  첫 번째 작품: {artworks[0]}")

# 논문 데이터는 별도로 저장되지 않았을 수 있음
print("\n=== 논문 데이터 확인 ===")
# 논문 데이터는 점수 계산에만 사용되고 별도로 저장되지 않았을 수 있음
print("논문 데이터는 점수 계산에만 사용되었을 수 있습니다.")



