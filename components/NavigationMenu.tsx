import React from 'react';

/**
 * NavigationMenu 컴포넌트
 * Task 3.2: 네비게이션 메뉴 추가 (PRD 3.2, DDS 2.3)
 * 하단 메뉴: [분석] [군집] [이상치] [방법론] [비교] [프로필]
 */
interface NavigationMenuProps {
  activeItem?: string;
  onItemClick?: (item: string) => void;
}

export const NavigationMenu: React.FC<NavigationMenuProps> = ({ 
  activeItem, 
  onItemClick 
}) => {
  const menuItems = [
    { id: 'analysis', label: '분석' },
    { id: 'clusters', label: '군집' },
    { id: 'anomalies', label: '이상치' },
    { id: 'methodology', label: '방법론' },
    { id: 'compare', label: '비교' },
    { id: 'profile', label: '프로필' }
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-black/90 backdrop-blur-xl border-t border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex justify-center gap-8">
          {menuItems.map(item => (
            <button
              key={item.id}
              onClick={() => onItemClick?.(item.id)}
              className={`text-xs uppercase tracking-wider transition-all duration-200 ${
                activeItem === item.id
                  ? 'text-white border-b-2 border-white pb-1'
                  : 'text-white/60 hover:text-white/80'
              }`}
              aria-label={item.label}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

