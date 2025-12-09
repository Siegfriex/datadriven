import fs from 'fs';

const artists = [];
const segments = [
  'contemporary_monochrome_KR',
  'contemporary_abstract_KR',
  'contemporary_media_KR',
  'contemporary_sculpture_KR',
  'contemporary_installation_KR'
];
const stages = ['early', 'mid', 'late'];

// 군집 중심점 (6개 군집)
const clusters = [
  [25, 20, 20],   // 상위권 군집
  [15, 15, 15],   // 중상위 군집
  [5, 5, 5],      // 중위 군집
  [-5, -5, -5],   // 중하위 군집
  [-15, -15, -15], // 하위권 군집
  [-25, -20, -20]  // 최하위 군집
];

for (let i = 1; i <= 100; i++) {
  const clusterIdx = Math.floor((i - 1) / 17);
  const cluster = clusters[clusterIdx] || clusters[0];
  const segment = segments[i % segments.length];
  const stage = stages[i % stages.length];
  
  // 군집 중심에서 약간의 변동 추가
  const baseScores = {
    inst: cluster[0] + (Math.random() * 20 - 10),
    acad: cluster[1] + (Math.random() * 20 - 10),
    media: cluster[2] + (Math.random() * 20 - 10)
  };
  
  // 점수를 0-100 범위로 정규화
  const inst_score = Math.max(0, Math.min(100, baseScores.inst + 50));
  const acad_score = Math.max(0, Math.min(100, baseScores.acad + 50));
  const media_score = Math.max(0, Math.min(100, baseScores.media + 50));
  const network_score = Math.max(0, Math.min(100, (inst_score + acad_score + media_score) / 3 + (Math.random() * 20 - 10)));
  const composite_score = inst_score * 0.3 + acad_score * 0.2 + media_score * 0.25 + network_score * 0.25;
  
  // 3D 좌표 계산 (x=제도, y=학술, z=담론, 범위 -30 ~ 30)
  const x = (inst_score / 100 * 60 - 30);
  const y = (acad_score / 100 * 60 - 30);
  const z = (media_score / 100 * 60 - 30);
  const radius = 10 + network_score / 5;
  
  artists.push({
    artist_id: `artist_${String(i).padStart(3, '0')}`,
    name: `작가${i}`,
    alternativeName: `Artist${i}`,
    birth_year: 1950 + Math.floor(Math.random() * 50),
    segment_id: segment,
    career_stage: stage,
    scores: {
      inst_score: Math.round(inst_score * 10) / 10,
      acad_score: Math.round(acad_score * 10) / 10,
      media_score: Math.round(media_score * 10) / 10,
      network_score: Math.round(network_score * 10) / 10,
      composite_score: Math.round(composite_score * 10) / 10
    },
    coordinates_3d: {
      x: Math.round(x * 10) / 10,
      y: Math.round(y * 10) / 10,
      z: Math.round(z * 10) / 10,
      radius: Math.round(radius * 10) / 10
    }
  });
}

fs.writeFileSync('data/mockArtists.json', JSON.stringify(artists, null, 2));
console.log(`Generated ${artists.length} artists`);

