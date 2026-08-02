import pytest
from pydantic import ValidationError

from src.cabamodel.domain.models import AgentConfig


def _valid_kwargs(**overrides):
    kwargs = {
        "name": "valid_agent",
        "description": "A sufficiently long description for the agent.",
        "instruction": "A sufficiently long instruction for the agent to follow.",
    }
    kwargs.update(overrides)
    return kwargs


def test_defaults_to_gemini_flash_model():
    config = AgentConfig(**_valid_kwargs())
    assert config.model == "gemini-2.0-flash"


def test_accepts_explicit_model_override():
    config = AgentConfig(**_valid_kwargs(model="gemini-flash-latest"))
    assert config.model == "gemini-flash-latest"


def test_tools_default_to_empty_list():
    config = AgentConfig(**_valid_kwargs())
    assert config.tools == []


def test_rejects_name_below_min_length():
    with pytest.raises(ValidationError):
        AgentConfig(**_valid_kwargs(name="ab"))


def test_rejects_name_above_max_length():
    with pytest.raises(ValidationError):
        AgentConfig(**_valid_kwargs(name="a" * 51))


def test_rejects_description_below_min_length():
    with pytest.raises(ValidationError):
        AgentConfig(**_valid_kwargs(description="short"))


def test_rejects_instruction_below_min_length():
    with pytest.raises(ValidationError):
        AgentConfig(**_valid_kwargs(instruction="too short"))


def test_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        AgentConfig(name="valid_agent")
