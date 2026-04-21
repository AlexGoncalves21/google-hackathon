# System Overview

## Project Purpose

`google-hackathon` is a GitHub-focused agent repo that combines four ideas:

1. ADK for defining agents.
2. MCP for connecting to GitHub tools.
3. A2A for exposing a specialist agent to other agents.
4. Agent Engine for hosting a Gemini Enterprise-facing client agent.

## Main Components

### Root-Level README

- `README.md` explains the final split architecture and the role of each top-level directory.

### GitHub Specialist Service

- `github_agent/github_agent/agent.py`

This file hosts the specialized GitHub service. It is designed to:

- Load a GitHub personal access token from the environment.
- Connect to the GitHub MCP endpoint at
  `https://api.githubcopilot.com/mcp/`.
- Expose selected GitHub tools such as:
  - `search_repositories`
  - `search_issues`
  - `list_issues`
- Wrap those tools in an ADK agent.
- Publish the agent over A2A with an agent card.

Its instruction and A2A card metadata live in
`github_agent/github_agent/prompts/agent.yaml`.

### Gemini Enterprise-Facing Client Agent

- `client_agent/app/agent.py`
- `client_agent/app/agent_engine_app.py`

This is the more complete client path in the project.

`client_agent/app/agent.py` defines:

- A helper to resolve the main specialist base URL.
- A `RemoteA2aAgent` path for the remote specialist.
- A `root_agent` that delegates GitHub tasks to the specialist.
- An ADK `App`.

The user-facing instruction for this agent lives in
`client_agent/app/prompts/agent.yaml`.

`client_agent/app/agent_engine_app.py` wraps that ADK app in an Agent Engine
application with telemetry, logging, artifact storage, and feedback hooks.

### Supporting Docs

- `docs/knowledge_base/`

This folder contains mock retrieval-oriented documentation for the repo layout,
runtime expectations, and troubleshooting guidance.

## Request Flow

The intended runtime flow is:

1. A user interacts with the Gemini Enterprise-facing client agent.
2. The client agent receives a GitHub-oriented question.
3. The client agent delegates the task to the specialist GitHub agent.
4. The specialist agent uses MCP-backed GitHub tools.
5. The result is returned through A2A to the client.
6. The client agent presents the final answer to the user.

## Separation Of Responsibilities

The repository is intentionally split into two independent apps:

- `client_agent/` for the Gemini Enterprise-facing delegator.
- `github_agent/` for the MCP-backed GitHub specialist service.

This keeps the deployment targets and branch ownership clean.
