/**
 * 색상 매핑 유틸리티
 * 점수를 RGB 색상으로 변환하는 로직
 */

import { Artist } from '../../../types/argo';
import * as THREE from 'three';

/**
 * 점수를 RGB 색상으로 변환
 * PRD 3.3.1: R=제도, G=학술, B=담론
 * @param inst_score 제도 점수 (0-100)
 * @param acad_score 학술 점수 (0-100)
 * @param media_score 담론 점수 (0-100)
 * @returns RGB 색상 (0-255)
 */
export function scoreToRGB(
  inst_score: number,
  acad_score: number,
  media_score: number
): { r: number; g: number; b: number } {
  return {
    r: Math.round((inst_score / 100) * 255),
    g: Math.round((acad_score / 100) * 255),
    b: Math.round((media_score / 100) * 255)
  };
}

/**
 * 점수를 Three.js Color로 변환
 * @param inst_score 제도 점수 (0-100)
 * @param acad_score 학술 점수 (0-100)
 * @param media_score 담론 점수 (0-100)
 * @returns THREE.Color
 */
export function scoreToThreeColor(
  inst_score: number,
  acad_score: number,
  media_score: number
): THREE.Color {
  const rgb = scoreToRGB(inst_score, acad_score, media_score);
  return new THREE.Color(rgb.r / 255, rgb.g / 255, rgb.b / 255);
}

/**
 * 복합 점수를 발광 강도로 변환
 * @param composite_score 복합 점수 (0-100)
 * @returns 발광 강도 (0-1)
 */
export function scoreToEmissive(composite_score: number): number {
  return composite_score / 100;
}

/**
 * 작가의 색상 배열 생성 (InstancedMesh용)
 * @param artists 작가 배열
 * @returns Float32Array (r, g, b, emissive) * count
 */
export function createColorArray(artists: Artist[]): Float32Array {
  const colors = new Float32Array(artists.length * 4); // r, g, b, emissive
  
  artists.forEach((artist, index) => {
    const rgb = scoreToRGB(
      artist.scores.inst_score,
      artist.scores.acad_score,
      artist.scores.media_score
    );
    const emissive = scoreToEmissive(artist.scores.composite_score);
    
    const baseIndex = index * 4;
    colors[baseIndex] = rgb.r / 255;
    colors[baseIndex + 1] = rgb.g / 255;
    colors[baseIndex + 2] = rgb.b / 255;
    colors[baseIndex + 3] = emissive;
  });
  
  return colors;
}

