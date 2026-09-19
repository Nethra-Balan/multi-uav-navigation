import os
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.manager import MissionManager
from backend.schemas import (
    HealthResponse,
    LifecycleResponse,
    MissionConfigRequest,
    MissionResponse,
    StatusResponse,
)
from src.integration.serialization import to_json_safe


app = FastAPI(
    title="Dronetic Engine API",
    description="Programmatic API for the Dronetic multi-UAV optimization engine.",
    version="1.0.0",
)
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "DRONETIC_CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = MissionManager()


def mission_or_404(mission_id: str):
    try:
        return manager.get(mission_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="mission not found") from exc


def transition_error(exc: RuntimeError):
    raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/health", response_model=HealthResponse)
def health():
    return {
        "status": "ok",
        "service": "dronetic-fastapi",
        "engine_available": True,
    }


@app.post("/api/missions", response_model=MissionResponse, status_code=201)
def create_mission(request: MissionConfigRequest):
    try:
        config = request.to_engine_config()
        mission = manager.create(config, request.algorithm.value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "mission_id": mission.mission_id,
        "status": mission.status,
        "configuration": to_json_safe({
            **config.__dict__,
            "algorithm": request.algorithm.value,
        }),
        "environment": manager.environment_payload(mission),
    }


@app.get("/api/missions/{mission_id}/environment")
def environment(mission_id: str):
    mission = mission_or_404(mission_id)
    return manager.environment_payload(mission)


@app.post("/api/missions/{mission_id}/optimization/start", response_model=LifecycleResponse)
def start_optimization(mission_id: str):
    mission = mission_or_404(mission_id)
    try:
        manager.start(mission)
    except RuntimeError as exc:
        transition_error(exc)
    return {
        "mission_id": mission_id,
        "status": "starting",
        "message": "optimization started",
    }


@app.post("/api/missions/{mission_id}/optimization/pause", response_model=LifecycleResponse)
def pause_optimization(mission_id: str):
    mission = mission_or_404(mission_id)
    try:
        manager.pause(mission)
    except RuntimeError as exc:
        transition_error(exc)
    return {"mission_id": mission_id, "status": "paused", "message": "optimization paused"}


@app.post("/api/missions/{mission_id}/optimization/resume", response_model=LifecycleResponse)
def resume_optimization(mission_id: str):
    mission = mission_or_404(mission_id)
    try:
        manager.resume(mission)
    except RuntimeError as exc:
        transition_error(exc)
    return {"mission_id": mission_id, "status": "running", "message": "optimization resumed"}


@app.post("/api/missions/{mission_id}/optimization/stop", response_model=LifecycleResponse)
def stop_optimization(mission_id: str):
    mission = mission_or_404(mission_id)
    try:
        manager.stop(mission)
    except RuntimeError as exc:
        transition_error(exc)
    return {"mission_id": mission_id, "status": "stopping", "message": "optimization stopping"}


@app.get("/api/missions/{mission_id}/optimization/status", response_model=StatusResponse)
def optimization_status(mission_id: str):
    mission = mission_or_404(mission_id)
    return manager.status_payload(mission)


@app.get("/api/missions/{mission_id}/results")
def results(mission_id: str):
    mission = mission_or_404(mission_id)
    with mission.lock:
        if mission.final_result is None:
            raise HTTPException(status_code=409, detail="final result is not available")
        return mission.final_result


@app.websocket("/ws/missions/{mission_id}/optimization")
async def optimization_stream(websocket: WebSocket, mission_id: str):
    try:
        mission = manager.get(mission_id)
    except KeyError:
        await websocket.close(code=1008, reason="mission not found")
        return
    await websocket.accept()
    queue = manager.subscribe(mission)
    await websocket.send_json({
        "type": "connection_ack",
        "mission_id": mission_id,
        "payload": manager.status_payload(mission),
    })
    try:
        while True:
            message = await queue.get()
            await websocket.send_json(message)
    except WebSocketDisconnect:
        pass
    finally:
        manager.unsubscribe(mission, queue)
