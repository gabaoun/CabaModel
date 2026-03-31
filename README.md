# CabaModel: Gemini-Native Agent Architecture

<p align="center">
  <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Powered_by-Gemini-blue?style=for-the-badge&logo=google-gemini" />
</p>

Study on AI agent architecture using **Google ADK**, **Pydantic v2**, and asynchronous execution.

This project was developed as part of my transition from game development to backend/AI engineering. The focus was to explore:

- **Modular organization:** Separation between domain, application, and infrastructure (hexagonal architecture) to facilitate testing and evolution.

- **Data validation:** Use of Pydantic v2 to define strict input and output contracts, reducing runtime errors.

- **Basic resilience:** Implementation of retry with exponential backoff (Tenacity) to handle temporary Gemini API failures.

- **Asynchronous execution:** Use of `asyncio` for non-blocking operations.

## Project Structure

- `src/cabamodel/domain/` – Models and contracts (Pydantic)
- `src/cabamodel/infrastructure/` – Adapters for the Gemini API and tools
- `src/cabamodel/application/` – Specific agents (e.g., temporal_agent)

## How to Run

1. Clone the repository
2. Configure your Gemini API key in the `.env` file (see `.env.example`)
3. Synchronize dependencies with `uv sync`

4. Run the example:

```python

import asyncio
from src.cabamodel.application.temporal_agent import root_agent

async def main():

response = root_agent.chat("What is the current time?")

print(response)

asyncio.run(main())

```

## ⚖️ License
Distributed under the Apache 2.0 License. See `LICENSE` for more information.
