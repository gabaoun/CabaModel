import os
import time
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.cabamodel.application.supervisor_agent import supervisor_config
from src.cabamodel.infrastructure.agent_service import run_agent_async

app = FastAPI(
    title="CabaModel API",
    description="REST interface for Gemini-Native agent orchestration (Level 2 Multi-Agent)",
    version="1.0.0"
)

_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/ui", StaticFiles(directory=_STATIC_DIR, html=True), name="ui")

# In-memory per-IP sliding-window limiter for /chat. This is a public demo
# backed by a real Gemini API key/quota, so it needs a cheap guard against
# a single caller burning the quota. Single-process, resets on restart -
# acceptable for a free-tier demo deployment, not meant for production scale.
RATE_LIMIT_PER_HOUR = int(os.getenv("CHAT_RATE_LIMIT_PER_HOUR", "5"))
_RATE_LIMIT_WINDOW_SECONDS = 3600
_request_log: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(client_id: str, now: float | None = None) -> None:
    now = time.time() if now is None else now
    window_start = now - _RATE_LIMIT_WINDOW_SECONDS
    recent = [t for t in _request_log[client_id] if t > window_start]
    if len(recent) >= RATE_LIMIT_PER_HOUR:
        _request_log[client_id] = recent
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {RATE_LIMIT_PER_HOUR} requests/hour on this demo endpoint.",
        )
    recent.append(now)
    _request_log[client_id] = recent


class ChatRequest(BaseModel):
    message: str
    agent_type: str = "supervisor"  # Maintained for backward compatibility, but ignored

class ChatResponse(BaseModel):
    response: str
    agent_name: str

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "CabaModel API is running (Level 2)", "docs": "/docs", "ui": "/ui"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
    """
    Sends a message to the Supervisor Agent (Level 2) and returns the response.
    """
    client_id = http_request.client.host if http_request.client else "unknown"
    _check_rate_limit(client_id)

    try:
        # Route directly to the Supervisor - it decides which sub-agent to invoke
        response = await run_agent_async(supervisor_config, request.message)
        
        return ChatResponse(
            response=response,
            agent_name=supervisor_config.name
        )
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001 - final boundary, converts any failure into a 500
        raise HTTPException(status_code=500, detail=str(e))
