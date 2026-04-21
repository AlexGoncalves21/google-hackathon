# GitHub Agent

This directory contains the GitHub specialist service for the hackathon project.
It is a standalone ADK + A2A application that connects to GitHub through MCP and
is deployed to Cloud Run.

The Gemini-facing client lives separately in `../client_agent`.

## Project Structure

```text
github_agent/
├── github_agent/            # A2A service package and MCP-backed agent logic
│   └── prompts/agent.yaml   # Prompt and agent-card config
├── deployment/              # Optional Terraform and infra helpers
├── notebooks/               # Prototyping and evaluation notebooks
├── tests/                   # Unit, integration, and load tests
├── .env.example             # Local environment template
├── Dockerfile               # Cloud Run container build
├── Makefile                 # Local run, test, and deploy commands
└── pyproject.toml           # Python dependencies
```

## What This Agent Does

- Connects to the GitHub MCP endpoint with a GitHub personal access token.
- Exposes a public A2A agent card.
- Handles GitHub retrieval tasks for the separate `client_agent`.

## Quick Start

```bash
cp .env.example .env
make install
make run
```

In another terminal, verify the agent card:

```bash
make smoke-card
```

## Commands

| Command | Description |
| ------- | ----------- |
| `make install` | Install Python dependencies with `uv` |
| `make run` | Start the local A2A service on port `8001` |
| `make smoke-card` | Fetch the local agent card |
| `make playground` | Open ADK web for local debugging |
| `make lint` | Run linting and static analysis |
| `make test` | Run unit and integration tests |
| `make deploy` | Build and deploy the service to Cloud Run |
| `make inspector` | Open the A2A inspector UI |
| `make setup-dev-env` | Apply optional Terraform dev resources |

## Deployment

Set your active GCP project and export a GitHub token before deploying:

```bash
gcloud config set project <your-project-id>
export GITHUB_PERSONAL_ACCESS_TOKEN=<your-token>
make deploy
```

`make deploy` stores the GitHub token in Secret Manager and mounts it into Cloud Run
as a secret-backed environment variable.

## End-To-End Setup

This service is only one half of the hackathon architecture:

1. Deploy `github_agent` to Cloud Run.
2. Put the public service URL into `client_agent/.env`.
3. Deploy `client_agent` to Agent Engine.
4. Register `client_agent` in Gemini Enterprise.
