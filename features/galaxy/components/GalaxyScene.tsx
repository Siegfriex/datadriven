import React, { Suspense, useState, useMemo, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Stars, Stats } from '@react-three/drei';
import { ArtistParticles } from './ArtistParticles';
import { ArtistEdges } from './ArtistEdges';
import { GalaxyControls } from './GalaxyControls';
import { Artist } from '../../../types/argo';
import { addInstanceIds } from '../utils/coordinateTransform';
import { useAppContext } from '../../../context/AppContext';
import mockArtistsData from '../../../data/mockArtists.json';

interface GalaxySceneProps {
  onArtistSelect: (artist: Artist, instanceId: number) => void;
  onArtistHover: (artist: Artist | null, instanceId: number | null) => void;
  selectedArtist?: Artist | null;
}

/**
 * GalaxyScene 컴포넌트
 * 메인 3D 갤러리 씬 설정
 * Task 1.1: 필터 동적 업데이트 구현
 */
export const GalaxyScene: React.FC<GalaxySceneProps> = ({
  onArtistSelect,
  onArtistHover,
  selectedArtist
}) => {
  const [hoveredArtist, setHoveredArtist] = useState<Artist | null>(null);
  const { filteredArtists, setArtistsList } = useAppContext();
  
  // 초기 데이터 로드 및 필터 적용
  const allArtists = useMemo(() => {
    return addInstanceIds(mockArtistsData as Artist[]);
  }, []);
  
  // useGalaxy에 전체 작가 목록 설정
  useEffect(() => {
    setArtistsList(allArtists);
  }, [allArtists, setArtistsList]);
  
  // 필터된 작가 목록 사용 (필터가 없으면 전체 목록)
  const artists = filteredArtists.length > 0 ? filteredArtists : allArtists;
  
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
      {/* Task 3.1: 성능 최적화 - 뷰 프러스텀 컬링 활성화 */}
      <Canvas
        camera={{ position: [15, 15, 15], fov: 60 }}
        gl={{ 
          antialias: false, 
          alpha: false,
          // 성능 최적화 설정
          powerPreference: 'high-performance',
          stencil: false,
          depth: true
        }}
        // 뷰 프러스텀 컬링 활성화
        frameloop="always"
        performance={{ min: 0.5 }}
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
