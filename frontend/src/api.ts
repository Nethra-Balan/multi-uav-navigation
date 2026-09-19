import type { EnvironmentData, FinalResult, MissionConfig, MissionResponse, SocketMessage, Telemetry } from "./types";

const baseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const wsUrl = baseUrl.replace(/^http/, "ws");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try { const body = await response.json(); detail = body.detail || detail; } catch { /* retain status */ }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

function normalizeEnvironment(value: EnvironmentData): EnvironmentData {
  return {
    ...value,
    uavs: value.uavs ?? value.uav_positions.map((start_position, index) => ({ id: index + 1, start_position })),
    targets: value.targets ?? value.target_positions.map((position, index) => ({ id: index + 1, position })),
  };
}

function normalizeResult(value: FinalResult): FinalResult {
  if (value.uav_paths) return value;
  return {
    ...value,
    uav_paths: value.paths.map((path, index) => {
      const targets = value.allocation[index]?.targets ?? [];
      const points: FinalResult["uav_paths"][number]["points"] = [{ kind: "start", position: path[0] }];
      let pathIndex = 1;
      targets.forEach((target) => {
        while (pathIndex < path.length - 1 && (value.waypoints[index] ?? []).some((waypoint) => waypoint.every((coordinate, coordinateIndex) => coordinate === path[pathIndex][coordinateIndex]))) {
          points.push({ kind: "waypoint" as const, position: path[pathIndex] });
          pathIndex += 1;
        }
        points.push({ kind: "target" as const, target, position: path[pathIndex] });
        pathIndex += 1;
      });
      return { uav: index + 1, points, distance: value.allocation[index]?.path_distance ?? 0 };
    }),
  };
}

export const api = {
  health: () => request<{ status: string; service: string; engine_available: boolean }>("/api/health"),
  createMission: async (config: MissionConfig) => {
    const response = await request<MissionResponse>("/api/missions", { method: "POST", body: JSON.stringify(config) });
    return { ...response, environment: normalizeEnvironment(response.environment) };
  },
  environment: async (id: string) => normalizeEnvironment(await request<EnvironmentData>(`/api/missions/${id}/environment`)),
  status: (id: string) => request<Telemetry & { mission_id: string; status: string }>(`/api/missions/${id}/optimization/status`),
  result: async (id: string) => normalizeResult(await request<FinalResult>(`/api/missions/${id}/results`)),
  control: (id: string, action: "start" | "pause" | "resume" | "stop") =>
    request<{ status: string; message: string }>(`/api/missions/${id}/optimization/${action}`, { method: "POST" }),
};

export function optimizationSocket(id: string): WebSocket {
  return new WebSocket(`${wsUrl}/ws/missions/${id}/optimization`);
}
