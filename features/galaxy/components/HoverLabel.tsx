import React from 'react';
import { Html } from '@react-three/drei';
import { Artist } from '../../../types/argo';

interface HoverLabelProps {
  artist: Artist | null;
  position: [number, number, number];
  visible: boolean;
}

/**
 * HoverLabel 컴포넌트
 * 호버 시 작가 이름을 표시하는 2D 오버레이 (Arario Style)
 */
export const HoverLabel: React.FC<HoverLabelProps> = ({
  artist,
  position,
  visible
}) => {
  if (!visible || !artist) return null;
  
  return (
    <Html
      position={position}
      occlude
      style={{
        pointerEvents: 'none',
        userSelect: 'none',
        transform: 'translate3d(-50%, -100%, 0)', // 중앙 정렬 및 위로 띄우기
        paddingBottom: '16px'
      }}
    >
      <div className="flex flex-col items-center gap-1">
        {/* 연결선 (선택적) */}
        <div className="w-px h-4 bg-gradient-to-b from-white/50 to-transparent opacity-50 mb-1" />
        
        <div className="
          relative overflow-hidden
          bg-black/90 backdrop-blur-xl
          border border-white/30 rounded
          px-5 py-3
          shadow-[0_8px_32px_rgba(0,0,0,0.8)]
          transition-all duration-200 ease-out
          group
        ">
          {/* 미세한 광택 효과 */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          
          <div className="relative z-10 flex flex-col items-start min-w-[140px]">
            <span className="text-xs font-semibold text-cyan-400 tracking-widest uppercase mb-1">
              {artist.segment_id?.split('_')[1] || 'ARTIST'}
            </span>
            <h3 className="text-lg font-bold text-white tracking-tight leading-tight drop-shadow-lg">
              {artist.name}
            </h3>
            {artist.alternativeName && (
              <span className="text-sm font-light text-white/60 mt-1 font-serif italic">
                {artist.alternativeName}
              </span>
            )}
            <div className="mt-2 flex gap-2 text-xs text-white/50">
              <span>Score: {Math.round(artist.scores.composite_score)}</span>
            </div>
          </div>
        </div>
      </div>
    </Html>
  );
};
