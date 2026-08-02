import asyncio

import pytest

from src.cabamodel.domain.models import AgentConfig
from src.cabamodel.infrastructure.agent_service import AgentFactory, async_tool


def _config(**overrides):
    kwargs = {
        "name": "factory_agent",
        "description": "A sufficiently long description for the agent.",
        "instruction": "A sufficiently long instruction for the agent to follow.",
    }
    kwargs.update(overrides)
    return AgentConfig(**kwargs)


def test_create_agent_maps_config_fields_onto_adk_agent():
    def dummy_tool():
        return "ok"

    config = _config(tools=[dummy_tool])
    agent = AgentFactory.create_agent(config)

    assert agent.name == config.name
    assert agent.model == config.model
    assert agent.description == config.description
    assert agent.instruction == config.instruction
    assert agent.tools == [dummy_tool]


def test_create_agent_defaults_to_no_tools():
    agent = AgentFactory.create_agent(_config())
    assert agent.tools == []


def test_async_tool_wraps_sync_function_and_returns_its_result():
    def add(a, b):
        return a + b

    wrapped = async_tool(add)
    result = asyncio.run(wrapped(2, 3))

    assert result == 5


def test_async_tool_propagates_exceptions_from_the_wrapped_function():
    def boom():
        raise ValueError("expected failure")

    wrapped = async_tool(boom)

    with pytest.raises(ValueError, match="expected failure"):
        asyncio.run(wrapped())
