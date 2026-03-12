# ADR 001: Minimalist Agent Architecture (Google-ADK)

## Status
Accepted

## Context
We need a framework to build autonomous agents that are optimized for the Gemini ecosystem, requiring minimal boilerplate and direct access to native tool-calling features. Traditional frameworks like LangChain or AutoGen can introduce significant overhead and complex state management.

## Decision
We decided to adopt the **Google Agent Development Kit (ADK)** for this project.

## Rationale
- **Performance:** ADK is designed for low-latency interactions with Gemini models.
- **Simplicity:** It provides a clean, declarative API for defining agents, instructions, and tools without unnecessary abstractions.
- **Gemini-Native:** Built by Google, it ensures first-class support for Gemini features (like JSON mode and Function Calling) as they evolve.
- **State Management:** Simple built-in session handling (e.g., `session.db`) is sufficient for our current sandbox requirements.

## Consequences
- **Positive:** extremely fast development cycles and minimal code footprint.
- **Negative:** Access to high-level "pre-built" chains common in LangChain is limited, requiring manual implementation of complex reasoning flows.
