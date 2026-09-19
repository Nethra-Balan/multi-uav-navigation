import type { FinalResult } from "../types";
import { toSceneVector } from "../scene/coordinateAdapter";

export interface PlaybackSnapshot {
  positions: Record<number, [number, number, number]>;
  visitedTargets: number[];
  progress: number;
  elapsed: number;
}

const displaySpeedMetersPerSecond = 40;

function routeDistances(route: FinalResult["uav_paths"][number]) {
  const distances = [0];
  for (let index = 1; index < route.points.length; index += 1) {
    const previous = toSceneVector(route.points[index - 1].position);
    const current = toSceneVector(route.points[index].position);
    distances.push(distances[index - 1] + previous.distanceTo(current));
  }
  return distances;
}

export function playbackDuration(result: FinalResult): number {
  const routeDurations = result.uav_paths.map((route) => {
    const distances = routeDistances(route);
    return (distances.at(-1) ?? 0) / displaySpeedMetersPerSecond;
  });
  return Math.max(...routeDurations, 0);
}

export function samplePlayback(result: FinalResult, elapsed: number): PlaybackSnapshot {
  const duration = playbackDuration(result);
  const safeElapsed = Number.isFinite(elapsed) ? Math.max(0, elapsed) : 0;
  const progress = duration === 0 ? 1 : Math.min(1, Math.max(0, safeElapsed / duration));
  const positions: Record<number, [number, number, number]> = {};
  const visited = new Set<number>();

  result.uav_paths.forEach((route) => {
    if (route.points.length === 0) return;
    const distances = routeDistances(route);
    const routeDistance = distances.at(-1) ?? 0;
    const elapsedDistance = progress * routeDistance;
    if (route.points.length === 1) {
      const position = toSceneVector(route.points[0].position);
      positions[route.uav] = [position.x, position.y, position.z];
      return;
    }
    const segmentIndex = Math.min(
      Math.max(distances.findIndex((distance) => distance >= elapsedDistance), 1) - 1,
      route.points.length - 2,
    );
    const segmentDistance = distances[segmentIndex + 1] - distances[segmentIndex];
    const localProgress = segmentDistance === 0
      ? 1
      : (elapsedDistance - distances[segmentIndex]) / segmentDistance;
    const from = toSceneVector(route.points[segmentIndex].position);
    const to = toSceneVector(route.points[Math.min(segmentIndex + 1, route.points.length - 1)].position);
    const position = from.lerp(to, localProgress);
    positions[route.uav] = [position.x, position.y, position.z];

    route.points.forEach((point, index) => {
      if (point.kind === "target" && distances[index] <= elapsedDistance) visited.add(point.target!);
    });
  });

  return { positions, visitedTargets: [...visited], progress, elapsed: Math.min(safeElapsed, duration) };
}
