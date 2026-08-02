import pytest
from fastapi.testclient import TestClient

import src.cabamodel.infrastructure.api as api_module
from src.cabamodel.infrastructure.api import app

client = TestClient(app)


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
