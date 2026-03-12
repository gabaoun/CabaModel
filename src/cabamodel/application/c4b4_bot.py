from src.cabamodel.domain.models import AgentConfig
from src.cabamodel.infrastructure.agent_service import AgentFactory

# Configuration definition using Pydantic
c4b4_config = AgentConfig(
    name="C4B4-Assistant",
    model="gemini-2.0-flash",
    description="Community support agent specializing in automated assistance for the C4B4 ecosystem.",
    instruction="""You are the C4B4 Assistant, a highly efficient, friendly, and direct 
    autonomous agent. Your primary goal is to assist the community with technical guidance 
    and operational support. Always prioritize clarity and accuracy in your responses."""
)

# Resilient instantiation
root_agent = AgentFactory.create_agent(c4b4_config)
