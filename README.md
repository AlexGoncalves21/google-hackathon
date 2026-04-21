# Google Hackathon Agents

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-34A853?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Vertex%20AI%20%26%20Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/)

This repo contains the hackathon delivery for a two-agent GitHub assistant: a Gemini Enterprise-facing client agent that runs on Vertex AI Agent Engine, and a GitHub specialist agent that runs as an A2A service on Cloud Run and talks to GitHub through MCP. Together they provide a single GitHub copilot experience while keeping the user-facing orchestration and the backend GitHub integration independently deployable.

This repo is intentionally split into two self-contained projects:

```text
google-hackathon/
├── client_agent/   # Gemini Enterprise-facing ADK agent on Agent Engine
├── github_agent/   # GitHub specialist A2A service on Cloud Run
└── docs/           # Supporting architecture and mock RAG docs
```

## Architecture

```text
Gemini Enterprise
  -> client_agent
  -> RemoteA2aAgent
  -> github_agent
  -> GitHub MCP
  -> GitHub
```

## Directory Guide

- `client_agent/`: The user-facing agent. It runs on Agent Engine and delegates GitHub work to the remote A2A service.
- `github_agent/`: The MCP-backed GitHub specialist. It serves an A2A agent card and handles GitHub retrieval tasks.
- `docs/knowledge_base/`: Secondary reference material and mock retrieval docs for the project.

Each directory has its own:

- `Makefile`
- `pyproject.toml`
- environment file template
- deployment workflow

That means each agent can be worked on, deployed, and reviewed independently.
