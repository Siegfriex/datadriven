import React, { useState, useEffect } from 'react';
import { useAppContext } from '../../../context/AppContext';
import { FilterState } from '../../../types/argo';

interface LeftPanelProps {
  className?: string;
  onToggle?: () => void;
}

/**
 * LeftPanel 컴포넌트
 * 미니멀한 하얀색 타이포 중심의 필터 패널 (개선됨)
 * Task 1.1: 필터 동적 업데이트 구현
 */
export const LeftPanel: React.FC<LeftPanelProps> = ({ className = '', onToggle }) => {
  const { filters, updateFilters, resetFilters, filteredArtists, artists } = useAppContext();
  const [selectedSegments, setSelectedSegments] = useState<string[]>(filters.segment_ids || []);
  const [selectedCareer, setSelectedCareer] = useState<string[]>(
    filters.career_stages?.map(s => s.charAt(0).toUpperCase() + s.slice(1)) || []
  );
  
  // 필터 변경 시 useGalaxy의 필터 상태 업데이트
  useEffect(() => {
    const newFilters: FilterState = {
      segment_ids: selectedSegments.length > 0 ? selectedSegments : undefined,
      career_stages: selectedCareer.length > 0 
        ? selectedCareer.map(c => c.toLowerCase() as 'early' | 'mid' | 'late')
        : undefined
    };
    updateFilters(newFilters);
  }, [selectedSegments, selectedCareer, updateFilters]);
  
  const toggleSegment = (segment: string) => {
    setSelectedSegments(prev =>
      prev.includes(segment)
        ? prev.filter(s => s !== segment)
        : [...prev, segment]
    );
  };
  
  const toggleCareer = (career: string) => {
    setSelectedCareer(prev =>
      prev.includes(career)
        ? prev.filter(c => c !== career)
        : [...prev, career]
    );
  };
  
  const handleResetFilters = () => {
    setSelectedSegments([]);
    setSelectedCareer([]);
    resetFilters();
  };
  
  return (
    /* Task 2.3: 반응형 디자인 - 데스크톱: 288px(w-72), 태블릿: 240px(w-60), 모바일: 전체화면(w-full) */
    <aside 
      id="left-panel"
      className={`fixed left-0 top-0 h-full w-full md:w-60 lg:w-72 z-40 flex flex-col pointer-events-none transition-transform duration-300 ease-out transform -translate-x-full md:translate-x-0 ${className}`}
      role="complementary"
      aria-label="Filter and statistics panel"
    >
      <div className="flex-1 overflow-y-auto pointer-events-auto bg-black/95 backdrop-blur-xl p-8 scrollbar-hide border-r border-white/5">
        {/* 헤더 */}
        <div className="mb-12">
          <h1 className="text-2xl font-light tracking-tight text-white mb-2">ARGO</h1>
          <p className="text-xs text-white/60 uppercase tracking-widest">Galaxy</p>
        </div>

        {/* 통계 */}
        <section className="mb-12">
          <div className="mb-6">
            <div className="text-4xl font-light text-white mb-1">{filteredArtists.length}</div>
            <div className="text-xs text-white/60 uppercase tracking-wider">Artists</div>
            {artists.length > 0 && filteredArtists.length < artists.length && (
              <div className="text-xs text-white/40 mt-1">
                ({artists.length} total)
              </div>
            )}
          </div>
          <div className="mb-6">
            <div className="text-4xl font-light text-white mb-1">6</div>
            <div className="text-xs text-white/60 uppercase tracking-wider">Clusters</div>
          </div>
        </section>

        {/* 필터 */}
        <section>
          <h2 className="text-xs text-white/60 uppercase tracking-widest mb-6">Filters</h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-light text-white mb-4">Segment</h3>
              <div className="space-y-2">
                {['Abstract', 'Monochrome', 'Media', 'Sculpture', 'Installation'].map((item) => {
                  const isSelected = selectedSegments.includes(item);
                  return (
                    <label 
                      key={item} 
                      className="flex items-center gap-3 cursor-pointer group"
                      onClick={() => toggleSegment(item)}
                      role="checkbox"
                      aria-checked={isSelected}
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          toggleSegment(item);
                        }
                      }}
                    >
                      <div className={`w-2 h-2 border transition-all duration-200 ${
                        isSelected 
                          ? 'bg-white border-white shadow-[0_0_8px_rgba(255,255,255,0.6)]' 
                          : 'border-white/40 group-hover:border-white'
                      }`} />
                      <span className={`text-xs transition-colors uppercase tracking-wider ${
                        isSelected 
                          ? 'text-white font-normal' 
                          : 'text-white/80 group-hover:text-white'
                      }`}>
                        {item}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-light text-white mb-4">Career</h3>
              <div className="space-y-2">
                {['Early', 'Mid', 'Late'].map((item) => {
                  const isSelected = selectedCareer.includes(item);
                  return (
                    <label 
                      key={item} 
                      className="flex items-center gap-3 cursor-pointer group"
                      onClick={() => toggleCareer(item)}
                      role="checkbox"
                      aria-checked={isSelected}
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          toggleCareer(item);
                        }
                      }}
                    >
                      <div className={`w-2 h-2 border transition-all duration-200 ${
                        isSelected 
                          ? 'bg-white border-white shadow-[0_0_8px_rgba(255,255,255,0.6)]' 
                          : 'border-white/40 group-hover:border-white'
                      }`} />
                      <span className={`text-xs transition-colors uppercase tracking-wider ${
                        isSelected 
                          ? 'text-white font-normal' 
                          : 'text-white/80 group-hover:text-white'
                      }`}>
                        {item}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>
          </div>
          
          {/* 필터 리셋 버튼 */}
          {(selectedSegments.length > 0 || selectedCareer.length > 0) && (
            <div className="mt-8 pt-6 border-t border-white/10">
              <button
                onClick={handleResetFilters}
                className="w-full text-xs text-white/60 uppercase tracking-wider hover:text-white transition-colors duration-200 py-2"
              >
                Reset Filters
              </button>
            </div>
          )}
        </section>
      </div>
    </aside>
  );
};
