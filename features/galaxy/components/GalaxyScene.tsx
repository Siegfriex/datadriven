import React, { Suspense, useState, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { Stars, Stats } from '@react-three/drei';
import { ArtistParticles } from './ArtistParticles';
import { ArtistEdges } from './ArtistEdges';
import { GalaxyControls } from './GalaxyControls';
import { Artist } from '../../../types/argo';
import { addInstanceIds } from '../utils/coordinateTransform';
import mockArtistsData from '../../../data/mockArtists.json';

interface GalaxySceneProps {
  onArtistSelect: (artist: Artist, instanceId: number) => void;
  onArtistHover: (artist: Artist | null, instanceId: number | null) => void;
  selectedArtist?: Artist | null;
}

/**
 * GalaxyScene 컴포넌트
 * 메인 3D 갤러리 씬 설정
 */
export const GalaxyScene: React.FC<GalaxySceneProps> = ({
  onArtistSelect,
  onArtistHover,
  selectedArtist
}) => {
  const [hoveredArtist, setHoveredArtist] = useState<Artist | null>(null);
  
  // 데이터 중앙 관리: 한 번만 처리하여 모든 하위 컴포넌트에 전달
  const artists = useMemo(() => {
    return addInstanceIds(mockArtistsData as Artist[]);
  }, []);
  
  const selectedPosition = selectedArtist
    ? {
        x: selectedArtist.coordinates_3d.x,
        y: selectedArtist.coordinates_3d.y,
        z: selectedArtist.coordinates_3d.z,
        radius: selectedArtist.coordinates_3d.radius
      }
    : null;
  
  const handleArtistHover = (artist: Artist | null, instanceId: number | null) => {
    setHoveredArtist(artist);
    onArtistHover(artist, instanceId);
  };
  return (
    <div 
      className="fixed inset-0 w-screen h-screen bg-black" 
      style={{ 
        touchAction: 'none', 
        width: '100vw', 
        height: '100vh',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      }}
    >
      <Canvas
        camera={{ position: [15, 15, 15], fov: 60 }}
        gl={{ antialias: false, alpha: false }}
        style={{ 
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          display: 'block',
          margin: 0,
          padding: 0
        }}
      >
        {/* 배경 */}
        <color attach="background" args={['#050505']} />
        
        {/* 별 필드 배경 */}
        <Stars
          radius={100}
          depth={50}
          count={5000}
          factor={4}
          saturation={0}
          fade
        />
        
        {/* 3점 조명 설정 (Key, Fill, Rim) */}
        <ambientLight intensity={0.3} />
        {/* Key Light: 메인 조명 */}
        <pointLight position={[15, 15, 15]} intensity={1.2} distance={100} decay={2} />
        {/* Fill Light: 보조 조명 */}
        <pointLight position={[-10, 5, -10]} intensity={0.4} distance={100} decay={2} />
        {/* Rim Light: 후면 조명 (깊이감) */}
        <pointLight position={[0, -10, -15]} intensity={0.3} distance={100} decay={2} />
        
        {/* 핵심: 작가 데이터 시각화 */}
        <Suspense fallback={null}>
          <ArtistParticles
            artists={artists}
            onArtistSelect={onArtistSelect}
            onArtistHover={handleArtistHover}
          />
          {/* 연결선 시각화 */}
          <ArtistEdges
            selectedArtist={selectedArtist || null}
            hoveredArtist={hoveredArtist}
            artists={artists}
          />
        </Suspense>
        
        {/* 카메라 제어 */}
        <GalaxyControls selectedArtistPosition={selectedPosition} />
        
        {/* 성능 모니터링 (개발용) */}
        {process.env.NODE_ENV === 'development' && <Stats />}
      </Canvas>
    </div>
  );
};
