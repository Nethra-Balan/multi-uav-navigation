import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, optimizationSocket } from "./api";
import type { EnvironmentData, FinalResult, Lifecycle, MissionConfig, MissionResponse, SocketMessage, Telemetry } from "./types";

const defaults: MissionConfig = {
  environment_dimensions: [200, 200, 100], seed: 42, uav_count: 6, target_count: 30, obstacle_count: 8,
  population_size: 10, generations: 30, elite_count: 2, crossover_probability: 0.85,
  fixed_mutation_probability: 0.15, adaptive_mutation_minimum: 0.05, adaptive_mutation_maximum: 0.3,
  collision_penalty: 5000, balance_weight: 10, algorithm: "adaptive",
};
type HistoryPoint = Telemetry & { generation: number };
interface Store {
  config: MissionConfig; setConfig: (config: MissionConfig) => void;
  mission: MissionResponse | null; environment: EnvironmentData | null; result: FinalResult | null;
  telemetry: Telemetry; history: HistoryPoint[]; lifecycle: Lifecycle; socketStatus: string; backendStatus: "checking" | "online" | "offline"; error: string | null;
  createMission: () => Promise<void>; control: (action: "start" | "pause" | "resume" | "stop") => Promise<void>;
  refreshStatus: () => Promise<void>; clearError: () => void;
}
const Context = createContext<Store | null>(null);
export function StoreProvider({ children }: { children: React.ReactNode }) {
  const [config, setConfig] = useState(defaults);
  const [mission, setMission] = useState<MissionResponse | null>(null);
  const [environment, setEnvironment] = useState<EnvironmentData | null>(null);
  const [result, setResult] = useState<FinalResult | null>(null);
  const [telemetry, setTelemetry] = useState<Telemetry>({ total_generations: 0 });
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [lifecycle, setLifecycle] = useState<Lifecycle>("idle");
  const [socketStatus, setSocketStatus] = useState("offline");
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let disposed = false;
    api.health()
      .then((health) => {
        if (!disposed) setBackendStatus(health.engine_available ? "online" : "offline");
      })
      .catch(() => {
        if (!disposed) setBackendStatus("offline");
      });
    return () => { disposed = true; };
  }, []);

  const createMission = useCallback(async () => {
    setError(null);
    try {
      const created = await api.createMission(config);
      setMission(created); setEnvironment(created.environment); setLifecycle("idle"); setTelemetry({ total_generations: config.generations });
      setHistory([]); setResult(null);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to create mission"); throw err; }
  }, [config]);

  const refreshStatus = useCallback(async () => {
    if (!mission) return;
    try {
      const status = await api.status(mission.mission_id);
      setTelemetry(status); setLifecycle(status.status as Lifecycle);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to read mission status"); }
  }, [mission]);

  const control = useCallback(async (action: "start" | "pause" | "resume" | "stop") => {
    if (!mission) return;
    setError(null);
    try { const response = await api.control(mission.mission_id, action); setLifecycle(response.status as Lifecycle); }
    catch (err) { setError(err instanceof Error ? err.message : `Unable to ${action} optimization`); throw err; }
  }, [mission]);

  useEffect(() => {
    if (!mission) return;
    let socket: WebSocket | null = null;
    let retry: number | undefined;
    let disposed = false;
    const connect = () => {
      if (disposed) return;
      socket = optimizationSocket(mission.mission_id); setSocketStatus("connecting");
      socket.onopen = () => setSocketStatus("connected");
      socket.onmessage = (event) => {
        let message: SocketMessage;
        try {
          message = JSON.parse(event.data) as SocketMessage;
        } catch (err) {
          console.error("Invalid optimization WebSocket message", err);
          setError("Received an invalid update from the optimization stream.");
          return;
        }
        const payload = message.payload || {};
        if (message.type === "generation_update") {
          const point = payload as unknown as HistoryPoint;
          setTelemetry((current) => ({ ...current, ...point }));
          setHistory((current) => point.generation ? [...current.filter((item) => item.generation !== point.generation), point].sort((a, b) => a.generation - b.generation) : current);
          setLifecycle((current) => (
            ["paused", "stopping", "stopped", "completed", "error"].includes(current)
              ? current
              : "running"
          ));
        } else if (message.type === "optimization_completed") {
          setLifecycle("completed");
          api.result(mission.mission_id)
            .then(setResult)
            .catch((err) => {
              console.error("Unable to load final optimization result", err);
              setError(err instanceof Error ? err.message : "Final optimization result is unavailable.");
            });
        } else if (message.type === "optimization_paused") setLifecycle("paused");
        else if (message.type === "optimization_resumed") setLifecycle("running");
        else if (message.type === "optimization_running") {
          setLifecycle((current) => current === "paused" || current === "stopping" || current === "stopped" || current === "completed" ? current : "running");
        } else if (message.type === "optimization_stopped") {
          setLifecycle((current) => current === "completed" ? current : "stopped");
        } else if (message.type === "optimization_error") { setLifecycle("error"); setError(String(payload.message || "Optimization error")); }
      };
      socket.onclose = () => { setSocketStatus("offline"); if (!disposed) retry = window.setTimeout(connect, 2000); };
      socket.onerror = () => setSocketStatus("error");
    };
    connect();
    return () => { disposed = true; if (retry) window.clearTimeout(retry); socket?.close(); setSocketStatus("offline"); };
  }, [mission]);

  const clearError = useCallback(() => setError(null), []);
  const value = useMemo(() => ({ config, setConfig, mission, environment, result, telemetry, history, lifecycle, socketStatus, backendStatus, error, createMission, control, refreshStatus, clearError }), [config, mission, environment, result, telemetry, history, lifecycle, socketStatus, backendStatus, error, createMission, control, refreshStatus, clearError]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useStore() { const value = useContext(Context); if (!value) throw new Error("useStore must be inside StoreProvider"); return value; }
