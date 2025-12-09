/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { createContext, useContext } from 'react';

// ARGO 프로젝트 전용 AppContext 타입 정의
// 현재는 최소한의 구조만 유지 (필요시 확장 가능)
export interface AppContextType {
  // ARGO 프로젝트에 필요한 상태를 여기에 추가
  // 현재는 useGalaxy hook으로 상태를 관리하므로 빈 구조
}

// Create the context with a default null value
export const AppContext = createContext<AppContextType | null>(null);

// Create a provider component
export const AppProvider: React.FC<{ value: AppContextType; children: React.ReactNode }> = ({ value, children }) => {
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Create a custom hook for easy consumption
export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
