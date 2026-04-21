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
│   ├── prompts/
│   │   └── agent.yaml
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
- `DATASTORE_PATH`: Optional Vertex AI Search serving config used for retrieval grounding.
- `GOOGLE_CLOUD_PROJECT`: Project for the client agent deployment.
- `GOOGLE_CLOUD_LOCATION`: Region for Agent Engine deployment.

When `MAIN_AGENT_BASE_URL` points at a private Cloud Run service, the client now
supports service-to-service auth automatically. At deployment time it defaults
to sending a Google-signed ID token for non-local URLs, using the Cloud Run base
URL as the audience unless `MAIN_AGENT_AUDIENCE` is set.

The client no longer contains a local mock GitHub agent. For local development,
point `MAIN_AGENT_BASE_URL` at a real local or deployed `github_agent` service.

## Local Workflow

```bash
cp .env.example .env
make install
make playground
```

In ADK Web, select the `app` folder.

For local development against a private deployed `github_agent`, export a
short-lived identity token and point the audience at the Cloud Run URL:

```bash
export MAIN_AGENT_BASE_URL="https://your-private-service-xxxxx-uc.a.run.app"
export MAIN_AGENT_AUTH_TOKEN="$(gcloud auth print-identity-token --audiences=${MAIN_AGENT_BASE_URL})"
make playground
```

## Deploy

```bash
make deploy
make register-gemini-enterprise
```

Before invoking the client from Gemini Enterprise, make sure the private
`github_agent` Cloud Run service grants `roles/run.invoker` to the Agent Engine
runtime service account used by this client.

The `register-gemini-enterprise` step should be run while authenticated with the Google account intended for the client agent.
