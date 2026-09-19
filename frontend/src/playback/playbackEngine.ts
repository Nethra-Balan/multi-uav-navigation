import type { FinalResult } from "../types";
import { toSceneVector } from "../scene/coordinateAdapter";

export interface PlaybackSnapshot {
  positions: Record<number, [number, number, number]>;
  visitedTargets: number[];
  progress: number;
  elapsed: number;
}

const segmentDuration = 1.4;

export function playbackDuration(result: FinalResult): number {
  return Math.max(...result.uav_paths.map((route) => Math.max(route.points.length - 1, 1)), 1) * segmentDuration;
}

export function samplePlayback(result: FinalResult, elapsed: number): PlaybackSnapshot {
  const duration = playbackDuration(result);
  const progress = Math.min(1, Math.max(0, elapsed / duration));
  const positions: Record<number, [number, number, number]> = {};
  const visited = new Set<number>();

  result.uav_paths.forEach((route) => {
    const segmentCount = Math.max(route.points.length - 1, 1);
    const routeElapsed = Math.min(segmentCount, progress * segmentCount);
    const segmentIndex = Math.min(Math.floor(routeElapsed), segmentCount - 1);
    const localProgress = routeElapsed - segmentIndex;
    const from = toSceneVector(route.points[segmentIndex].position);
    const to = toSceneVector(route.points[Math.min(segmentIndex + 1, route.points.length - 1)].position);
    const position = from.lerp(to, localProgress);
    positions[route.uav] = [position.x, position.y, position.z];

    route.points.forEach((point, index) => {
      if (point.kind === "target" && index <= routeElapsed) visited.add(point.target!);
    });
  });

  return { positions, visitedTargets: [...visited], progress, elapsed: Math.min(elapsed, duration) };
}
