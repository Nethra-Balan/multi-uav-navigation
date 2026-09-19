export type Lifecycle = "idle" | "starting" | "running" | "paused" | "stopping" | "stopped" | "completed" | "error";
export type Algorithm = "fixed" | "adaptive";

export interface MissionConfig {
  environment_dimensions: [number, number, number];
  seed: number;
  uav_count: number;
  target_count: number;
  obstacle_count: number;
  population_size: number;
  generations: number;
  elite_count: number;
  crossover_probability: number;
  fixed_mutation_probability: number;
  adaptive_mutation_minimum: number;
  adaptive_mutation_maximum: number;
  collision_penalty: number;
  balance_weight: number;
  algorithm: Algorithm;
}
export interface EnvironmentData {
  dimensions: { width: number; depth: number; height: number };
  start_position: number[];
  uav_positions: number[][];
  uavs: { id: number; start_position: number[] }[];
  target_positions: number[][];
  targets: { id: number; position: number[] }[];
  obstacles: { id: number; min: number[]; max: number[] }[];
  seed: number;
  uav_count: number;
  target_count: number;
  obstacle_count: number;
}
export interface MissionResponse {
  mission_id: string;
  status: Lifecycle;
  configuration: MissionConfig & { algorithm: Algorithm };
  environment: EnvironmentData;
}
export interface Telemetry {
  generation?: number;
  total_generations: number;
  best_fitness?: number;
  mean_fitness?: number;
  mutation_probability?: number;
  total_path_distance?: number;
  collision_count?: number;
  balance_penalty?: number;
  route_distances?: number[];
  target_counts?: number[];
  best_routes?: number[][];
}
export interface FinalResult {
  best_chromosome: { routes: number[][] };
  paths: number[][][];
  uav_paths: {
    uav: number;
    points: { kind: "start" | "waypoint" | "target"; target?: number; position: number[] }[];
    distance: number;
  }[];
  waypoints: number[][][];
  allocation: { uav: number; targets: number[]; target_count: number; path_distance: number }[];
  collisions: { uav: number; segment_index: number; start: number[]; end: number[]; obstacle: number }[];
  metrics: { fitness: number; total_distance: number; collision_count: number; balance_penalty: number; route_distances: number[] };
  validation: { total_collisions: number; routes_with_collision: number; collision_free: boolean };
}
export interface SocketMessage { type: string; mission_id: string; payload: Record<string, unknown>; }
