# Execution Flows

## Local Specialist Service Flow

The intended local specialist flow is:

1. Create a `.env` file in the project root.
2. Provide `GITHUB_PERSONAL_ACCESS_TOKEN`.
3. Install dependencies.
4. Run the GitHub specialist service with the project `Makefile`.
5. Verify the agent card at `/.well-known/agent-card.json`.

The main README describes this as the server-side GitHub agent flow.

## Delegation Flow

The conceptual delegation flow in this repository is:

1. A client-facing agent receives a GitHub question.
2. The client-facing agent identifies that the task belongs to the GitHub
   specialist.
3. The client agent calls the specialist through A2A.
4. The specialist queries GitHub through MCP tools.
5. The client agent returns a polished answer.

## Current Practical Flow

There are two practical client paths in the repository:

### Path A: Root-Level Delegating Client

- file: `agent.py`
- state: incomplete

This file is the simplest planned delegator, but it still has TODO markers and
is not the best reference for an end-to-end runnable flow.

### Path B: Nested Gemini Enterprise Client

- file: `client_agent/app/agent.py`
- state: more complete

This path supports two modes:

- Stub mode for local development when the real specialist is unavailable.
- Remote A2A mode when a real specialist agent card URL exists.

This makes `client_agent/` the most useful reference for a runnable client.

## Stub Mode Flow

When stub mode is active, `client_agent/app/agent.py` creates a local ADK agent
named `github_specialist_stub`.

The stub does not claim to fetch live GitHub data. Instead it:

- helps structure GitHub tasks
- drafts issue and PR review plans
- explains what repository context is needed
- describes what the real specialist will do once connected

This is useful for UI, prompt, and deployment testing before the MCP backend is
fully working.

## Remote Specialist Flow

When stub mode is off, the client uses `RemoteA2aAgent` and points it at the
specialist card URL derived from `MAIN_AGENT_BASE_URL`.

That means the expected remote sequence is:

1. Start or deploy the specialist service.
2. Expose the A2A card URL.
3. Configure `MAIN_AGENT_BASE_URL`.
4. Start or deploy the nested client agent.
5. Let the client delegate GitHub questions to the specialist.

## Agent Engine Flow

The nested client project's `client_agent/app/agent_engine_app.py` wraps the
ADK app in `AgentEngineApp`, which:

- calls `vertexai.init()`
- sets up telemetry
- configures logging
- configures artifact storage
- exposes a `register_feedback` operation

This file represents the Agent Engine deployment entry point for the nested
client agent.

## Gemini Enterprise Flow

The intended Gemini Enterprise path is:

1. Deploy the client-facing agent to Agent Engine.
2. Register that deployed agent with Gemini Enterprise.
3. Let Gemini Enterprise users interact with the client agent.
4. Let the client delegate GitHub-specific work to the specialist agent.

The nested client project README explicitly says:

- `make deploy`
- `make register-gemini-enterprise`

This makes the `client_agent/` project the strongest reference for the Gemini
Enterprise-facing workflow.
