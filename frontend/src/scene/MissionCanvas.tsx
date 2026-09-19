import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { GizmoHelper, GizmoViewport, Line, OrbitControls, Text } from "@react-three/drei";
import { memo, useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import type { EnvironmentData, FinalResult } from "../types";
import { sceneDimensions, toSceneVector } from "./coordinateAdapter";

type Visibility = { targets: boolean; obstacles: boolean; uavs: boolean; paths: boolean; waypoints: boolean; collisions: boolean; grid: boolean; axes: boolean };
type Props = {
  environment: EnvironmentData;
  result: FinalResult | null;
  visibility: Visibility;
  selectedUav: number | null;
  selectedTarget: number | null;
  selectedCollision: number | null;
  playbackPositions: Record<number, [number, number, number]>;
  visitedTargets: number[];
  onSelectUav: (id: number) => void;
  onSelectTarget: (id: number) => void;
  onSelectCollision: (index: number) => void;
  cameraPreset: "perspective" | "top" | "side";
  resetToken: number;
  playbackActive: boolean;
};

const routeColors = ["#54d6ff", "#86efac", "#fbbf24", "#c4b5fd", "#fb7185", "#67e8f9", "#fdba74", "#a7f3d0"];

function CameraController({ preset, resetToken }: { preset: Props["cameraPreset"]; resetToken: number }) {
  const { camera } = useThree();
  const controls = useRef<any>(null);
  useEffect(() => {
    const positions = { perspective: [260, 190, 280], top: [0, 330, 0.01], side: [330, 80, 0.01] } as const;
    const position = positions[preset];
    camera.position.set(position[0], position[1], position[2]);
    camera.lookAt(0, 0, 0);
    controls.current?.target.set(0, 0, 0);
    controls.current?.update();
  }, [camera, preset, resetToken]);
  return <OrbitControls ref={controls} makeDefault enableDamping dampingFactor={0.08} minDistance={30} maxDistance={700} />;
}

const Boundary = memo(function Boundary({ dimensions }: { dimensions: EnvironmentData["dimensions"] }) {
  const size = sceneDimensions(dimensions);
  const geometry = useMemo(() => new THREE.BoxGeometry(size.x, size.y, size.z), [size.x, size.y, size.z]);
  useEffect(() => () => geometry.dispose(), [geometry]);
  return <lineSegments geometry={geometry}>
    <lineBasicMaterial color="#4d91a2" transparent opacity={0.9} />
  </lineSegments>;
});

function GridAndAxes({ dimensions, visibility }: { dimensions: EnvironmentData["dimensions"]; visibility: Visibility }) {
  const size = sceneDimensions(dimensions);
  return <group>
    {visibility.grid && <gridHelper args={[Math.max(size.x, size.z), 20, "#3e8192", "#1b3e4d"]} rotation={[0, 0, 0]} />}
    {visibility.axes && <GizmoHelper alignment="bottom-right" margin={[70, 70]}><GizmoViewport axisColors={["#ef4444", "#22c55e", "#3b82f6"]} labelColor="white" /></GizmoHelper>}
    <Boundary dimensions={dimensions} />
    <Text position={[size.x / 2 + 8, 0, 0]} rotation={[0, Math.PI / 2, 0]} fontSize={5} color="#5c7890">X</Text>
    <Text position={[0, size.y / 2 + 8, 0]} fontSize={5} color="#5c7890">Z</Text>
    <Text position={[0, 0, size.z / 2 + 8]} rotation={[0, Math.PI, 0]} fontSize={5} color="#5c7890">Y</Text>
  </group>;
}

const Obstacles = memo(function Obstacles({ environment, visible }: { environment: EnvironmentData; visible: boolean }) {
  return <group visible={visible}>{environment.obstacles.map((obstacle) => {
    const min = toSceneVector(obstacle.min); const max = toSceneVector(obstacle.max);
    const center = min.clone().add(max).multiplyScalar(0.5); const size = max.clone().sub(min);
    return <mesh key={obstacle.id} position={center}><boxGeometry args={[size.x, size.y, size.z]} /><meshStandardMaterial color="#b77d2d" transparent opacity={0.42} roughness={0.6} metalness={0.25} emissive="#3b260d" emissiveIntensity={0.18} /></mesh>;
  })}</group>;
});

function Targets({ environment, result, visible, selected, visited, onSelect }: { environment: EnvironmentData; result: FinalResult | null; visible: boolean; selected: number | null; visited: number[]; onSelect: (id: number) => void }) {
  const assigned = useMemo(() => new Set(result?.allocation.flatMap((row) => row.targets) ?? []), [result]);
  return <group visible={visible}>{environment.targets.map((target) => {
    const position = toSceneVector(target.position); const isVisited = visited.includes(target.id);
    return <group key={target.id} position={position} onClick={(event) => { event.stopPropagation(); onSelect(target.id); }}>
      <mesh><sphereGeometry args={[selected === target.id ? 3.3 : 2.4, 16, 16]} /><meshStandardMaterial color={isVisited ? "#4ade80" : selected === target.id ? "#ffffff" : assigned.has(target.id) ? "#55d6ff" : "#7dd3fc"} emissive={isVisited ? "#14532d" : "#0e7490"} emissiveIntensity={selected === target.id ? 1.15 : 0.7} roughness={0.26} metalness={0.2} /></mesh>
      {selected === target.id && <mesh rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[4.8, 0.32, 8, 24]} /><meshBasicMaterial color="#dffeff" transparent opacity={0.82} /></mesh>}
      <Text position={[0, 5, 0]} fontSize={2.6} color={isVisited ? "#86efac" : "#bdefff"}>{`T${target.id}`}</Text>
    </group>;
  })}</group>;
}

