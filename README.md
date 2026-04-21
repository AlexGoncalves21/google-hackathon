# Google Hackathon Agents

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
