import React, { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Artist } from '../../../types/argo';

interface ArtistEdgesProps {
  selectedArtist: Artist | null;
  hoveredArtist: Artist | null;
  artists: Artist[];
}

/**
 * ArtistEdges 컴포넌트
 * 선택/호버된 작가와 협력 관계에 있는 작가들을 연결하는 선 시각화
 */
export const ArtistEdges: React.FC<ArtistEdgesProps> = ({
  selectedArtist,
  hoveredArtist,
  artists
}) => {
  const linesRef = useRef<THREE.LineSegments>(null);
  const materialRef = useRef<THREE.LineBasicMaterial>(null);
  
  // 현재 보여줄 작가 (선택 우선, 없으면 호버)
  const activeArtist = selectedArtist || hoveredArtist;
  
  // 연결선 데이터 계산
  const { positions, colors, distances } = useMemo(() => {
    if (!activeArtist || !activeArtist.collaborators) {
      return { positions: new Float32Array(0), colors: new Float32Array(0), distances: [] };
    }
    
    const artistMap = new Map(artists.map(a => [a.artist_id, a]));
    const edges: { from: Artist; to: Artist; distance: number }[] = [];
    
    // 협력 작가들과의 연결선 생성
    activeArtist.collaborators.forEach(collabId => {
      const collaborator = artistMap.get(collabId);
      if (collaborator) {
        const distance = Math.sqrt(
          Math.pow(activeArtist.coordinates_3d.x - collaborator.coordinates_3d.x, 2) +
          Math.pow(activeArtist.coordinates_3d.y - collaborator.coordinates_3d.y, 2) +
          Math.pow(activeArtist.coordinates_3d.z - collaborator.coordinates_3d.z, 2)
        );
        edges.push({ from: activeArtist, to: collaborator, distance });
      }
    });
    
    // 위치 배열 생성 (각 선은 2개의 점)
    const positions = new Float32Array(edges.length * 6);
    const colors = new Float32Array(edges.length * 6);
    const distances: number[] = [];
    
    edges.forEach((edge, i) => {
      const idx = i * 6;
      
      // 시작점
      positions[idx] = edge.from.coordinates_3d.x;
      positions[idx + 1] = edge.from.coordinates_3d.y;
      positions[idx + 2] = edge.from.coordinates_3d.z;
      
      // 끝점
      positions[idx + 3] = edge.to.coordinates_3d.x;
      positions[idx + 4] = edge.to.coordinates_3d.y;
      positions[idx + 5] = edge.to.coordinates_3d.z;
      
      // 거리에 따른 투명도 계산 (더 강한 가시성)
      const maxDistance = 50;
      const normalizedDistance = Math.min(edge.distance / maxDistance, 1);
      const opacity = 1 - normalizedDistance * 0.5; // 0.5 ~ 1.0 (더 밝게)
      
      // 색상 (더 강렬한 Neon Cyan)
      const r = 0.2;
      const g = 1.0;
      const b = 1.0;
      
      colors[idx] = r * opacity;
      colors[idx + 1] = g * opacity;
      colors[idx + 2] = b * opacity;
      colors[idx + 3] = r * opacity;
      colors[idx + 4] = g * opacity;
      colors[idx + 5] = b * opacity;
      
      distances.push(edge.distance);
    });
    
    return { positions, colors, distances };
  }, [activeArtist, artists]);
  
  // 페이드 인/아웃 애니메이션
  useFrame((state, delta) => {
    if (!materialRef.current) return;
    
    const targetOpacity = activeArtist ? 1 : 0;
    const currentOpacity = materialRef.current.opacity;
    
    // 부드러운 전환
    if (Math.abs(targetOpacity - currentOpacity) > 0.01) {
      materialRef.current.opacity = THREE.MathUtils.lerp(
        currentOpacity,
        targetOpacity,
        delta * 5
      );
    }
  });
  
  if (positions.length === 0) {
    return null;
  }
  
  return (
    <lineSegments ref={linesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial
        ref={materialRef}
        vertexColors
        transparent
        opacity={0}
        linewidth={1}
        depthWrite={false}
      />
    </lineSegments>
  );
};
