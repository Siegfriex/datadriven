/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/


import React, { useState, useEffect } from 'react';
import { GalaxyScene } from './features/galaxy/components/GalaxyScene';
import { LeftPanel } from './features/galaxy/components/LeftPanel';
import { RightPanel } from './features/galaxy/components/RightPanel';
import { AppProvider, useAppContext } from './context/AppContext';
import { NavigationMenu } from './components/NavigationMenu';

const AppContent: React.FC = () => {
    const { 
        selectArtist, 
        hoverArtist, 
        selectedArtist 
    } = useAppContext();

    const [isLeftPanelOpen, setIsLeftPanelOpen] = useState(false);
    const [isRightPanelOpen, setIsRightPanelOpen] = useState(false);

    // ESC 키로 패널 닫기
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                setIsLeftPanelOpen(false);
                setIsRightPanelOpen(false);
            }
        };
        window.addEventListener('keydown', handleEscape);
        return () => window.removeEventListener('keydown', handleEscape);
    }, []);

    return (
        <div className="fixed inset-0 w-screen h-screen bg-black text-white overflow-hidden font-sans" style={{ width: '100vw', height: '100vh' }}>
            {/* 전체화면 캔버스 - Task 2.3: 반응형 디자인 (PRD 3.2, DDS 2.3) */}
            <div className="w-full h-full md:w-[60%] lg:w-[60%]">
                <GalaxyScene 
                    onArtistSelect={(artist, id) => {
                        selectArtist(artist, id);
                        setIsRightPanelOpen(true);
                    }}
                    onArtistHover={hoverArtist}
                    selectedArtist={selectedArtist?.artist || null}
                />
            </div>
            
            {/* 좌패널: 미니멀 오버레이 - 반응형 너비 (데스크톱: 288px, 태블릿: 240px, 모바일: 전체화면) */}
            <LeftPanel 
                className={isLeftPanelOpen ? 'translate-x-0' : ''}
                onToggle={() => setIsLeftPanelOpen(!isLeftPanelOpen)}
            />
            
            {/* 우패널: 미니멀 오버레이 - 반응형 너비 */}
            <RightPanel 
                selectedArtist={selectedArtist?.artist || null} 
                className={isRightPanelOpen ? 'translate-x-0' : ''}
                onToggle={() => setIsRightPanelOpen(!isRightPanelOpen)}
            />
            
            {/* 패널 토글 버튼 (미니멀) - Task 4.1: 접근성 개선 */}
            <button
                onClick={() => setIsLeftPanelOpen(!isLeftPanelOpen)}
                className={`fixed top-6 left-6 z-50 text-white text-xs uppercase tracking-wider transition-opacity hover:opacity-100 ${
                    isLeftPanelOpen ? 'opacity-100' : 'opacity-40'
                }`}
                aria-label="Toggle Filters"
                aria-expanded={isLeftPanelOpen}
                aria-controls="left-panel"
            >
                Filter
            </button>
            
            {/* 우측 상단: 정보 패널 토글 */}
            {selectedArtist && (
                <button
                    onClick={() => setIsRightPanelOpen(!isRightPanelOpen)}
                    className={`fixed top-6 right-6 z-50 text-white text-xs uppercase tracking-wider transition-opacity hover:opacity-100 ${
                        isRightPanelOpen ? 'opacity-100' : 'opacity-40'
                    }`}
                    aria-label="Toggle Info"
                    aria-expanded={isRightPanelOpen}
                    aria-controls="right-panel"
                >
                    Info
                </button>
            )}
            
            {/* 패널 오버레이 (외부 클릭 시 닫기) */}
            {isLeftPanelOpen && (
                <div 
                    className="fixed inset-0 z-30 bg-black/20"
                    onClick={() => setIsLeftPanelOpen(false)}
                />
            )}
            {isRightPanelOpen && (
                <div 
                    className="fixed inset-0 z-30 bg-black/20"
                    onClick={() => setIsRightPanelOpen(false)}
                />
            )}
            
            {/* Task 3.2: 네비게이션 메뉴 */}
            <NavigationMenu 
                activeItem="analysis"
                onItemClick={(item) => {
                    console.log('Navigation item clicked:', item);
                    // 향후 React Router 통합 시 라우팅 처리
                }}
            />
        </div>
    );
};

const App: React.FC = () => {
    return (
        <AppProvider>
            <AppContent />
        </AppProvider>
    );
};

export default App;
