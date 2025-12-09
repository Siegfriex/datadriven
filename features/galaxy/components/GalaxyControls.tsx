import React, { useRef, useEffect } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import CameraControls from 'camera-controls';
import * as THREE from 'three';

// CameraControls를 Three.js에 등록
CameraControls.install({ THREE });

/**
 * GalaxyControls 컴포넌트
 * CameraControls를 사용한 부드러운 카메라 제어 (Google Earth 스타일)
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
    
    // 1.1 구글 어스 스타일 설정 적용
    // dollyToCursor: 마우스 커서 위치로 줌인
    controls.dollyToCursor = true;
    
    // smoothTime: 부드러운 감속 (관성 효과)
    controls.smoothTime = 0.8; // 0.25 -> 0.8로 증가하여 묵직한 느낌 부여
    
    // 속도 조절
    controls.dollySpeed = 0.5;
    controls.truckSpeed = 2.0;
    controls.rotateSpeed = 1.0;
    
    // 거리 제한
    controls.minDistance = 2;
    controls.maxDistance = 200;
    
    // 1.2 마우스 입력 매핑 (Google Earth / 일반 3D 툴 표준)
    // Left Click + Drag: ROTATE
    controls.mouseButtons.left = CameraControls.ACTION.ROTATE;
    // Right Click + Drag: TRUCK (Pan)
    controls.mouseButtons.right = CameraControls.ACTION.TRUCK;
    // Wheel Click + Drag: DOLLY
    controls.mouseButtons.middle = CameraControls.ACTION.DOLLY;
    // Wheel: DOLLY
    controls.mouseButtons.wheel = CameraControls.ACTION.DOLLY;
    
    // 터치 입력 매핑
    controls.touches.one = CameraControls.ACTION.TOUCH_ROTATE;
    controls.touches.two = CameraControls.ACTION.TOUCH_DOLLY_TRUCK;
    controls.touches.three = CameraControls.ACTION.TOUCH_OFF;
    
    // 초기 뷰 설정
    controls.setLookAt(15, 15, 15, 0, 0, 0, false);
    
    // 키보드 단축키
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!controlsRef.current) return;
      
      switch (event.key.toLowerCase()) {
        case 'r':
          // 리셋: 초기 위치로 복귀
          controls.setLookAt(15, 15, 15, 0, 0, 0, true);
          break;
        case 'f':
          // 포커스: 전체 뷰 (Fit to box)
          controls.fitToBox(
            new THREE.Box3(
              new THREE.Vector3(-30, -30, -30),
              new THREE.Vector3(30, 30, 30)
            ),
            true,
            { paddingLeft: 2, paddingRight: 2, paddingBottom: 2, paddingTop: 2 }
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
  
  // 선택된 작가로 카메라 이동 (2. 카메라 전환 로직 개선)
  useEffect(() => {
    if (!controlsRef.current || !selectedArtistPosition) return;
    
    // 이미 같은 위치면 무시
    if (lastSelectedRef.current && 
        lastSelectedRef.current.x === selectedArtistPosition.x && 
        lastSelectedRef.current.y === selectedArtistPosition.y && 
        lastSelectedRef.current.z === selectedArtistPosition.z) {
      return;
    }
    
    zoomToArtist(controlsRef.current, selectedArtistPosition, selectedArtistPosition.radius);
    
    lastSelectedRef.current = { 
      x: selectedArtistPosition.x, 
      y: selectedArtistPosition.y, 
      z: selectedArtistPosition.z 
    };
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
 * 특정 작가로 카메라 줌인 함수 (고도화)
 * 2.1 zoomToArtist 함수 고도화
 * - 현재 뷰 각도 유지하며 접근 또는 최적 쿼터뷰 각도로 전환
 * - 적절한 거리(Padding) 자동 계산
 * - 부드러운 이동 곡선 적용 (camera-controls 내장 easing 활용)
 */
export const zoomToArtist = (
  controls: CameraControls | null,
  position: { x: number; y: number; z: number },
  radius: number
) => {
  if (!controls) return;
  
  const target = new THREE.Vector3(position.x, position.y, position.z);
  
  // Padding 적용: 타겟이 화면에 너무 꽉 차지 않도록 (Radius * 3.5)
  // 최소 거리 5, 최대 거리 30으로 제한하여 너무 가깝거나 멀지 않게 함
  const distance = Math.min(Math.max(radius * 3.5, 5), 30);
  
  // 현재 카메라 위치와 타겟 사이의 거리 계산
  const currentPos = new THREE.Vector3();
  controls.getPosition(currentPos);
  const currentDistance = currentPos.distanceTo(target);
  
  // 현재 뷰 각도를 유지하면서 타겟으로 접근하기 위한 방향 계산
  const direction = currentPos.clone().sub(target);
  const directionLength = direction.length();
  
  let cameraPosition: THREE.Vector3;
  
  // 카메라가 타겟과 충분히 멀리 떨어져 있고, 방향이 유효한 경우
  // 현재 뷰 각도를 유지하면서 접근
  if (directionLength > 0.1 && currentDistance > distance * 0.5) {
    // 현재 방향을 유지하면서 거리만 조정
    direction.normalize();
    cameraPosition = target.clone().add(direction.multiplyScalar(distance));
  } else {
    // 카메라가 타겟과 너무 가깝거나 방향이 유효하지 않은 경우
    // 가장 보기 좋은 쿼터뷰 각도로 전환 (위에서 대각선으로 내려다보는 각도)
    // 여러 각도 중 가장 자연스러운 각도 선택
    const angles = [
      new THREE.Vector3(1, 1, 1).normalize(),      // 기본 쿼터뷰
      new THREE.Vector3(1, 0.8, 1).normalize(),   // 약간 위에서
      new THREE.Vector3(0.8, 1, 1).normalize(),   // 약간 옆에서
    ];
    
    // 현재 카메라 방향과 가장 유사한 각도 선택
    let bestAngle = angles[0];
    let maxDot = -Infinity;
    
    const currentDir = directionLength > 0.1 
      ? direction.normalize() 
      : new THREE.Vector3(1, 1, 1).normalize();
    
    for (const angle of angles) {
      const dot = currentDir.dot(angle);
      if (dot > maxDot) {
        maxDot = dot;
        bestAngle = angle;
      }
    }
    
    cameraPosition = target.clone().add(bestAngle.multiplyScalar(distance));
  }
  
  // 부드러운 전환 (Transition)
  // camera-controls의 내장 easing 함수를 활용 (smoothTime 설정에 따라 자동 적용)
  controls.setLookAt(
    cameraPosition.x,
    cameraPosition.y,
    cameraPosition.z,
    target.x,
    target.y,
    target.z,
    true // smooth transition (smoothTime=0.8 설정에 따라 부드러운 easing 적용)
  );
};
