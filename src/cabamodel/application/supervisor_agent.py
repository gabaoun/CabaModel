import asyncio
import concurrent.futures
from typing import Any, Coroutine

from src.cabamodel.domain.models import AgentConfig
from src.cabamodel.application.temporal_agent import temporal_config
from src.cabamodel.application.c4b4_bot import c4b4_config
from src.cabamodel.infrastructure.agent_service import run_agent_async

def _run_async_in_thread(coro: Coroutine[Any, Any, Any]) -> Any:
    """Helper to run async code safely from a sync tool if called inside an event loop."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)

def ask_temporal_agent(query: str) -> str:
    """
    Delegates time, date, and schedule related queries to the Temporal Agent.
    Use this tool when the user asks about the current time, day, or date.
    
    Args:
        query: The specific question to ask the Temporal Agent.
    """
    return _run_async_in_thread(run_agent_async(temporal_config, query))

def ask_c4b4_agent(query: str) -> str:
    """
    Delegates community support and operational queries to the C4B4 Agent.
    Use this tool when the user asks for community help, platform operations, or C4B4 specific knowledge.
    
    Args:
        query: The specific question to ask the C4B4 Agent.
    """
    return _run_async_in_thread(run_agent_async(c4b4_config, query))

supervisor_config = AgentConfig(
    name="Supervisor_Agent",
    model="gemini-1.5-pro",
    description="The main intelligent routing agent that delegates tasks to specialized sub-agents.",
    instruction="""You are the master Supervisor Agent. Your job is to understand the user's request
    and decide which sub-agent is best suited to handle it. You have access to tools that can invoke
    the Temporal Agent (for time/date queries) and the C4B4 Agent (for community/support queries).
    If a query requires both, you can call both tools. Synthesize the final answer based on the responses
    from the sub-agents. Do not attempt to answer temporal or community questions yourself without 
    using the appropriate tool first.""",
    tools=[ask_temporal_agent, ask_c4b4_agent]
)
