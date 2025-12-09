import React, { useRef, useEffect } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import CameraControls from 'camera-controls';
import * as THREE from 'three';

// CameraControls를 Three.js에 등록
CameraControls.install({ THREE });

/**
 * GalaxyControls 컴포넌트
 * CameraControls를 사용한 부드러운 카메라 제어
 */
interface GalaxyControlsProps {
  selectedArtistPosition?: { x: number; y: number; z: number; radius: number } | null;
}

export const GalaxyControls: React.FC<GalaxyControlsProps> = ({ selectedArtistPosition }) => {
  const { camera, gl } = useThree();
  const controlsRef = useRef<CameraControls | null>(null);
  const lastSelectedRef = useRef<{ x: number; y: number; z: number } | null>(null);
  
  useEffect(() => {
    if (!camera || !gl.domElement) return;
    
    // CameraControls 인스턴스 생성
    const controls = new CameraControls(camera, gl.domElement);
    controlsRef.current = controls;
    
    // 초기 설정
    controls.setLookAt(15, 15, 15, 0, 0, 0);
    controls.minDistance = 5;
    controls.maxDistance = 100;
    controls.dollySpeed = 0.5;
    controls.truckSpeed = 2;
    controls.smoothTime = 0.25; // 부드러운 전환
    
    // 키보드 단축키
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!controlsRef.current) return;
      
      switch (event.key.toLowerCase()) {
        case 'r':
          // 리셋: 초기 위치로 복귀
          controls.setLookAt(15, 15, 15, 0, 0, 0, true);
          break;
        case 'f':
          // 포커스: 선택된 작가로 줌인 (현재는 중심으로)
          controls.fitToBox(
            new THREE.Box3(
              new THREE.Vector3(-30, -30, -30),
              new THREE.Vector3(30, 30, 30)
            ),
            true
          );
          break;
        case 'h':
          // 홈: 기본 뷰로 복귀
          controls.setLookAt(15, 15, 15, 0, 0, 0, true);
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      controls.dispose();
    };
  }, [camera, gl]);
  
  // 선택된 작가로 카메라 이동
  useEffect(() => {
    if (!controlsRef.current || !selectedArtistPosition) return;
    
    const { x, y, z, radius } = selectedArtistPosition;
    const target = new THREE.Vector3(x, y, z);
    const distance = Math.max(radius * 4, 8); // 최소 거리 보장
    
    // 카메라 위치 계산 (타겟에서 약간 위쪽, 대각선 방향)
    const offset = new THREE.Vector3(1, 1, 1).normalize().multiplyScalar(distance);
    const cameraPosition = target.clone().add(offset);
    
    controlsRef.current.setLookAt(
      cameraPosition.x,
      cameraPosition.y,
      cameraPosition.z,
      target.x,
      target.y,
      target.z,
      true // smooth transition
    );
    
    lastSelectedRef.current = { x, y, z };
  }, [selectedArtistPosition]);
  
  // R3F의 useFrame으로 애니메이션 루프
  useFrame((_, delta) => {
    if (controlsRef.current) {
      controlsRef.current.update(delta);
    }
  });
  
  return null;
};

/**
 * 특정 작가로 카메라 줌인 함수
 * @param position 작가의 3D 위치
 * @param radius 작가의 반경
 */
export const zoomToArtist = (
  controls: CameraControls | null,
  position: { x: number; y: number; z: number },
  radius: number
) => {
  if (!controls) return;
  
  const target = new THREE.Vector3(position.x, position.y, position.z);
  const distance = radius * 3; // 작가로부터 3배 거리
  
  // 카메라 위치 계산
  const direction = new THREE.Vector3(15, 15, 15).normalize();
  const cameraPosition = target.clone().add(direction.multiplyScalar(distance));
  
  controls.setLookAt(
    cameraPosition.x,
    cameraPosition.y,
    cameraPosition.z,
    target.x,
    target.y,
    target.z,
    true // smooth transition
  );
};

