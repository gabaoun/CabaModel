from typing import List, Optional, Callable
from pydantic import BaseModel, Field, ConfigDict

class AgentConfig(BaseModel):
    """Configuration schema for any ADK-based agent.
    
    Attributes:
        name: Unique identifier for the agent.
        model: Target Gemini model identifier.
        description: Functional description for the agent's purpose.
        instruction: System prompt guiding the agent's behavior.
        tools: List of executable functions available to the agent.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., min_length=3, max_length=50)
    model: str = Field(default="gemini-2.0-flash")
    description: str = Field(..., min_length=10)
    instruction: str = Field(..., min_length=20)
    tools: List[Callable] = Field(default_factory=list)
