# CabaModel: Gemini-Native Agent Architecture

<p align="left">
  <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Powered_by-Gemini-blue?style=for-the-badge&logo=google-gemini" />
</p>

A modular, production-grade AI Agent orchestration framework engineered using the **Google ADK (Agent Development Kit)**, **FastAPI**, **Pydantic v2**, and asynchronous event-driven execution.

This microservice provides a resilient agent orchestration interface featuring clean architectural decoupling, structured schema validation, and Multi-Agent patterns.

## 🚀 System Architecture & Features

- **Multi-Agent & Tool Calling:** Implements advanced agentic loops capable of delegating tasks and autonomously invoking tools using the latest ADK Runner pattern.
- **RESTful Orchestration:** Powered by FastAPI with an interactive Swagger UI for real-time testing, acting as a scalable backend for LLM interactions.
- **Hexagonal Design (Ports & Adapters):** Strict separation between **Domain**, **Application**, and **Infrastructure** layers, ensuring horizontal scalability.
- **Non-blocking Execution:** Full `asyncio` implementation to handle high-throughput I/O and event streams efficiently.
- **Data Integrity:** Pydantic v2 ensures strict typing and data compliance across all agent-tool LLM payloads.

## 🐳 Quick Start (Docker)
The service is containerized for seamless reproduction.

```bash
# Clone the repository
git clone https://github.com/gabaoun/CabaModel.git
cd CabaModel

# Boot the service via Docker Compose
docker-compose up -d --build
```

*The interactive API documentation will be available at http://localhost:8000/docs.*
