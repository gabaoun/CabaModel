import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
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
            tools=config.tools  # type: ignore[arg-type]  # list is invariant; domain Callables are a valid subset of ADK's broader tools union
        )

def async_tool(func: Callable[..., Any]) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Decorator to wrap synchronous tools into async-compatible execution."""
    import functools
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

async def run_agent_async(agent: Agent, message: str) -> str:
    """
    Runs an agent asynchronously using the Runner.run_async pattern (ADK 1.30.0+).
    This is the recommended way for production and better error handling.
    """
    # 1. Setup Session Service (In-memory for simplicity)
    session_service = InMemorySessionService()  # type: ignore[no-untyped-call]  # google-adk ships incomplete type stubs
    
    # 2. Setup Runner
    runner = Runner(
        app_name="cabamodel_app",
        agent=agent,
        session_service=session_service,
        auto_create_session=True
    )
    
    # 3. Format input
    content = types.Content(
        role='user',
        parts=[types.Part(text=message)]
    )
    
    full_response = []
    
    # 4. Run the agent and collect events
    try:
        async for event in runner.run_async(
            user_id="default_user",
            session_id="default_session",
            new_message=content
        ):
            # We look for content in any event that has text part
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        full_response.append(part.text)
    except Exception as e:  # noqa: BLE001 - translates any ADK/model failure into a user-facing message
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "ERROR: Google API Quota Exceeded (429). Please wait a moment or try again."
        elif "404" in error_msg:
            return "ERROR: Model not found (404). Falling back..."
        return f"ERROR: {error_msg}"

    result = "".join(full_response).strip()
    return result if result else "Agent finished with no text output."
