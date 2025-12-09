import React, { useRef, useMemo, useState, useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { Artist } from '../../../types/argo';
import { scoreToRGB, scoreToEmissive } from '../utils/colorMapping';
import { useFrame } from '@react-three/fiber';
import { HoverLabel } from './HoverLabel';

interface ArtistParticlesProps {
  artists: Artist[];
  onArtistSelect?: (artist: Artist, instanceId: number) => void;
  onArtistHover?: (artist: Artist | null, instanceId: number | null) => void;
}

/**
 * ArtistParticles 컴포넌트
 * InstancedMesh 기반 입자 시스템으로 작가들을 시각화
 * Task 3.1: 성능 최적화 (LOD, 컬링) - SRD 2.2.2
 */
export const ArtistParticles: React.FC<ArtistParticlesProps> = ({
  artists,
  onArtistSelect,
  onArtistHover
}) => {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const [hoveredInstanceId, setHoveredInstanceId] = useState<number | null>(null);
  const [selectedInstanceId, setSelectedInstanceId] = useState<number | null>(null);
  const { raycaster, pointer, camera } = useThree();
  
  const count = artists.length;
  
  // 초기 배치 및 색상 설정
  useEffect(() => {
    if (!meshRef.current) return;
    
    const tempObject = new THREE.Object3D();
    const tempColor = new THREE.Color();
    
    // InstancedMesh에 색상 attribute 생성 (한 번만)
    if (!meshRef.current.instanceColor) {
      const colors = new Float32Array(count * 3);
      for (let i = 0; i < count; i++) {
        colors[i * 3] = 1; // R
        colors[i * 3 + 1] = 1; // G
        colors[i * 3 + 2] = 1; // B
      }
      meshRef.current.geometry.setAttribute('color', new THREE.InstancedBufferAttribute(colors, 3));
    }
    
    artists.forEach((artist, i) => {
      const { x, y, z, radius } = artist.coordinates_3d;
      
      // 위치 설정
      tempObject.position.set(x, y, z);
      
      // 크기 설정 - 50% 축소로 공간감 확보
      const baseScale = Math.max(0.25, radius / 20); // 최소 0.25 스케일 (50% 축소)
      const hoverScale = i === hoveredInstanceId ? baseScale * 2.0 : baseScale;
      tempObject.scale.set(hoverScale, hoverScale, hoverScale);
      
      tempObject.updateMatrix();
      meshRef.current!.setMatrixAt(i, tempObject.matrix);
      
      // 색상 설정 (점수 기반 RGB)
      const rgb = scoreToRGB(
        artist.scores.inst_score,
        artist.scores.acad_score,
        artist.scores.media_score
      );
      
      // 입자 가시성 개선: 밝기 조정 (하얀색 덩어리 방지)
      // 최소 밝기: 0.2-0.3 (기존 0.5에서 대폭 감소)
      // 호버/선택 시 밝기 증가: 1.3x-1.5x (기존 2.0x-2.2x에서 감소)
      const isHovered = i === hoveredInstanceId;
      const isSelected = i === selectedInstanceId;
      
      if (isHovered || isSelected) {
        // 호버/선택 시 밝기 증가 (1.3x-1.5x로 감소)
        const brightnessMultiplier = isSelected ? 1.5 : 1.3;
        tempColor.setRGB(
          Math.min(1, (rgb.r / 255) * brightnessMultiplier),
          Math.min(1, (rgb.g / 255) * brightnessMultiplier),
          Math.min(1, (rgb.b / 255) * brightnessMultiplier)
        );
      } else {
        // 최소 밝기 보장 (0.2-0.3으로 감소, 점수에 따라 차등 적용)
        const minBrightness = Math.max(0.2, Math.min(0.3, artist.scores.composite_score / 300));
        tempColor.setRGB(
          Math.max(minBrightness, rgb.r / 255),
          Math.max(minBrightness, rgb.g / 255),
          Math.max(minBrightness, rgb.b / 255)
        );
      }
      
      meshRef.current!.setColorAt(i, tempColor);
    });
    
    meshRef.current.instanceMatrix.needsUpdate = true;
    if (meshRef.current.instanceColor) {
      meshRef.current.instanceColor.needsUpdate = true;
    }
  }, [artists, hoveredInstanceId, selectedInstanceId, count]);
  
  // 호버/클릭 이벤트 처리
  const handlePointerMove = (event: any) => {
    if (!meshRef.current) return;
    
    const instanceId = event.instanceId;
    if (instanceId !== undefined && instanceId < artists.length) {
      const artist = artists[instanceId];
      setHoveredInstanceId(instanceId);
      onArtistHover?.(artist, instanceId);
      event.stopPropagation();
    } else {
      setHoveredInstanceId(null);
      onArtistHover?.(null, null);
    }
  };
  
  const handleClick = (event: any) => {
    if (!meshRef.current) return;
    
    const instanceId = event.instanceId;
    if (instanceId !== undefined && instanceId < artists.length) {
      const artist = artists[instanceId];
      setSelectedInstanceId(instanceId);
      onArtistSelect?.(artist, instanceId);
      event.stopPropagation();
    }
  };
  
  // 호버된 작가의 라벨 위치 계산
  const hoveredArtist = hoveredInstanceId !== null ? artists[hoveredInstanceId] : null;
  const hoveredPosition: [number, number, number] | null = hoveredArtist
    ? [
        hoveredArtist.coordinates_3d.x,
        hoveredArtist.coordinates_3d.y + hoveredArtist.coordinates_3d.radius + 1,
        hoveredArtist.coordinates_3d.z
      ]
    : null;
  
  // 발광 효과 조정: 하얀색 덩어리 방지를 위해 대폭 감소
  // 기본 발광 강도: 0.05-0.1 (기존 0.2에서 감소)
  // 호버 시: 0.1-0.15 (기존 0.5에서 감소)
  // 선택 시: 0.15-0.2 (기존 0.7에서 감소)
  const materialRef = useRef<THREE.MeshPhysicalMaterial>(null);
  
  useFrame(() => {
    if (!meshRef.current || !materialRef.current) return;
    
    // 호버/선택된 입자의 발광 강도 증가 (대폭 감소)
    if (hoveredInstanceId !== null || selectedInstanceId !== null) {
      const activeId = selectedInstanceId !== null ? selectedInstanceId : hoveredInstanceId;
      if (activeId !== null) {
        const artist = artists[activeId];
        const baseEmissive = scoreToEmissive(artist.scores.composite_score);
        // 호버: 0.1-0.15, 선택: 0.15-0.2 (기존 대비 대폭 감소)
        const intensityMultiplier = selectedInstanceId !== null ? 0.15 : 0.1;
        materialRef.current.emissiveIntensity = Math.min(0.2, baseEmissive * 0.2 + intensityMultiplier);
      }
    } else {
      // 기본 발광 강도 (0.05-0.1로 감소)
      materialRef.current.emissiveIntensity = 0.05;
    }
  });
  
  // 아우라 표시 조정: 하얀색 덩어리 방지를 위해 대폭 감소
  // 반경: 기본 1.2x, 호버 1.5x, 선택 2x (기존 2x-4x에서 감소)
  // Opacity: 기본 0.1, 호버 0.2, 선택 0.3 (기존 0.4-0.8에서 감소)
  const glowSprites = useMemo(() => {
    // Canvas로 radial gradient 텍스처 생성 (더 부드러운 그라데이션)
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d')!;
    
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
    gradient.addColorStop(0.2, 'rgba(255, 255, 255, 0.3)');
    gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.1)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);
    
    const texture = new THREE.CanvasTexture(canvas);
    
    return artists.map((artist, i) => {
      const isHovered = i === hoveredInstanceId;
      const isSelected = i === selectedInstanceId;
      // 아우라 반경: 기본 1.2x, 호버 1.5x, 선택 2x (대폭 감소)
      const baseRadius = artist.coordinates_3d.radius;
      const scale = isSelected ? baseRadius * 2 : (isHovered ? baseRadius * 1.5 : baseRadius * 1.2);
      
      return (
        <sprite
          key={artist.artist_id}
          position={[
            artist.coordinates_3d.x,
            artist.coordinates_3d.y,
            artist.coordinates_3d.z
          ]}
          scale={[scale, scale, scale]}
          raycast={() => null}
        >
          <spriteMaterial
            map={texture}
            transparent
            opacity={isSelected ? 0.3 : (isHovered ? 0.2 : 0.1)}
            depthWrite={false}
            blending={THREE.AdditiveBlending}
          />
        </sprite>
      );
    });
  }, [artists, hoveredInstanceId, selectedInstanceId]);

  return (
    <>
      {/* Glow layer (background) */}
      {glowSprites}
      
      {/* Core spheres */}
      <instancedMesh
        ref={meshRef}
        args={[undefined, undefined, count]}
        onPointerMove={handlePointerMove}
        onClick={handleClick}
      >
        <sphereGeometry args={[0.8, 16, 16]} />
        <meshPhysicalMaterial
          ref={materialRef}
          vertexColors={true} // InstancedMesh instanceColor 사용
          roughness={0.3}
          metalness={0.1}
          clearcoat={0.5}
          clearcoatRoughness={0.1}
          emissive="#000000"
          emissiveIntensity={0.05}
        />
      </instancedMesh>
      
      {/* 호버 라벨 */}
      {hoveredPosition && hoveredArtist && (
        <HoverLabel
          artist={hoveredArtist}
          position={hoveredPosition}
          visible={true}
        />
      )}
    </>
  );
};
