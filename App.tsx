/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/


import React, { useState, useEffect } from 'react';
import { GalaxyScene } from './features/galaxy/components/GalaxyScene';
import { LeftPanel } from './features/galaxy/components/LeftPanel';
import { RightPanel } from './features/galaxy/components/RightPanel';
import { AppProvider } from './context/AppContext';
import { useAppStoreComplete } from './hooks/useAppStore';
import { useGalaxy } from './features/galaxy/hooks/useGalaxy';

const AppContent: React.FC = () => {
    const { 
        selectArtist, 
        hoverArtist, 
        selectedArtist 
    } = useGalaxy();

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
            {/* 전체화면 캔버스 */}
            <GalaxyScene 
                onArtistSelect={(artist, id) => {
                    selectArtist(artist, id);
                    setIsRightPanelOpen(true);
                }}
                onArtistHover={hoverArtist}
                selectedArtist={selectedArtist?.artist || null}
            />
            
            {/* 좌패널: 미니멀 오버레이 (호버/클릭 시 표시) */}
            <LeftPanel 
                className={isLeftPanelOpen ? 'translate-x-0' : ''}
                onToggle={() => setIsLeftPanelOpen(!isLeftPanelOpen)}
            />
            
            {/* 우패널: 미니멀 오버레이 */}
            <RightPanel 
                selectedArtist={selectedArtist?.artist || null} 
                className={isRightPanelOpen ? 'translate-x-0' : ''}
                onToggle={() => setIsRightPanelOpen(!isRightPanelOpen)}
            />
            
            {/* 패널 토글 버튼 (미니멀) */}
            <button
                onClick={() => setIsLeftPanelOpen(!isLeftPanelOpen)}
                className={`fixed top-6 left-6 z-50 text-white text-xs uppercase tracking-wider transition-opacity hover:opacity-100 ${
                    isLeftPanelOpen ? 'opacity-100' : 'opacity-40'
                }`}
                aria-label="Toggle Filters"
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
        </div>
    );
};

const App: React.FC = () => {
    const store = useAppStoreComplete();
    return (
        <AppProvider value={store}>
            <AppContent />
        </AppProvider>
    );
};

export default App;
