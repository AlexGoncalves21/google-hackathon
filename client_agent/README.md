# Client Agent

This folder contains the Gemini Enterprise-facing client agent for the GitHub hackathon project.

It is intentionally separate from the existing `github_agent/` implementation so the `client-agent`
branch can evolve independently without creating merge conflicts with the MCP/A2A branch.

## What This Agent Does

- Runs as a standard ADK agent on Agent Engine.
- Delegates GitHub questions to the main remote agent over A2A.
- Presents the answer back to Gemini Enterprise users as a single polished response.

## Architecture

```text
Gemini Enterprise
  -> Agent Engine
  -> client_agent/app/agent.py
  -> RemoteA2aAgent
  -> MAIN_AGENT_BASE_URL + /.well-known/agent-card.json
```

## Files

```text
client_agent/
├── app/
│   ├── agent.py
│   ├── agent_engine_app.py
│   └── app_utils/
│       ├── deploy.py
│       ├── telemetry.py
│       └── typing.py
├── .env.example
├── Makefile
└── pyproject.toml
```

## Environment

Copy `.env.example` to `.env` and fill in the client-agent project values later from your console session.

Important values:

- `MAIN_AGENT_BASE_URL`: Base URL of the deployed main A2A agent.
- `GITHUB_AGENT_URL`: Legacy alias also supported by the client code.
- `USE_LOCAL_GITHUB_STUB`: When `true`, the client uses a local stand-in specialist
  instead of calling the real remote GitHub agent.
- `GOOGLE_CLOUD_PROJECT`: Project for the client agent deployment.
- `GOOGLE_CLOUD_LOCATION`: Region for Agent Engine deployment.

## Local Workflow

```bash
cp .env.example .env
make install
make playground
```

In ADK Web, select the `app` folder.

## Deploy

```bash
make deploy
make register-gemini-enterprise
```

The `register-gemini-enterprise` step should be run while authenticated with the Google account intended for the client agent.
