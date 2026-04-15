# CabaModel: Gemini-Native Agent Architecture

<p align="center">
  <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Powered_by-Gemini-blue?style=for-the-badge&logo=google-gemini" />
</p>

An advanced study on AI agent architecture using **Google ADK (Agent Development Kit)**, **FastAPI**, **Pydantic v2**, and asynchronous event-driven execution.

This project demonstrates a production-ready transition from simple scripts to a resilient, microservice-oriented agent orchestration.

## 🚀 Key Features

- **Google ADK Runner Architecture:** Implements the latest `Runner` pattern for managing agentic loops, event streams, and tool calls.
- **RESTful Interface:** Powered by FastAPI with an interactive Swagger UI for real-time testing and orchestration.
- **Hexagonal Design:** Clear separation between **Domain**, **Application**, and **Infrastructure** layers, ensuring scalability and testability.
- **Asynchronous & Non-blocking:** Full `asyncio` implementation to handle I/O and event streams without blocking the main event loop.
- **Strict Validation:** Pydantic v2 ensures data integrity across all agent-tool interactions.
- **Resilience:** Built-in retry logic with exponential backoff for robust API communication.

## 📂 Project Structure

- `src/cabamodel/domain/` – Core models and Pydantic schemas.
- `src/cabamodel/infrastructure/` – API implementation, ADK Adapters, and Tools.
- `src/cabamodel/application/` – Specialized agent definitions (e.g., temporal_agent, c4b4_bot).
- `main.py` – Entry point for the FastAPI server and agent initialization.

## ⚙️ How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/CabaModel.git
   ```

2. **Setup Environment:**
   Create a `.env` file based on `.env.example` and add your `GOOGLE_API_KEY`.

3. **Install Dependencies:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -e .
   ```

4. **Run the API:**
   ```bash
   python main.py
   ```

5. **Interact:**
   Open your browser at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to access the interactive Swagger documentation.

## 🛠️ Programmatic Usage Example

```python
from src.cabamodel.application.temporal_agent import root_agent
from src.cabamodel.infrastructure.agent_service import run_agent_async

async def main():
    # Execute the agent using the ADK Runner-based service
    response = await run_agent_async(root_agent, "What time is it now?")
    print(f"Agent Response: {response}")

# This pattern handles tool-calling loops and event streams automatically
```

## ⚖️ License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.
