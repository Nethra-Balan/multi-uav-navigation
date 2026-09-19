import * as THREE from "three";

export type BackendPoint = number[];

export function toSceneVector(point: BackendPoint): THREE.Vector3 {
  return new THREE.Vector3(point[0] ?? 0, point[2] ?? 0, point[1] ?? 0);
}

export function toSceneTuple(point: BackendPoint): [number, number, number] {
  return [point[0] ?? 0, point[2] ?? 0, point[1] ?? 0];
}

export function sceneDimensions(dimensions: { width: number; depth: number; height: number }) {
  return { x: dimensions.width, y: dimensions.height, z: dimensions.depth };
}
