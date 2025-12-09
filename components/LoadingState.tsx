import React from 'react';

/**
 * LoadingState 컴포넌트
 * Task 4.2: 로딩 및 에러 상태 개선 (DDS 3.4.1)
 */
interface LoadingStateProps {
  message?: string;
  progress?: number; // 0-100
}

export const LoadingState: React.FC<LoadingStateProps> = ({ 
  message = 'Loading...',
  progress 
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="text-center">
        {/* 스켈레톤 UI */}
        <div className="mb-6">
          <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto" />
        </div>
        <p className="text-sm text-white/80 uppercase tracking-wider mb-2">{message}</p>
        {progress !== undefined && (
          <div className="w-64 h-1 bg-white/10 rounded-full overflow-hidden mx-auto">
            <div 
              className="h-full bg-white transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

