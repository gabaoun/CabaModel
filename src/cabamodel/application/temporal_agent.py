from datetime import UTC, datetime

from src.cabamodel.domain.models import AgentConfig
from src.cabamodel.infrastructure.agent_service import AgentFactory


def get_current_time() -> str:
    """Retrieves the current system time in HH:MM:SS format.

    Returns:
        str: Current formatted time string.
    """
    return datetime.now(UTC).strftime("%H:%M:%S")

def get_current_weekday() -> str:
    """Retrieves the current day of the week.

    Returns:
        str: Current weekday string (e.g., 'Monday').
    """
    return datetime.now(UTC).strftime("%A")

# Temporal agent configuration with strict validation
temporal_config = AgentConfig(
    name="Temporal_Tool_Agent",
    model="gemini-flash-latest",
    description="A specialized temporal agent capable of retrieving real-time system clock data.",
    instruction="""You are the Temporal Tool Agent, a precise assistant focused on providing 
    accurate time and date information. Use the provided system tools to answer temporal 
    queries accurately and professionally.""",
    tools=[get_current_time, get_current_weekday]
)


