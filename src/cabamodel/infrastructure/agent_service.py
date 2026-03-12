import asyncio
import functools
from typing import Any, Callable, TypeVar, Coroutine
from google.adk.agents import Agent
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from src.cabamodel.domain.models import AgentConfig

T = TypeVar("T")

# Exponential backoff for external API calls
standard_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((Exception,)),  # Narrow this to specific ADK/GRPC errors if known
    reraise=True
)

class AgentFactory:
    """Infrastructure-layer factory for creating resilient ADK agents."""

    @staticmethod
    def create_agent(config: AgentConfig) -> Agent:
        """Instantiates a Google-ADK agent with domain configuration.
        
        Args:
            config: Domain-defined agent configuration.
            
        Returns:
            An initialized Google ADK Agent instance.
        """
        return Agent(
            name=config.name,
            model=config.model,
            description=config.description,
            instruction=config.instruction,
            tools=config.tools
        )

def async_tool(func: Callable[..., Any]) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Decorator to wrap synchronous tools into async-compatible execution.
    
    Args:
        func: The synchronous tool function.
        
    Returns:
        The wrapped async function.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
