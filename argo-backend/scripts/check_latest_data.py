import json
import os

files = [f for f in os.listdir('data') if f.startswith('collected_artists_')]
latest = sorted(files)[-1] if files else None
print(f'최신 파일: {latest}')

if latest:
    with open(f'data/{latest}', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'작가 수: {len(data)}')
    
    if data:
        meta = data[0].get('metadata', {})
        artworks = meta.get('artworks', [])
        print(f'첫 번째 작가 작품 수: {len(artworks)}')
        if artworks:
            print(f'첫 번째 작품 샘플: {artworks[0]}')

