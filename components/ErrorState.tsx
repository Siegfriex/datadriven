import React from 'react';

/**
 * ErrorState 컴포넌트
 * Task 4.2: 로딩 및 에러 상태 개선 (DDS 3.4.2)
 */
interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  type?: 'api' | 'rendering';
}

export const ErrorState: React.FC<ErrorStateProps> = ({ 
  message, 
  onRetry,
  type = 'api'
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="text-center max-w-md mx-auto px-6">
        <div className="mb-6">
          <div className="w-16 h-16 border-2 border-red-500/50 rounded-full flex items-center justify-center mx-auto">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="32" 
              height="32" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
              className="text-red-500"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
        </div>
        <h2 className="text-lg font-semibold text-white mb-2">
          {type === 'api' ? 'API Error' : 'Rendering Error'}
        </h2>
        <p className="text-sm text-white/80 mb-6">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-6 py-2 text-xs uppercase tracking-wider text-white border border-white/20 hover:border-white/40 rounded transition-all duration-200"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
};