function Rotor({ rotation, active }: { rotation: [number, number, number]; active: boolean }) {
  const ref = useRef<THREE.Group>(null);
  useFrame((_, delta) => { if (active && ref.current) ref.current.rotation.y += delta * 18; });
  return <group ref={ref} rotation={rotation}><mesh><boxGeometry args={[5.5, 0.12, 0.22]} /><meshBasicMaterial color="#d9fbff" transparent opacity={0.72} /></mesh><mesh rotation={[0, Math.PI / 2, 0]}><boxGeometry args={[5.5, 0.12, 0.22]} /><meshBasicMaterial color="#d9fbff" transparent opacity={0.42} /></mesh></group>;
}

function UAVModel({ color, selected, active }: { color: string; selected: boolean; active: boolean }) {
  const motors: [number, number][] = [[-5, -5], [5, -5], [-5, 5], [5, 5]];
  return <group>
    <mesh><boxGeometry args={[4.8, 1.5, 4.8]} /><meshStandardMaterial color={selected ? "#ffffff" : "#172c38"} emissive={color} emissiveIntensity={selected ? 0.8 : 0.18} metalness={0.65} roughness={0.24} /></mesh>
    <mesh position={[0, 0.7, 0]}><coneGeometry args={[2.3, 1.8, 6]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={selected ? 0.9 : 0.35} metalness={0.5} roughness={0.25} /></mesh>
    {motors.map(([x, z], index) => <group key={index} position={[x / 2, 0, z / 2]}><mesh rotation={[0, 0, index % 2 ? -0.12 : 0.12]}><boxGeometry args={[9, 0.42, 0.55]} /><meshStandardMaterial color={color} metalness={0.55} roughness={0.3} /></mesh><mesh position={[0, 0.55, 0]}><cylinderGeometry args={[1.15, 1.15, 0.75, 12]} /><meshStandardMaterial color="#0b151c" emissive={color} emissiveIntensity={active ? 0.6 : 0.18} metalness={0.7} roughness={0.2} /></mesh><Rotor rotation={[0, index % 2 ? 0.4 : 0, 0]} active={active} /></group>)}
    <mesh position={[0, -1, 0]}><boxGeometry args={[2.2, 0.18, 2.2]} /><meshStandardMaterial color="#253f4a" metalness={0.5} roughness={0.4} /></mesh>
  </group>;
}

function Uavs({ environment, result, visible, selected, positions, onSelect, playbackActive }: { environment: EnvironmentData; result: FinalResult | null; visible: boolean; selected: number | null; positions: Record<number, [number, number, number]>; onSelect: (id: number) => void; playbackActive: boolean }) {
  return <group visible={visible}>{environment.uavs.map((uav) => {
    const position = positions[uav.id] ?? toSceneVector(uav.start_position).toArray() as [number, number, number];
    const color = routeColors[(uav.id - 1) % routeColors.length];
    return <group key={uav.id} position={position} scale={selected === uav.id ? 1.25 : 1} onClick={(event) => { event.stopPropagation(); onSelect(uav.id); }}>
      <UAVModel color={color} selected={selected === uav.id} active={playbackActive} />
      {selected === uav.id && <mesh rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[7, 0.38, 8, 28]} /><meshBasicMaterial color={color} transparent opacity={0.75} /></mesh>}
      <Text position={[0, 7, 0]} fontSize={3} color="#e5f7ff">{`UAV ${uav.id}`}</Text>
    </group>;
  })}</group>;
}

