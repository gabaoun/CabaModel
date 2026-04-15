from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.cabamodel.application.temporal_agent import root_agent as temporal_agent
from src.cabamodel.application.c4b4_bot import root_agent as c4b4_agent
from src.cabamodel.infrastructure.agent_service import run_agent_async

app = FastAPI(
    title="CabaModel API",
    description="REST interface for Gemini-Native agent orchestration",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str
    agent_type: str = "temporal"  # "temporal" or "c4b4"

class ChatResponse(BaseModel):
    response: str
    agent_name: str

@app.get("/")
async def root():
    return {"message": "CabaModel API is running", "docs": "/docs"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Sends a message to the selected agent and returns the response.
    """
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
