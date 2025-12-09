/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { createContext, useContext } from 'react';
import { useGalaxy } from '../features/galaxy/hooks/useGalaxy';

// ARGO 프로젝트 전용 AppContext 타입 정의
// useGalaxy hook의 반환값을 타입으로 사용
export type AppContextType = ReturnType<typeof useGalaxy>;

// Create the context with a default null value
export const AppContext = createContext<AppContextType | null>(null);

// Create a provider component that uses useGalaxy internally
export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const galaxyState = useGalaxy();
  return <AppContext.Provider value={galaxyState}>{children}</AppContext.Provider>;
};

// Create a custom hook for easy consumption
export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
