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
 * Task 1.2: 연결선 시각화 완성 - 관계 타입별 색상 구분
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
  
  // 연결선 타입별 색상 정의 (SRD 2.2.4)
  const EDGE_COLORS = {
    collaboration: { r: 0.2, g: 0.6, b: 1.0 }, // 파란색 - 협력자
    institution: { r: 0.2, g: 1.0, b: 0.4 }, // 초록색 - 소속 기관
    exhibition: { r: 1.0, g: 0.8, b: 0.2 }, // 황색 - 전시 참여
  };
  
  // 연결선 데이터 계산
  const { positions, colors, distances } = useMemo(() => {
    if (!activeArtist) {
      return { positions: new Float32Array(0), colors: new Float32Array(0), distances: [] };
    }
    
    const artistMap = new Map(artists.map(a => [a.artist_id, a]));
    const edges: { from: Artist; to: Artist; distance: number; type: 'collaboration' | 'institution' | 'exhibition' }[] = [];
    
    // 1. 협력 작가들과의 연결선 (strength ≥ 0.3)
    if (activeArtist.collaborations && activeArtist.collaborations.length > 0) {
      activeArtist.collaborations.forEach(collab => {
        if (collab.strength >= 0.3) {
          const collaborator = artistMap.get(collab.artist_id);
          if (collaborator) {
            const distance = Math.sqrt(
              Math.pow(activeArtist.coordinates_3d.x - collaborator.coordinates_3d.x, 2) +
              Math.pow(activeArtist.coordinates_3d.y - collaborator.coordinates_3d.y, 2) +
              Math.pow(activeArtist.coordinates_3d.z - collaborator.coordinates_3d.z, 2)
            );
            edges.push({ from: activeArtist, to: collaborator, distance, type: 'collaboration' });
          }
        }
      });
    }
    // 기존 collaborators 배열도 지원 (하위 호환성)
    else if (activeArtist.collaborators && activeArtist.collaborators.length > 0) {
      activeArtist.collaborators.forEach(collabId => {
        const collaborator = artistMap.get(collabId);
        if (collaborator) {
          const distance = Math.sqrt(
            Math.pow(activeArtist.coordinates_3d.x - collaborator.coordinates_3d.x, 2) +
            Math.pow(activeArtist.coordinates_3d.y - collaborator.coordinates_3d.y, 2) +
            Math.pow(activeArtist.coordinates_3d.z - collaborator.coordinates_3d.z, 2)
          );
          edges.push({ from: activeArtist, to: collaborator, distance, type: 'collaboration' });
        }
      });
    }
    
    // 2. 소속 기관과의 연결선 (향후 구현: 기관 위치 데이터 필요)
    // if (activeArtist.institutions && activeArtist.institutions.length > 0) {
    //   activeArtist.institutions.forEach(inst => {
    //     // 기관 위치 데이터가 필요함
    //   });
    // }
    
    // 3. 전시 참여 연결선 (향후 구현: 전시 위치 데이터 필요)
    // if (activeArtist.exhibitions && activeArtist.exhibitions.length > 0) {
    //   activeArtist.exhibitions.forEach(exh => {
    //     // 전시 위치 데이터가 필요함
    //   });
    // }
    
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
      
      // 거리에 따른 투명도 계산
      const maxDistance = 50;
      const normalizedDistance = Math.min(edge.distance / maxDistance, 1);
      const opacity = 1 - normalizedDistance * 0.5; // 0.5 ~ 1.0
      
      // 관계 타입별 색상 적용
      const edgeColor = EDGE_COLORS[edge.type];
      
      colors[idx] = edgeColor.r * opacity;
      colors[idx + 1] = edgeColor.g * opacity;
      colors[idx + 2] = edgeColor.b * opacity;
      colors[idx + 3] = edgeColor.r * opacity;
      colors[idx + 4] = edgeColor.g * opacity;
      colors[idx + 5] = edgeColor.b * opacity;
      
      distances.push(edge.distance);
    });
    
    return { positions, colors, distances };
  }, [activeArtist, artists]);
  
  // 페이드 인/아웃 애니메이션 (0.3초 fade-in, SRD 2.2.4)
  useFrame((state, delta) => {
    if (!materialRef.current) return;
    
    const targetOpacity = activeArtist ? 1 : 0;
    const currentOpacity = materialRef.current.opacity;
    
    // 부드러운 전환 (0.3초 = 약 5프레임 @ 60fps, delta * 5 ≈ 0.3초)
    if (Math.abs(targetOpacity - currentOpacity) > 0.01) {
      materialRef.current.opacity = THREE.MathUtils.lerp(
        currentOpacity,
        targetOpacity,
        delta * 5 // 약 0.3초 fade-in
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
