import { useState, useCallback, useMemo } from 'react';
import { Artist, SelectedArtist, FilterState } from '../../../types/argo';

/**
 * useGalaxy 훅
 * 갤럭시 상태 관리 (useState 기반)
 * Task 1.1: 필터 동적 업데이트 구현
 */
export const useGalaxy = () => {
  const [selectedArtist, setSelectedArtist] = useState<SelectedArtist | null>(null);
  const [hoveredArtist, setHoveredArtist] = useState<SelectedArtist | null>(null);
  const [artists, setArtists] = useState<Artist[]>([]);
  const [filters, setFilters] = useState<FilterState>({});
  
  // 필터 적용 함수 (Task 1.1: DDS 2.1.4)
  const applyFilters = useCallback((artistsList: Artist[], filterState: FilterState): Artist[] => {
    return artistsList.filter(artist => {
      // 세그먼트 필터
      if (filterState.segment_ids && filterState.segment_ids.length > 0) {
        if (!artist.segment_id || !filterState.segment_ids.includes(artist.segment_id)) {
          return false;
        }
      }
      
      // 경력 단계 필터
      if (filterState.career_stages && filterState.career_stages.length > 0) {
        if (!artist.career_stage || !filterState.career_stages.includes(artist.career_stage)) {
          return false;
        }
      }
      
      // 점수 범위 필터
      if (filterState.score_ranges) {
        const { inst, acad, media, network } = filterState.score_ranges;
        if (inst && (artist.scores.inst_score < inst[0] || artist.scores.inst_score > inst[1])) {
          return false;
        }
        if (acad && (artist.scores.acad_score < acad[0] || artist.scores.acad_score > acad[1])) {
          return false;
        }
        if (media && (artist.scores.media_score < media[0] || artist.scores.media_score > media[1])) {
          return false;
        }
        if (network && (artist.scores.network_score < network[0] || artist.scores.network_score > network[1])) {
          return false;
        }
      }
      
      // 지역 필터 (향후 구현)
      // 기관 필터 (향후 구현)
      
      return true;
    });
  }, []);
  
  // 필터된 작가 목록 (useMemo로 최적화)
  const filteredArtists = useMemo(() => {
    return applyFilters(artists, filters);
  }, [artists, filters, applyFilters]);
  
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
  
  // 필터 업데이트
  const updateFilters = useCallback((newFilters: FilterState) => {
    setFilters(newFilters);
  }, []);
  
  // 필터 리셋
  const resetFilters = useCallback(() => {
    setFilters({});
  }, []);
  
  return {
    selectedArtist,
    hoveredArtist,
    artists,
    filteredArtists,
    filters,
    selectArtist,
    hoverArtist,
    clearSelection,
    setArtistsList,
    updateFilters,
    resetFilters
  };
};

