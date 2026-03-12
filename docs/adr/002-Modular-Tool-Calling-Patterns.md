# ADR 002: Modular Tool-Calling Patterns

## Status
Accepted

## Context
As the number of agent capabilities grows, a monolithic agent becomes difficult to manage, test, and optimize. Different tasks (e.g., technical support vs. real-time data retrieval) require different instruction sets and tool subsets.

## Decision
We adopted a **Modular Sandbox** approach, where each specialized capability is encapsulated in its own directory and `Agent` instance.

## Rationale
- **Isolation:** Changes to the `Temporal-Tool-Agent` do not impact the `C4B4-Assistant`.
- **Security:** Agents only have access to the specific tools defined in their scope (Principle of Least Privilege).
- **Instruction Precision:** Smaller instruction sets reduce the risk of "instruction drift" and improve model follow-through.

## Consequences
- **Positive:** High maintainability and easy to scale by adding new modules to the `src/` directory.
- **Negative:** Requires a more robust cross-agent orchestration layer if we want them to collaborate in a single workflow in the future.
