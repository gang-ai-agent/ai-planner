from fastapi.testclient import TestClient

from app.main import app


def test_chat_endpoint_returns_follow_up_for_missing_slots() -> None:
    client = TestClient(app)
    response = client.post("/api/chat", json={"user_id": "u1", "message": "Plan a trip"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "waiting_for_user"
    assert payload["follow_up_questions"]
