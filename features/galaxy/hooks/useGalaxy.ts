import { useState, useCallback } from 'react';
import { Artist, SelectedArtist } from '../../../types/argo';

/**
 * useGalaxy 훅
 * 갤럭시 상태 관리 (useState 기반)
 */
export const useGalaxy = () => {
  const [selectedArtist, setSelectedArtist] = useState<SelectedArtist | null>(null);
  const [hoveredArtist, setHoveredArtist] = useState<SelectedArtist | null>(null);
  const [artists, setArtists] = useState<Artist[]>([]);
  
  // 작가 선택
  const selectArtist = useCallback((artist: Artist, instanceId: number) => {
    setSelectedArtist({
      artist,
      instanceId,
      hovered: false
    });
  }, []);
  
  // 작가 호버
  const hoverArtist = useCallback((artist: Artist | null, instanceId: number | null) => {
    if (artist && instanceId !== null) {
      setHoveredArtist({
        artist,
        instanceId,
        hovered: true
      });
    } else {
      setHoveredArtist(null);
    }
  }, []);
  
  // 선택 해제
  const clearSelection = useCallback(() => {
    setSelectedArtist(null);
  }, []);
  
  // 작가 목록 설정
  const setArtistsList = useCallback((newArtists: Artist[]) => {
    setArtists(newArtists);
  }, []);
  
  return {
    selectedArtist,
    hoveredArtist,
    artists,
    selectArtist,
    hoverArtist,
    clearSelection,
    setArtistsList
  };
};