function Paths({ result, visible, selected, selectedTarget, onSelectTarget }: { result: FinalResult | null; visible: boolean; selected: number | null; selectedTarget: number | null; onSelectTarget: (id: number) => void }) {
  return <group visible={visible}>{result?.uav_paths.map((route) => {
    const points = route.points.map((point) => toSceneVector(point.position).toArray() as [number, number, number]);
    const color = routeColors[(route.uav - 1) % routeColors.length]; const dim = selected !== null && selected !== route.uav;
    return <group key={route.uav}><Line points={points} color={color} transparent opacity={dim ? 0.12 : 0.85} lineWidth={selected === route.uav ? 3 : 1.4} />
      {route.points.filter((point) => point.kind === "target").map((point) => <mesh key={point.target} position={toSceneVector(point.position)} onClick={(event) => { event.stopPropagation(); onSelectTarget(point.target!); }} visible={selectedTarget === null || selectedTarget === point.target}><sphereGeometry args={[1.2, 10, 10]} /><meshBasicMaterial color={color} /></mesh>)}
    </group>;
  })}</group>;
}

function Waypoints({ result, visible, selected }: { result: FinalResult | null; visible: boolean; selected: number | null }) {
  return <group visible={visible}>{result?.waypoints.map((points, uavIndex) => points.map((point, index) =>   <mesh key={`${uavIndex}-${index}`} position={toSceneVector(point)}><octahedronGeometry args={[2.1, 0]} /><meshStandardMaterial color={selected === null || selected === uavIndex + 1 ? "#ffc857" : "#53616a"} emissive="#b86b0b" emissiveIntensity={0.7} roughness={0.35} metalness={0.25} /></mesh>))}</group>;
}

const Collisions = memo(function Collisions({ environment, result, visible, selected, onSelect }: { environment: EnvironmentData; result: FinalResult | null; visible: boolean; selected: number | null; onSelect: (index: number) => void }) {
  return <group visible={visible}>{result?.collisions.map((collision, index) => {
    const start = toSceneVector(collision.start); const end = toSceneVector(collision.end); const center = start.clone().add(end).multiplyScalar(0.5);
    const obstacle = environment.obstacles.find((item) => item.id === collision.obstacle); const obstacleCenter = obstacle ? toSceneVector(obstacle.min).add(toSceneVector(obstacle.max)).multiplyScalar(0.5) : center;
    return <group key={index}><Line points={[start.toArray(), end.toArray()]} color={selected === index ? "#ffffff" : "#ef4444"} lineWidth={5} /><mesh position={obstacleCenter} onClick={(event) => { event.stopPropagation(); onSelect(index); }}><boxGeometry args={[6, 6, 6]} /><meshBasicMaterial color="#ef4444" transparent opacity={selected === index ? 0.65 : 0.28} /></mesh></group>;
  })}</group>;
});

function Scene({ props }: { props: Props }) {
  return <><ambientLight intensity={1.1} /><directionalLight position={[100, 200, 120]} intensity={2.2} /><pointLight position={[0, 120, 0]} color="#47d9eb" intensity={1.2} distance={500} /><CameraController preset={props.cameraPreset} resetToken={props.resetToken} /><GridAndAxes dimensions={props.environment.dimensions} visibility={props.visibility} /><Obstacles environment={props.environment} visible={props.visibility.obstacles} /><Targets environment={props.environment} result={props.result} visible={props.visibility.targets} selected={props.selectedTarget} visited={props.visitedTargets} onSelect={props.onSelectTarget} /><Paths result={props.result} visible={props.visibility.paths} selected={props.selectedUav} selectedTarget={props.selectedTarget} onSelectTarget={props.onSelectTarget} /><Waypoints result={props.result} visible={props.visibility.waypoints} selected={props.selectedUav} /><Collisions environment={props.environment} result={props.result} visible={props.visibility.collisions} selected={props.selectedCollision} onSelect={props.onSelectCollision} /><Uavs environment={props.environment} result={props.result} visible={props.visibility.uavs} selected={props.selectedUav} positions={props.playbackPositions} onSelect={props.onSelectUav} playbackActive={props.playbackActive} /></>;
}

export function MissionCanvas(props: Props) {
  return <Canvas camera={{ position: [260, 190, 280], fov: 45, near: 0.1, far: 1600 }} dpr={[1, 2]} onPointerMissed={() => props.onSelectUav(0)}><Scene props={props} /></Canvas>;
}
