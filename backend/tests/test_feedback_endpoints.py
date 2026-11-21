from fastapi.testclient import TestClient

import main
import database


def _set_temp_db(tmp_path) -> None:
    db_file = tmp_path / "test.db"
    database.configure_database(f"sqlite:///{db_file}")
    database.Base.metadata.drop_all(bind=database.ENGINE)
    database.Base.metadata.create_all(bind=database.ENGINE)


def test_submit_feedback_saves_entry(tmp_path):
    _set_temp_db(tmp_path)
    client = TestClient(main.app)

    payload = {
        "feedback_type": "like",
        "comment": "Muy util",
        "origin": "https://example.com",
        "extension_version": "1.0.0",
        "anonymous_user_id": "abc1234567",
        "timestamp": "2026-10-07T12:00:00Z",
    }

    response = client.post("/api/v1/feedback", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "saved"
    assert isinstance(body["feedback_id"], int)
    assert body["feedback_id"] == 1


def test_feedback_stats_counts_like_and_dislike(tmp_path):
    _set_temp_db(tmp_path)
    client = TestClient(main.app)

    base_payload = {
        "origin": "https://example.com",
        "extension_version": "1.0.0",
        "anonymous_user_id": "user-001",
        "timestamp": "2026-10-07T12:00:00Z",
    }

    client.post("/api/v1/feedback", json={**base_payload, "feedback_type": "like"})
    client.post("/api/v1/feedback", json={**base_payload, "feedback_type": "dislike", "anonymous_user_id": "user-002"})
    client.post(
        "/api/v1/feedback",
        json={
            **base_payload,
            "feedback_type": "like",
            "origin": "https://other.com",
            "anonymous_user_id": "user-003",
        },
    )

    response_all = client.get("/api/v1/feedback/stats")
    assert response_all.status_code == 200
    assert response_all.json()["total"] == 3

    response_origin = client.get("/api/v1/feedback/stats", params={"origin": "https://example.com"})
    assert response_origin.status_code == 200
    stats = response_origin.json()
    assert stats["total"] == 2
    assert stats["likes"] == 1
    assert stats["dislikes"] == 1


def test_submit_feedback_rejects_invalid_type(tmp_path):
    _set_temp_db(tmp_path)
    client = TestClient(main.app)

    payload = {
        "feedback_type": "meh",
        "anonymous_user_id": "abc1234567",
    }

    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 422


def test_darkmode_state_roundtrip(tmp_path):
    _set_temp_db(tmp_path)
    client = TestClient(main.app)

    origin = "https://example.com"
    response_initial = client.get(f"/api/v1/darkmode/state/{origin}")
    assert response_initial.status_code == 200
    assert response_initial.json()["enabled"] is False

    save_response = client.post(
        "/api/v1/darkmode/state",
        json={"origin": origin, "enabled": True},
    )
    assert save_response.status_code == 200
    assert save_response.json()["status"] == "saved"

    response_after = client.get(f"/api/v1/darkmode/state/{origin}")
    assert response_after.status_code == 200
    body = response_after.json()
    assert body["enabled"] is True
    assert body["last_updated"] is not None


