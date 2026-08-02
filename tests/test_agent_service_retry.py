import asyncio
from types import SimpleNamespace

import pytest

from src.cabamodel.domain.models import AgentConfig
from src.cabamodel.infrastructure import agent_service
from src.cabamodel.infrastructure.agent_service import AgentFactory, run_agent_async


def _agent():
    config = AgentConfig(
        name="retry_agent",
        description="A sufficiently long description for the agent.",
        instruction="A sufficiently long instruction for the agent to follow.",
    )
    return AgentFactory.create_agent(config)


class _RaisingRunner:
    """Stands in for google.adk.runners.Runner and fails as soon as it's iterated."""

    def __init__(self, error: Exception, **_kwargs):
        self._error = error

    def run_async(self, **_kwargs):
        async def _gen():
            raise self._error
            yield  # pragma: no cover - unreachable, makes this an async generator

        return _gen()


class _TextEventRunner:
    """Stands in for Runner and yields a fixed sequence of text-bearing events."""

    def __init__(self, texts, **_kwargs):
        self._texts = texts

    def run_async(self, **_kwargs):
        async def _gen():
            for text in self._texts:
                part = SimpleNamespace(text=text)
                yield SimpleNamespace(content=SimpleNamespace(parts=[part]))

        return _gen()


@pytest.mark.parametrize(
    "raw_message,expected_snippet",
    [
        ("429 RESOURCE_EXHAUSTED: quota", "Google API Quota Exceeded"),
        ("model 404 not found", "Model not found (404)"),
        ("connection reset by peer", "connection reset by peer"),
    ],
)
def test_run_agent_async_translates_known_error_shapes(monkeypatch, raw_message, expected_snippet):
    monkeypatch.setattr(
        agent_service, "Runner", lambda **kwargs: _RaisingRunner(Exception(raw_message), **kwargs)
    )

    result = asyncio.run(run_agent_async(_agent(), "What time is it?"))

    assert expected_snippet in result


def test_run_agent_async_joins_streamed_text_parts(monkeypatch):
    monkeypatch.setattr(
        agent_service, "Runner", lambda **kwargs: _TextEventRunner(["It is ", "14:32."], **kwargs)
    )

    result = asyncio.run(run_agent_async(_agent(), "What time is it?"))

    assert result == "It is 14:32."


def test_run_agent_async_reports_when_no_text_was_produced(monkeypatch):
    monkeypatch.setattr(agent_service, "Runner", lambda **kwargs: _TextEventRunner([], **kwargs))

    result = asyncio.run(run_agent_async(_agent(), "..."))

    assert result == "Agent finished with no text output."
