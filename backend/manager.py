import asyncio
import logging
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

from src.adaptive_genetic_algorithm import AdaptiveGeneticAlgorithm
from src.environment import Environment
from src.genetic_algorithm import GeneticAlgorithm
from src.integration.engine_config import EngineConfig
from src.integration.results import extract_final_result
from src.integration.serialization import (
    serialize_environment,
    serialize_generation_event,
    to_json_safe,
)
from src.population import generate_population


logger = logging.getLogger(__name__)


@dataclass
class MissionState:
    mission_id: str
    config: EngineConfig
    algorithm_mode: str
    environment: Environment
    population: list
    status: str = "idle"
    generation: Optional[int] = None
    latest_event: Optional[Dict[str, Any]] = None
    final_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    pause_event: threading.Event = field(default_factory=threading.Event)
    stop_event: threading.Event = field(default_factory=threading.Event)
    worker: Optional[threading.Thread] = None
    lock: threading.RLock = field(default_factory=threading.RLock)
    subscribers: Set[asyncio.Queue] = field(default_factory=set)
    subscriber_loops: Dict[asyncio.Queue, asyncio.AbstractEventLoop] = field(
        default_factory=dict
    )


class MissionManager:
    def __init__(self):
        self._missions: Dict[str, MissionState] = {}
        self._lock = threading.RLock()

    def create(self, config: EngineConfig, algorithm_mode: str) -> MissionState:
        environment = Environment(
            size=config.environment_size,
            num_uavs=config.num_uavs,
            num_targets=config.num_targets,
            num_obstacles=config.num_obstacles,
            random_seed=config.seed,
        )
        population = generate_population(
            num_individuals=config.population_size,
            num_targets=config.num_targets,
            num_uavs=config.num_uavs,
            random_seed=config.seed,
        )
        mission = MissionState(
            mission_id=str(uuid.uuid4()),
            config=config,
            algorithm_mode=algorithm_mode,
            environment=environment,
            population=population,
        )
        with self._lock:
            self._missions[mission.mission_id] = mission
        return mission

    def get(self, mission_id: str) -> MissionState:
        with self._lock:
            mission = self._missions.get(mission_id)
        if mission is None:
            raise KeyError(mission_id)
        return mission

    def environment_payload(self, mission: MissionState) -> dict:
        payload = serialize_environment(mission.environment)
        payload.update({
            "seed": mission.config.seed,
            "uav_count": mission.config.num_uavs,
            "target_count": mission.config.num_targets,
            "obstacle_count": mission.config.num_obstacles,
        })
        return payload

    def status_payload(self, mission: MissionState) -> dict:
        with mission.lock:
            payload = {
                "mission_id": mission.mission_id,
                "status": mission.status,
                "total_generations": mission.config.generations,
            }
            if mission.latest_event is not None:
                payload.update({
                    key: mission.latest_event.get(key)
                    for key in (
                        "generation",
                        "best_fitness",
                        "mean_fitness",
                        "mutation_probability",
                        "total_path_distance",
                        "collision_count",
                        "balance_penalty",
                        "route_distances",
                        "target_counts",
                    )
                })
            if mission.error is not None:
                payload["error"] = mission.error
            return to_json_safe(payload)

    def start(self, mission: MissionState):
        with mission.lock:
            if mission.status in {"starting", "running", "paused", "stopping"}:
                raise RuntimeError("optimization is already active")
            mission.status = "starting"
            mission.error = None
            mission.latest_event = None
            mission.final_result = None
            mission.pause_event.clear()
            mission.stop_event.clear()
            mission.worker = threading.Thread(
                target=self._run,
                args=(mission,),
                daemon=True,
            )
            mission.worker.start()
        self._publish(mission, "optimization_started", {
            "status": "starting",
            "total_generations": mission.config.generations,
        })

    def pause(self, mission: MissionState):
        with mission.lock:
            if mission.status != "running":
                raise RuntimeError("optimization is not running")
            mission.pause_event.set()
            mission.status = "paused"
        self._publish(mission, "optimization_paused", {"status": "paused"})

    def resume(self, mission: MissionState):
        with mission.lock:
            if mission.status != "paused":
                raise RuntimeError("optimization is not paused")
            mission.pause_event.clear()
            mission.status = "running"
        self._publish(mission, "optimization_resumed", {"status": "running"})

    def stop(self, mission: MissionState):
        with mission.lock:
            if mission.status not in {"running", "paused", "starting"}:
                raise RuntimeError("optimization is not active")
            mission.stop_event.set()
            mission.pause_event.clear()
            mission.status = "stopping"
        self._publish(mission, "optimization_stopping", {"status": "stopping"})

    def subscribe(self, mission: MissionState):
        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()
        with mission.lock:
            mission.subscribers.add(queue)
            mission.subscriber_loops[queue] = loop
        return queue

    def unsubscribe(self, mission: MissionState, queue: asyncio.Queue):
        with mission.lock:
            mission.subscribers.discard(queue)
            mission.subscriber_loops.pop(queue, None)

    def _publish(self, mission: MissionState, message_type: str, payload: dict):
        message = {
            "type": message_type,
            "mission_id": mission.mission_id,
            "payload": to_json_safe(payload),
        }
        with mission.lock:
            subscribers = list(mission.subscribers)
            loops = dict(mission.subscriber_loops)
        for queue in subscribers:
            loop = loops.get(queue)
            if loop is not None and not loop.is_closed():
                loop.call_soon_threadsafe(queue.put_nowait, message)

    def _run(self, mission: MissionState):
        try:
            algorithm_class = (
                AdaptiveGeneticAlgorithm
                if mission.algorithm_mode == "adaptive"
                else GeneticAlgorithm
            )
            if mission.algorithm_mode == "adaptive":
                algorithm = algorithm_class(
                    mission.population,
                    mission.environment,
                    generations=mission.config.generations,
                    elite_count=mission.config.elite_count,
                    crossover_probability=mission.config.crossover_probability,
                    mutation_minimum=mission.config.adaptive_mutation_minimum,
                    mutation_maximum=mission.config.adaptive_mutation_maximum,
                    collision_penalty=mission.config.collision_penalty,
                    balance_weight=mission.config.balance_weight,
                )
            else:
                algorithm = algorithm_class(
                    mission.population,
                    mission.environment,
                    generations=mission.config.generations,
                    elite_count=mission.config.elite_count,
                    crossover_probability=mission.config.crossover_probability,
                    mutation_probability=mission.config.fixed_mutation_probability,
                    collision_penalty=mission.config.collision_penalty,
                    balance_weight=mission.config.balance_weight,
                )
            with mission.lock:
                mission.status = "running"
            self._publish(mission, "optimization_running", {"status": "running"})

            def on_generation(event):
                serialized = serialize_generation_event(event)
                with mission.lock:
                    mission.generation = event.generation
                    mission.latest_event = serialized
                    if mission.status == "paused":
                        pass
                self._publish(mission, "generation_update", serialized)

            algorithm.run(
                callback=on_generation,
                pause_event=mission.pause_event,
                stop_event=mission.stop_event,
            )
            with mission.lock:
                if mission.stop_event.is_set():
                    mission.status = "stopped"
                else:
                    mission.status = "completed"
                if algorithm.best_chromosome is not None:
                    mission.final_result = extract_final_result(
                        algorithm.best_chromosome,
                        mission.environment,
                        mission.config.collision_penalty,
                        mission.config.balance_weight,
                    )
            if mission.status == "completed":
                self._publish(mission, "optimization_completed", mission.final_result or {})
            else:
                self._publish(mission, "optimization_stopped", {
                    "status": "stopped",
                    "result_available": mission.final_result is not None,
                })
        except Exception as exc:
            logger.exception("Dronetic optimization failed for %s", mission.mission_id)
            with mission.lock:
                mission.status = "error"
                mission.error = str(exc)
            self._publish(mission, "optimization_error", {
                "status": "error",
                "message": str(exc),
            })
