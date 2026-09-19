import json
import time

from fastapi.testclient import TestClient

from backend.app import app


def small_config(**overrides):
    config = {
        "environment_dimensions": [80, 80, 50],
        "seed": 7,
        "uav_count": 2,
        "target_count": 6,
        "obstacle_count": 1,
        "population_size": 4,
        "generations": 2,
        "elite_count": 1,
        "algorithm": "adaptive",
    }
    config.update(overrides)
    return config


def wait_for_status(client, mission_id, expected, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        response = client.get(
            f"/api/missions/{mission_id}/optimization/status"
        )
        status = response.json()["status"]
        if status in expected:
            return response.json()
        time.sleep(0.02)
    raise AssertionError(f"status did not reach {expected}")


def test_health_and_mission_environment_are_real_and_json_safe():
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["engine_available"] is True

        mission = client.post("/api/missions", json=small_config())
        assert mission.status_code == 201
        body = mission.json()
        assert body["environment"]["seed"] == 7
        assert len(body["environment"]["target_positions"]) == 6
        assert body["environment"]["uavs"] == [
            {"id": 1, "start_position": [10.0, 10.0, 10.0]},
            {"id": 2, "start_position": [10.0, 10.0, 10.0]},
        ]
        assert [
            target["id"] for target in body["environment"]["targets"]
        ] == list(range(1, 7))
        assert [
            target["position"]
            for target in body["environment"]["targets"]
        ] == body["environment"]["target_positions"]
        assert len(body["environment"]["obstacles"]) == 1
        json.dumps(body)

        environment = client.get(
            f"/api/missions/{body['mission_id']}/environment"
        )
        assert environment.status_code == 200
        assert environment.json()["dimensions"] == {
            "width": 80.0,
            "depth": 80.0,
            "height": 50.0,
        }


def test_invalid_configuration_and_lifecycle_transitions():
    with TestClient(app) as client:
        invalid = client.post(
            "/api/missions",
            json=small_config(target_count=1, uav_count=2),
        )
        assert invalid.status_code == 422

        mission = client.post("/api/missions", json=small_config()).json()
        mission_id = mission["mission_id"]
        assert client.post(
            f"/api/missions/{mission_id}/optimization/pause"
        ).status_code == 409
        assert client.post(
            f"/api/missions/{mission_id}/optimization/stop"
        ).status_code == 409
        assert client.get(
            f"/api/missions/{mission_id}/results"
        ).status_code == 409


def test_optimization_updates_websocket_and_final_result():
    with TestClient(app) as client:
        mission = client.post(
            "/api/missions",
            json=small_config(generations=3),
        ).json()
        mission_id = mission["mission_id"]

        with client.websocket_connect(
            f"/ws/missions/{mission_id}/optimization"
        ) as websocket:
            ack = websocket.receive_json()
            assert ack["type"] == "connection_ack"

            started = client.post(
                f"/api/missions/{mission_id}/optimization/start"
            )
            assert started.status_code == 200

            messages = []
            final_message = None
            deadline = time.time() + 20
            while time.time() < deadline:
                message = websocket.receive_json()
                messages.append(message)
                if message["type"] == "optimization_completed":
                    final_message = message
                    break

            assert final_message is not None
            generation_messages = [
                message for message in messages
                if message["type"] == "generation_update"
            ]
            assert len(generation_messages) == 3
            assert generation_messages[-1]["payload"]["generation"] == 3
            json.dumps(generation_messages[-1])

        status = wait_for_status(client, mission_id, {"completed"})
        assert status["generation"] == 3
        assert status["best_fitness"] is not None
        assert status["collision_count"] is not None

        result = client.get(
            f"/api/missions/{mission_id}/results"
        )
        assert result.status_code == 200
        result_body = result.json()
        assert len(result_body["allocation"]) == 2
        assert len(result_body["paths"]) == 2
        assert len(result_body["uav_paths"]) == 2
        for uav_path in result_body["uav_paths"]:
            assert uav_path["uav"] in {1, 2}
            assert uav_path["points"][0]["kind"] == "start"
            assert all(
                point["kind"] in {"start", "waypoint", "target"}
                for point in uav_path["points"]
            )
            assert [
                point["target"]
                for point in uav_path["points"]
                if point["kind"] == "target"
            ] == result_body["allocation"][uav_path["uav"] - 1]["targets"]
            assert all(
                "target" in point
                for point in uav_path["points"]
                if point["kind"] == "target"
            )
            assert all(
                "target" not in point
                for point in uav_path["points"]
                if point["kind"] != "target"
            )
        assert "validation" in result_body
        assert "waypoints" in result_body
        assert "collisions" in result_body
        assert "metrics" in result_body
        json.dumps(result_body)


def test_pause_resume_and_stop_are_boundary_safe():
    with TestClient(app) as client:
        mission = client.post(
            "/api/missions",
            json=small_config(generations=20),
        ).json()
        mission_id = mission["mission_id"]
        assert client.post(
            f"/api/missions/{mission_id}/optimization/start"
        ).status_code == 200
        wait_for_status(client, mission_id, {"running", "paused", "completed"})

        pause = client.post(
            f"/api/missions/{mission_id}/optimization/pause"
        )
        if pause.status_code == 200:
            assert client.post(
                f"/api/missions/{mission_id}/optimization/resume"
            ).status_code == 200
        stop = client.post(
            f"/api/missions/{mission_id}/optimization/stop"
        )
        assert stop.status_code in {200, 409}
        final = wait_for_status(
            client,
            mission_id,
            {"stopped", "completed"},
        )
        assert final["status"] in {"stopped", "completed"}
