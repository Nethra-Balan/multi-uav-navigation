import { useEffect, useMemo, useState } from "react";
import { useStore } from "../store";
import type { FinalResult } from "../types";
import { MissionCanvas } from "../scene/MissionCanvas";
import { playbackDuration, samplePlayback } from "../playback/playbackEngine";

type Visibility = { targets: boolean; obstacles: boolean; uavs: boolean; paths: boolean; waypoints: boolean; collisions: boolean; grid: boolean; axes: boolean };
type Selection = { uav: number | null; target: number | null; collision: number | null };

const initialVisibility: Visibility = { targets: true, obstacles: true, uavs: true, paths: true, waypoints: true, collisions: true, grid: true, axes: true };
const fmt = (value: number | undefined, digits = 1) => value === undefined ? "—" : value.toFixed(digits);

function initialPlayback(result: FinalResult | null) {
  if (!result) return { positions: {}, visitedTargets: [] as number[], progress: 0, elapsed: 0 };
  return samplePlayback(result, 0);
}

export default function MissionPage() {
  const { mission, environment, result, lifecycle } = useStore();
  const [visibility, setVisibility] = useState(initialVisibility);
  const [selection, setSelection] = useState<Selection>({ uav: null, target: null, collision: null });
  const [preset, setPreset] = useState<"perspective" | "top" | "side">("perspective");
  const [resetToken, setResetToken] = useState(0);
  const [playbackStatus, setPlaybackStatus] = useState<"ready" | "playing" | "paused" | "completed">("ready");
  const [elapsed, setElapsed] = useState(0);
  const [speed, setSpeed] = useState(1);

  const duration = result ? playbackDuration(result) : 0;
  const playback = result ? samplePlayback(result, elapsed) : initialPlayback(null);

  useEffect(() => {
    if (playbackStatus !== "playing" || !result) return;
    let frame = 0;
    let last = performance.now();
    const tick = (now: number) => {
      const delta = (now - last) / 1000;
      last = now;
      setElapsed((current) => {
        const next = current + delta * speed;
        if (next >= duration) {
          setPlaybackStatus("completed");
          return duration;
        }
        return next;
      });
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [duration, playbackStatus, result, speed]);

  useEffect(() => {
    if (result) {
      setElapsed(0);
      setPlaybackStatus("ready");
    }
  }, [result]);

  if (!mission || !environment) return <div className="empty"><div className="empty-mark">+</div><h3>Mission viewport offline</h3><p>Create a mission first. The 3D simulator will connect to the generated backend environment.</p></div>;

  const toggle = (key: keyof Visibility) => setVisibility((current) => ({ ...current, [key]: !current[key] }));
  const selectedUav = selection.uav ? result?.allocation.find((row) => row.uav === selection.uav) : undefined;
  const selectedTarget = selection.target ? environment.targets.find((target) => target.id === selection.target) : undefined;
  const assignedUav = selectedTarget && result?.allocation.find((row) => row.targets.includes(selectedTarget.id))?.uav;
  const selectedCollision = selection.collision !== null ? result?.collisions[selection.collision] : undefined;
  const resetPlayback = () => { setElapsed(0); setPlaybackStatus("ready"); };
  const selectUav = (id: number) => setSelection({ uav: id || null, target: null, collision: null });

  return <div className="mission-page">
    <section className="mission-stage">
      <div className="mission-toolbar">
        <div className="toolbar-group"><span className="eyebrow cyan">3D MISSION VIEW</span><strong>{lifecycle.toUpperCase()}</strong></div>
        <div className="toolbar-group camera-buttons">{(["perspective", "top", "side"] as const).map((item) => <button className={preset === item ? "selected" : ""} key={item} onClick={() => setPreset(item)}>{item === "side" ? "Front / Side" : item[0].toUpperCase() + item.slice(1)}</button>)}<button onClick={() => setResetToken((value) => value + 1)}>Reset view</button></div>
        <div className="toolbar-group layer-buttons">{(["targets", "obstacles", "uavs", "paths", "waypoints", "collisions", "grid", "axes"] as const).map((key) => <button key={key} className={visibility[key] ? "selected" : ""} onClick={() => toggle(key)}>{key}</button>)}</div>
      </div>
      <div className="mission-canvas"><MissionCanvas environment={environment} result={result} visibility={visibility} selectedUav={selection.uav} selectedTarget={selection.target} selectedCollision={selection.collision} playbackPositions={playback.positions} visitedTargets={playback.visitedTargets} onSelectUav={selectUav} onSelectTarget={(id) => setSelection({ uav: result?.allocation.find((row) => row.targets.includes(id))?.uav ?? null, target: id, collision: null })} onSelectCollision={(index) => setSelection({ uav: result?.collisions[index]?.uav ?? null, target: null, collision: index })} cameraPreset={preset} resetToken={resetToken} /></div>
      <div className="scene-status"><span><i className="legend-dot cyan-dot" /> Backend coordinates / Z-up</span><span>{environment.dimensions.width} × {environment.dimensions.depth} × {environment.dimensions.height} m</span><span>{result ? "Optimized route data loaded" : "Paths appear after optimization completes"}</span></div>
    </section>
    <section className="playback-panel">
      <div><span className="eyebrow">MISSION PLAYBACK</span><strong>{result ? playbackStatus.toUpperCase() : "WAITING FOR FINAL RESULT"}</strong></div>
      <div className="playback-actions"><button className="button compact" disabled={!result || playbackStatus === "playing"} onClick={() => setPlaybackStatus("playing")}>Play</button><button className="button compact" disabled={!result || playbackStatus !== "playing"} onClick={() => setPlaybackStatus("paused")}>Pause</button><button className="button compact" disabled={!result} onClick={resetPlayback}>Restart</button><select value={speed} onChange={(event) => setSpeed(Number(event.target.value))} disabled={!result}>{[0.25, 0.5, 1, 2, 4].map((value) => <option key={value} value={value}>{value}×</option>)}</select></div>
      <div className="timeline"><div className="timeline-track"><i style={{ width: `${playback.progress * 100}%` }} /></div><div className="timeline-meta"><span>{fmt(playback.elapsed)} s</span><span>{Math.round(playback.progress * 100)}% complete</span><span>{result ? `${playback.visitedTargets.length} / ${environment.target_count} targets visited` : "No playback data"}</span></div></div>
    </section>
    <div className="mission-underbar">
      <section className="mission-info panel"><div className="panel-head"><div><span className="eyebrow">MISSION LEGEND</span><h3>Scene layers</h3></div></div><div className="legend-grid"><span><i className="legend-dot cyan-dot" />UAV / path</span><span><i className="legend-dot green-dot" />Visited target</span><span><i className="legend-dot amber-dot" />Waypoint</span><span><i className="legend-dot red-dot" />Collision segment</span><span><i className="legend-dot obstacle-dot" />AABB obstacle</span></div></section>
      <section className="mission-info panel"><div className="panel-head"><div><span className="eyebrow">INSPECTOR</span><h3>{selection.uav ? `UAV ${selection.uav}` : selection.target ? `Target ${selection.target}` : selectedCollision ? "Collision diagnostic" : "Mission overview"}</h3></div></div><Inspector environment={environment} result={result} selectedUav={selectedUav} selectedTarget={selectedTarget} assignedUav={assignedUav} selectedCollision={selectedCollision} playback={playback} /></section>
    </div>
  </div>;
}

function Inspector({ environment, result, selectedUav, selectedTarget, assignedUav, selectedCollision, playback }: { environment: NonNullable<ReturnType<typeof useStore>["environment"]>; result: FinalResult | null; selectedUav: FinalResult["allocation"][number] | undefined; selectedTarget: typeof environment.targets[number] | undefined; assignedUav: number | undefined; selectedCollision: FinalResult["collisions"][number] | undefined; playback: ReturnType<typeof samplePlayback> }) {
  if (selectedUav) return <div className="inspector-list"><p><span>Assigned targets</span><b>{selectedUav.targets.join(" · ") || "—"}</b></p><p><span>Target count</span><b>{selectedUav.target_count}</b></p><p><span>Route distance</span><b>{fmt(selectedUav.path_distance)} m</b></p><p><span>Current position</span><b>{playback.positions[selectedUav.uav]?.map((value) => value.toFixed(1)).join(", ") || "Start position"}</b></p><p><span>Route status</span><b>{result ? "Backend path loaded" : "Awaiting result"}</b></p></div>;
  if (selectedTarget) return <div className="inspector-list"><p><span>Position</span><b>[{selectedTarget.position.map((value) => value.toFixed(1)).join(", ")}]</b></p><p><span>Assigned UAV</span><b>{assignedUav ? `UAV ${assignedUav}` : "—"}</b></p><p><span>Playback state</span><b>{playback.visitedTargets.includes(selectedTarget.id) ? "Visited" : "Remaining"}</b></p></div>;
  if (selectedCollision) return <div className="inspector-list"><p><span>UAV</span><b>{selectedCollision.uav}</b></p><p><span>Segment</span><b>{selectedCollision.segment_index}</b></p><p><span>Obstacle</span><b>{selectedCollision.obstacle}</b></p><p><span>Segment start</span><b>[{selectedCollision.start.map((value) => value.toFixed(1)).join(", ")}]</b></p><p><span>Segment end</span><b>[{selectedCollision.end.map((value) => value.toFixed(1)).join(", ")}]</b></p></div>;
  return <div className="inspector-list"><p><span>Dimensions</span><b>{environment.dimensions.width} × {environment.dimensions.depth} × {environment.dimensions.height} m</b></p><p><span>UAV fleet</span><b>{environment.uav_count}</b></p><p><span>Targets</span><b>{environment.target_count}</b></p><p><span>Obstacles</span><b>{environment.obstacle_count}</b></p><p><span>Optimization</span><b>{result ? "Completed" : "In progress / not started"}</b></p><p><span>Collisions</span><b>{result?.metrics.collision_count ?? "—"}</b></p></div>;
}
