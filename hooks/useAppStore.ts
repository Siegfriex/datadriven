/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import { AppContextType } from '../context/AppContext';

/**
 * useAppStoreComplete Hook
 * ARGO 프로젝트 전용 App Store
 * 
 * 현재 App.tsx에서는 useGalaxy hook으로 상태를 관리하므로,
 * 최소한의 구조만 제공합니다.
 */
export const useAppStoreComplete = (): AppContextType => {
  // ARGO 프로젝트에 필요한 상태를 여기에 추가
  // 현재는 빈 객체 반환 (필요시 확장)
  return {} as AppContextType;
};
