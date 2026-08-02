import os
import time
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.cabamodel.application.c4b4_bot import root_agent as c4b4_agent
from src.cabamodel.application.temporal_agent import root_agent as temporal_agent
from src.cabamodel.infrastructure.agent_service import run_agent_async

app = FastAPI(
    title="CabaModel API",
    description="REST interface for Gemini-Native agent orchestration",
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
    agent_type: str = "temporal"  # "temporal" or "c4b4"

class ChatResponse(BaseModel):
    response: str
    agent_name: str

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "CabaModel API is running", "docs": "/docs", "ui": "/ui"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
    """
    Sends a message to the selected agent and returns the response.
    """
    client_id = http_request.client.host if http_request.client else "unknown"
    _check_rate_limit(client_id)

    try:
        if request.agent_type == "temporal":
            selected_agent = temporal_agent
        elif request.agent_type == "c4b4":
            selected_agent = c4b4_agent
        else:
            raise HTTPException(status_code=400, detail="Agent type invalid. Use 'temporal' or 'c4b4'.")

        # Use the recommended async runner to handle events and errors properly
        response = await run_agent_async(selected_agent, request.message)
        
        return ChatResponse(
            response=response,
            agent_name=selected_agent.name
        )
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001 - final boundary, converts any failure into a 500
        raise HTTPException(status_code=500, detail=str(e))
