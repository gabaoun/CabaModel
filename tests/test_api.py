import pytest
from fastapi.testclient import TestClient

import src.cabamodel.infrastructure.api as api_module
from src.cabamodel.infrastructure.api import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    api_module._request_log.clear()
    yield
    api_module._request_log.clear()


def test_root_reports_service_is_running():
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "CabaModel API is running"
    assert body["docs"] == "/docs"


def test_chat_rejects_unknown_agent_type_without_calling_the_model():
    response = client.post("/chat", json={"message": "hi", "agent_type": "not_a_real_agent"})

    assert response.status_code == 400
    assert "Agent type invalid" in response.json()["detail"]


def test_chat_routes_to_the_requested_agent(monkeypatch):
    async def fake_run_agent_async(agent, message):
        assert message == "what time is it?"
        return f"mocked response from {agent.name}"

    # The model call itself is mocked - this test exercises routing/response
    # shaping, not the real Gemini API (no key or network access in CI).
    monkeypatch.setattr(api_module, "run_agent_async", fake_run_agent_async)

    response = client.post("/chat", json={"message": "what time is it?", "agent_type": "temporal"})

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "mocked response from Temporal_Tool_Agent"
    assert body["agent_name"] == "Temporal_Tool_Agent"


def test_chat_defaults_to_temporal_agent_when_agent_type_omitted(monkeypatch):
    async def fake_run_agent_async(agent, message):
        return f"mocked response from {agent.name}"

    monkeypatch.setattr(api_module, "run_agent_async", fake_run_agent_async)

    response = client.post("/chat", json={"message": "hi"})

    assert response.status_code == 200
    assert response.json()["agent_name"] == "Temporal_Tool_Agent"


def test_chat_returns_500_when_the_agent_run_raises(monkeypatch):
    async def failing_run_agent_async(agent, message):
        raise RuntimeError("boom")

    monkeypatch.setattr(api_module, "run_agent_async", failing_run_agent_async)

    response = client.post("/chat", json={"message": "hi", "agent_type": "c4b4"})

    assert response.status_code == 500
    assert "boom" in response.json()["detail"]


def test_chat_allows_requests_up_to_the_configured_limit(monkeypatch):
    monkeypatch.setattr(api_module, "RATE_LIMIT_PER_HOUR", 3)

    async def fake_run_agent_async(agent, message):
        return "ok"

    monkeypatch.setattr(api_module, "run_agent_async", fake_run_agent_async)

    for _ in range(3):
        response = client.post("/chat", json={"message": "hi"})
        assert response.status_code == 200


def test_chat_blocks_requests_beyond_the_configured_limit(monkeypatch):
    monkeypatch.setattr(api_module, "RATE_LIMIT_PER_HOUR", 2)

    async def fake_run_agent_async(agent, message):
        return "ok"

    monkeypatch.setattr(api_module, "run_agent_async", fake_run_agent_async)

    for _ in range(2):
        assert client.post("/chat", json={"message": "hi"}).status_code == 200

    response = client.post("/chat", json={"message": "hi"})

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]


def test_chat_rate_limit_resets_after_the_window_elapses(monkeypatch):
    monkeypatch.setattr(api_module, "RATE_LIMIT_PER_HOUR", 1)

    async def fake_run_agent_async(agent, message):
        return "ok"

    monkeypatch.setattr(api_module, "run_agent_async", fake_run_agent_async)

    assert client.post("/chat", json={"message": "hi"}).status_code == 200
    assert client.post("/chat", json={"message": "hi"}).status_code == 429

    # Simulate the window elapsing by rewriting the logged timestamp directly.
    for client_id in api_module._request_log:
        api_module._request_log[client_id] = [
            t - api_module._RATE_LIMIT_WINDOW_SECONDS - 1 for t in api_module._request_log[client_id]
        ]

    assert client.post("/chat", json={"message": "hi"}).status_code == 200
