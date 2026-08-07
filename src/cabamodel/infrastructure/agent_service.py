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

@standard_retry
async def _execute_agent(config: AgentConfig, message: str) -> str:
    """Executes the agent with tenacity exponential backoff retries."""
    session_service = InMemorySessionService()  # type: ignore[no-untyped-call]
    agent = AgentFactory.create_agent(config)
    
    runner = Runner(
        app_name="cabamodel_app",
        agent=agent,
        session_service=session_service,
        auto_create_session=True
    )
    
    content = types.Content(
        role='user',
        parts=[types.Part(text=message)]
    )
    
    full_response = []
    
    async for event in runner.run_async(
        user_id="default_user",
        session_id="default_session",
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    full_response.append(part.text)

    result = "".join(full_response).strip()
    if not result:
        # Not a failure worth retrying/falling back over: the call succeeded,
        # the model just had nothing to say. Return directly instead of
        # raising, so it doesn't burn the retry budget or trigger fallback.
        return "Agent finished with no text output."
    return result

def _translate_known_error(error_msg: str) -> str:
    """Maps a raw provider error string to a user-facing explanation."""
    if "404" in error_msg:
        return "Model not found (404)"
    if "500" in error_msg or "503" in error_msg:
        return "Service temporarily unavailable"
    return error_msg

async def run_agent_async(config: AgentConfig, message: str) -> str:
    """
    Public entrypoint for running an agent.
    Includes the @standard_retry loop internally via _execute_agent,
    and implements a true Fallback to a lighter model on critical errors.
    """
    try:
        return await _execute_agent(config, message)
    except Exception as e:  # noqa: BLE001
        error_msg = str(e)
        # Handle Quota / Rate Limiting (even after 3 retries)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "ERROR: Google API Quota Exceeded (429) after retries. Please wait."
        
        # Handle Model Not Found or Internal Errors by falling back!
        if "404" in error_msg or "500" in error_msg or "503" in error_msg:
            fallback_model = "gemini-1.5-flash"
            if config.model != fallback_model:
                fallback_config = config.model_copy(update={"model": fallback_model})
                try:
                    return await _execute_agent(fallback_config, message)
                except Exception as e_fallback:  # noqa: BLE001
                    return f"ERROR: Primary and Fallback models failed. Last error: {_translate_known_error(str(e_fallback))}"
            return f"ERROR: {_translate_known_error(error_msg)}"
        
        return f"ERROR: {error_msg}"
