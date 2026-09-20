import * as THREE from "three";

export type BackendPoint = number[];
export type EnvironmentDimensions = { width: number; depth: number; height: number };
export type SceneDimensions = { x: number; y: number; z: number };

export function toSceneVector(point: BackendPoint): THREE.Vector3 {
  return new THREE.Vector3(point[0] ?? 0, point[2] ?? 0, point[1] ?? 0);
}

export function toSceneTuple(point: BackendPoint): [number, number, number] {
  return [point[0] ?? 0, point[2] ?? 0, point[1] ?? 0];
}

export function sceneDimensions(dimensions: EnvironmentDimensions): SceneDimensions {
  return { x: dimensions.width, y: dimensions.height, z: dimensions.depth };
}

export function sceneCenter(dimensions: EnvironmentDimensions): THREE.Vector3 {
  const size = sceneDimensions(dimensions);
  return new THREE.Vector3(size.x / 2, size.y / 2, size.z / 2);
}
