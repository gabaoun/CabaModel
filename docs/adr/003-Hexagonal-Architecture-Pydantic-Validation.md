# ADR 003: Hexagonal Architecture & Strict Data Validation

## Status
Accepted

## Context
As the project moves from a sandbox to a production-grade codebase, we need to ensure scalability, maintainability, and data integrity. The previous flat structure coupled domain logic with infrastructure details (Google-ADK instances), making it harder to test and swap components.

## Decision
We implemented a **Hexagonal (Ports and Adapters) Architecture** and adopted **Pydantic v2** for all data schemas.

- **Domain Layer:** Contains Pydantic models (Entities) like `AgentConfig` which define *what* an agent is, independent of any framework.
- **Infrastructure Layer:** Contains the `AgentFactory` and `AgentService`, which handle the *how* (instantiating Google-ADK agents, handling retries with `tenacity`, and providing async wrappers).
- **Application Layer:** Contains specific agent instances (e.g., `C4B4Bot`, `TemporalAgent`) that combine domain configurations with infrastructure services.

## Rationale
- **Separation of Concerns:** Business rules (agent instructions and descriptions) are isolated from implementation details (ADK).
- **Strict Typing:** Eliminates `Any` and ensures runtime data validation, reducing "silent failures" common in LLM orchestration.
- **Resilience:** Centralizing agent creation in the infrastructure layer allows us to inject cross-cutting concerns like exponential backoff retries and logging globally.
- **Async-First:** Prepares the codebase for high-concurrency environments by wrapping sync tools and preparing for async I/O.

## Consequences
- **Positive:** Modular design allows for easier unit testing of configurations and swapping of LLM frameworks if needed. Higher reliability due to Pydantic validation.
- **Negative:** Slightly more boilerplate (more directories and files) compared to the original minimalist approach.
