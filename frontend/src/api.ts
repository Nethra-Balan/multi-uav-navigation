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

export const api = {
  health: () => request<{ status: string; service: string; engine_available: boolean }>("/api/health"),
  createMission: (config: MissionConfig) => request<MissionResponse>("/api/missions", { method: "POST", body: JSON.stringify(config) }),
  environment: (id: string) => request<EnvironmentData>(`/api/missions/${id}/environment`),
  status: (id: string) => request<Telemetry & { mission_id: string; status: string }>(`/api/missions/${id}/optimization/status`),
  result: (id: string) => request<FinalResult>(`/api/missions/${id}/results`),
  control: (id: string, action: "start" | "pause" | "resume" | "stop") =>
    request<{ status: string; message: string }>(`/api/missions/${id}/optimization/${action}`, { method: "POST" }),
};

export function optimizationSocket(id: string): WebSocket {
  return new WebSocket(`${wsUrl}/ws/missions/${id}/optimization`);
}
