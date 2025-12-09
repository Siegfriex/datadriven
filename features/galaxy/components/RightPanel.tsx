import React, { useEffect, useState } from 'react';
import { Artist } from '../../../types/argo';

interface RightPanelProps {
  selectedArtist: Artist | null;
  className?: string;
  onToggle?: () => void;
}

/**
 * RightPanel 컴포넌트
 * 미니멀한 하얀색 타이포 중심의 작가 정보 패널 (개선됨)
 */
export const RightPanel: React.FC<RightPanelProps> = ({ selectedArtist, className = '', onToggle }) => {
  const [animate, setAnimate] = useState(false);
  
  // 작가 선택 시 애니메이션 트리거
  useEffect(() => {
    if (selectedArtist) {
      setAnimate(false);
      setTimeout(() => setAnimate(true), 50);
    }
  }, [selectedArtist]);

  // 선택된 작가가 없을 때의 빈 상태 UI
  if (!selectedArtist) {
    return (
      <aside className={`fixed right-0 top-0 h-full w-96 z-40 flex flex-col pointer-events-none bg-black/95 backdrop-blur-xl transition-transform duration-300 ease-out transform translate-x-full border-l border-white/5 ${className}`}>
        <div className="flex-1 flex items-center justify-center p-8">
          <p className="text-sm text-white/40 uppercase tracking-widest text-center">
            Select an artist to view details
          </p>
        </div>
      </aside>
    );
  }

  // SVG 레이더 차트 데이터 계산
  const scores = selectedArtist.scores;
  const maxScore = 100;
  const points = [
    { label: 'INST', value: scores.inst_score, angle: 0 },
    { label: 'ACAD', value: scores.acad_score, angle: 90 },
    { label: 'MEDIA', value: scores.media_score, angle: 180 },
    { label: 'NET', value: scores.network_score, angle: 270 },
  ];

  const radius = 60;
  const center = 80;
  
  const polygonPoints = points.map(p => {
    const r = (p.value / maxScore) * radius;
    const x = center + r * Math.cos((p.angle - 90) * (Math.PI / 180));
    const y = center + r * Math.sin((p.angle - 90) * (Math.PI / 180));
    return `${x},${y}`;
  }).join(' ');

  const bgPoints = points.map(p => {
    const x = center + radius * Math.cos((p.angle - 90) * (Math.PI / 180));
    const y = center + radius * Math.sin((p.angle - 90) * (Math.PI / 180));
    return `${x},${y}`;
  }).join(' ');

  return (
    <aside className={`fixed right-0 top-0 h-full w-96 z-40 flex flex-col pointer-events-none bg-black/98 backdrop-blur-xl transition-transform duration-300 ease-out transform translate-x-full border-l border-white/20 shadow-[-10px_0_40px_rgba(0,0,0,0.5)] ${className}`}>
      <div className="flex-1 overflow-y-auto pointer-events-auto scrollbar-hide">
        {/* 닫기 버튼 */}
        <div className="sticky top-0 z-50 bg-black/80 backdrop-blur-lg border-b border-white/10 p-4 flex justify-between items-center">
          <h2 className="text-xs text-white/60 uppercase tracking-widest">Artist Details</h2>
          {onToggle && (
            <button 
              onClick={onToggle}
              className="text-white/60 hover:text-white transition-colors p-2 hover:bg-white/10 rounded"
              aria-label="Close panel"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          )}
        </div>

        <div className="p-8">
          {/* 프로필 헤더 */}
          <header className="mb-10">
            <div className="mb-3">
              <span className="inline-block px-3 py-1 bg-cyan-500/20 border border-cyan-400/30 rounded-full text-xs font-semibold text-cyan-300 uppercase tracking-wider mb-3">
                {selectedArtist.segment_id?.split('_')[1]}
              </span>
            </div>
            <h1 className="text-4xl font-bold text-white leading-tight mb-3 drop-shadow-lg">
              {selectedArtist.name}
            </h1>
            <p className="text-base text-white/70 mb-4 font-serif italic">
              {selectedArtist.alternativeName}
            </p>
            <div className="flex gap-4 text-sm text-white/50">
              <span className="font-medium">{selectedArtist.birth_year}</span>
              <span>•</span>
              <span className="capitalize">{selectedArtist.career_stage}</span>
            </div>
          </header>

        {/* 점수 시각화 (레이더 차트 with animation) */}
        <section className="mb-12">
          <div className="flex items-center justify-center py-6">
            <div className="relative w-48 h-48">
              <svg width="192" height="192" viewBox="0 0 192 192">
                {/* 배경 가이드 */}
                <circle cx={center} cy={center} r={radius} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                <circle cx={center} cy={center} r={radius * 0.66} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />
                <circle cx={center} cy={center} r={radius * 0.33} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />
                <path d={`M${center},${center} L${center},${center - radius} M${center},${center} L${center + radius},${center} M${center},${center} L${center},${center + radius} M${center},${center} L${center - radius},${center}`} stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                
                {/* 데이터 폴리곤 with animation */}
                <polygon 
                  points={polygonPoints} 
                  fill="rgba(255, 255, 255, 0.15)" 
                  stroke="white" 
                  strokeWidth="1.5"
                  className={`transition-all duration-700 ${animate ? 'opacity-100 scale-100' : 'opacity-0 scale-50'}`}
                  style={{ 
                    transformOrigin: `${center}px ${center}px`,
                    filter: 'drop-shadow(0 0 4px rgba(255,255,255,0.4))'
                  }}
                />
                
                {/* 라벨 */}
                <text x={center} y={center - radius - 8} textAnchor="middle" fill="rgba(255,255,255,0.6)" fontSize="9" fontWeight="300">INST</text>
                <text x={center + radius + 12} y={center + 4} textAnchor="middle" fill="rgba(255,255,255,0.6)" fontSize="9" fontWeight="300">ACAD</text>
                <text x={center} y={center + radius + 14} textAnchor="middle" fill="rgba(255,255,255,0.6)" fontSize="9" fontWeight="300">MEDIA</text>
                <text x={center - radius - 12} y={center + 4} textAnchor="middle" fill="rgba(255,255,255,0.6)" fontSize="9" fontWeight="300">NET</text>
              </svg>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            {points.map(p => (
              <div key={p.label} className="flex justify-between items-center text-xs">
                <span className="text-white/60 uppercase tracking-wider">{p.label}</span>
                <span className="text-white font-light">{Math.round(p.value)}</span>
              </div>
            ))}
          </div>
        </section>

        {/* 구조주의 분석 */}
        <section>
          <h2 className="text-xs text-white/60 uppercase tracking-widest mb-6">Analysis</h2>
          
          <div className="space-y-4 text-sm font-light leading-relaxed text-white/80">
            <p>
              Dominant capital: <span className="text-white">{Object.entries(scores).reduce((a, b) => a[1] > b[1] ? a : b)[0].split('_')[0]}</span>
            </p>
            <p>
              Position within {selectedArtist.segment_id?.split('_')[1]} field shows upward mobility driven by institutional recognition.
            </p>
          </div>
        </section>
        </div>
      </div>
    </aside>
  );
};
