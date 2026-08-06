import asyncio

import pytest

from src.cabamodel.domain.models import AgentConfig
from src.cabamodel.infrastructure.agent_service import AgentFactory


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



