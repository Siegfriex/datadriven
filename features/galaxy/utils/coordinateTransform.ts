/**
 * 좌표 변환 유틸리티
 * 점수를 3D 좌표로 변환하는 로직
 */

import { Artist, Coordinates3D } from '../../../types/argo';

/**
 * 점수를 3D 좌표로 변환
 * @param inst_score 제도 점수 (0-100)
 * @param acad_score 학술 점수 (0-100)
 * @param media_score 담론 점수 (0-100)
 * @param network_score 네트워크 점수 (0-100)
 * @param scale_factor 스케일 팩터 (기본값: 60, 범위 -30 ~ 30)
 * @returns 3D 좌표
 */
export function scoreToCoordinates(
  inst_score: number,
  acad_score: number,
  media_score: number,
  network_score: number,
  scale_factor: number = 60
): Coordinates3D {
  return {
    x: (inst_score / 100 * scale_factor) - scale_factor / 2, // -30 ~ 30
    y: (acad_score / 100 * scale_factor) - scale_factor / 2, // -30 ~ 30
    z: (media_score / 100 * scale_factor) - scale_factor / 2, // -30 ~ 30
    radius: 10 + network_score / 5 // network_score 기반 반경
  };
}

/**
 * 작가 배열에 instanceId 추가
 * @param artists 작가 배열
 * @returns instanceId가 추가된 작가 배열
 */
export function addInstanceIds(artists: Artist[]): Artist[] {
  return artists.map((artist, index) => ({
    ...artist,
    instanceId: index
  }));
}

/**
 * 좌표 범위 정규화
 * @param coordinates 좌표
 * @param min 최소값
 * @param max 최대값
 * @returns 정규화된 좌표
 */
export function normalizeCoordinates(
  coordinates: Coordinates3D,
  min: number = -30,
  max: number = 30
): Coordinates3D {
  return {
    ...coordinates,
    x: Math.max(min, Math.min(max, coordinates.x)),
    y: Math.max(min, Math.min(max, coordinates.y)),
    z: Math.max(min, Math.min(max, coordinates.z))
  };
}

