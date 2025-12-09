/**
 * ARGO 3D 갤러리 데이터 타입 정의
 * TSD 2.1.1 기반 Artist 인터페이스 및 관련 타입
 */

// 점수 구조
export interface Scores {
  inst_score: number; // 제도 레이어 (0-100)
  acad_score: number; // 학술 레이어 (0-100)
  media_score: number; // 담론 레이어 (0-100)
  network_score: number; // 네트워크 레이어 (0-100)
  composite_score: number; // 복합 점수 (0-100)
}

// 구조주의 분석
export interface StructuralistAnalysis {
  dominant_capital: 'institutional' | 'academic' | 'media' | 'network';
  capital_composition: {
    institutional_ratio: number;
    academic_ratio: number;
    media_ratio: number;
    network_ratio: number;
  };
  structural_position: {
    field_quadrant: 'Q1_established' | 'Q2_academic_elite' | 'Q3_media_star' | 'Q4_emerging';
    position_stability: number;
    mobility_potential: number;
  };
  algorithm_version: string;
  weights_applied: {
    inst: number;
    acad: number;
    media: number;
    network: number;
  };
  theoretical_basis: string;
}

// 3D 좌표 (Pre-calculated)
export interface Coordinates3D {
  x: number; // inst_score 정규화 (-30 ~ 30)
  y: number; // acad_score 정규화 (-30 ~ 30)
  z: number; // media_score 정규화 (-30 ~ 30)
  radius: number; // network_score 기반 (10 + score/5)
  computed_at?: string;
  algorithm?: string;
}

// Artist 엔터티 (TSD 2.1.1 기반)
export interface Artist {
  artist_id: string;
  name: string;
  alternativeName?: string;
  birth_year?: number;
  url?: string;
  segment_id?: string;
  career_stage?: 'early' | 'mid' | 'late';
  scores: Scores;
  structuralist_analysis?: StructuralistAnalysis;
  coordinates_3d: Coordinates3D;
  instanceId?: number; // InstancedMesh 인덱스 매핑용
  collaborators?: string[]; // 협력 작가 ID 목록
  // 관계 데이터 (Task 1.2: 연결선 시각화)
  collaborations?: Collaboration[]; // 협력 관계 배열
  institutions?: Institution[]; // 소속 기관 배열
  exhibitions?: Exhibition[]; // 전시 참여 배열
}

// Cluster 엔터티 (PRD 3.3.2 기반)
export interface Cluster {
  cluster_id: string;
  name: string;
  segment_ids: string[]; // 포함된 세그먼트 목록
  artist_ids: string[]; // 포함된 작가 목록
  center: {
    x: number;
    y: number;
    z: number;
  };
  radius: number; // 군집 반경
  opacity: number; // 투명도 (0-1)
  color?: string; // 군집 색상
}

// GalaxySnapshot (시각화 스냅샷)
export interface GalaxySnapshot {
  snapshot_id: string;
  timestamp: string;
  artists: Artist[];
  clusters?: Cluster[];
  coordinate_scale_factor?: number; // 시각화 보정 상수
  filters?: {
    segment_ids?: string[];
    career_stages?: ('early' | 'mid' | 'late')[];
    score_ranges?: {
      inst?: [number, number];
      acad?: [number, number];
      media?: [number, number];
      network?: [number, number];
    };
  };
}

// 선택된 작가 정보 (상호작용용)
export interface SelectedArtist {
  artist: Artist;
  instanceId: number;
  hovered: boolean;
}

// 관계 데이터 타입 정의 (Task 1.2: 연결선 시각화)
export interface Collaboration {
  artist_id: string;
  strength: number; // 0-1 범위
}

export interface Institution {
  institution_id: string;
  name: string;
  type?: string;
}

export interface Exhibition {
  exhibition_id: string;
  name: string;
  year?: number;
}

// 필터 상태 타입 정의 (Task 1.1: 필터 동적 업데이트)
export interface FilterState {
  segment_ids?: string[];
  career_stages?: ('early' | 'mid' | 'late')[];
  score_ranges?: {
    inst?: [number, number];
    acad?: [number, number];
    media?: [number, number];
    network?: [number, number];
  };
  region?: string[];
  institution_ids?: string[];
}