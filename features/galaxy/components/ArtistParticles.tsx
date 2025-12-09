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
      
      // 호버 시 색상 밝기 증가
      if (i === hoveredInstanceId) {
        tempColor.setRGB(
          Math.min(1, (rgb.r / 255) * 1.5),
          Math.min(1, (rgb.g / 255) * 1.5),
          Math.min(1, (rgb.b / 255) * 1.5)
        );
      } else {
        // 최소 밝기 보장 (입자가 보이도록)
        tempColor.setRGB(
          Math.max(0.4, rgb.r / 255),
          Math.max(0.4, rgb.g / 255),
          Math.max(0.4, rgb.b / 255)
        );
      }
      
      meshRef.current!.setColorAt(i, tempColor);
    });
    
    meshRef.current.instanceMatrix.needsUpdate = true;
    if (meshRef.current.instanceColor) {
      meshRef.current.instanceColor.needsUpdate = true;
    }
  }, [artists, hoveredInstanceId, count]);
  
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
  
  // 호버 시 발광 효과 강화를 위한 애니메이션
  const materialRef = useRef<THREE.MeshPhysicalMaterial>(null);
  
  useFrame(() => {
    if (!meshRef.current || !materialRef.current) return;
    
    // 호버된 입자의 발광 강도 증가
    if (hoveredInstanceId !== null) {
      const artist = artists[hoveredInstanceId];
      const emissiveIntensity = 0.3 + scoreToEmissive(artist.scores.composite_score) * 0.5;
      materialRef.current.emissiveIntensity = emissiveIntensity;
    } else {
      materialRef.current.emissiveIntensity = 0.2;
    }
  });
  
  // Glow sprites 생성 (각 입자마다 발광 효과)
  const glowSprites = useMemo(() => {
    // Canvas로 radial gradient 텍스처 생성
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d')!;
    
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    gradient.addColorStop(0.3, 'rgba(255, 255, 255, 0.6)');
    gradient.addColorStop(0.6, 'rgba(255, 255, 255, 0.2)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);
    
    const texture = new THREE.CanvasTexture(canvas);
    
    return artists.map((artist, i) => {
      const isHovered = i === hoveredInstanceId;
      const scale = isHovered ? 3.5 : 2.5;
      
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
            opacity={isHovered ? 0.6 : 0.4}
            depthWrite={false}
            blending={THREE.AdditiveBlending}
          />
        </sprite>
      );
    });
  }, [artists, hoveredInstanceId]);

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
          roughness={0.15}
          metalness={0.05}
          clearcoat={0.9}
          clearcoatRoughness={0.05}
          emissive="#ffffff"
          emissiveIntensity={0.3}
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
