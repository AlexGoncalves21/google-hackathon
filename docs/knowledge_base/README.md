# Mock RAG Documentation Corpus

This directory contains mock documentation for the final hackathon repo rooted
at `google-hackathon/`.

The files in this folder are intended to be ingested into a datastore for a
RAG agent. They are written as short, topic-focused documents so retrieval can
find precise answers about architecture, files, configuration, workflows, and
known gaps.

## Corpus Contents

- `01_system_overview.md`: High-level architecture and component roles.
- `02_repo_map.md`: Relative path map for the main project files and folders.
- `03_runtime_configuration.md`: Environment variables, ports, models, and
  dependency expectations.
- `04_execution_flows.md`: Local development, delegation flow, deployment
  flow, and Gemini Enterprise flow.
- `05_known_gaps_and_troubleshooting.md`: Current TODOs, implementation gaps,
  and common troubleshooting guidance.
- `06_example_queries.md`: Example natural-language questions a RAG agent
  should be able to answer from this corpus.

## Scope

All paths in this documentation are relative to the root of `google-hackathon/`.

Examples:

- `README.md`
- `client_agent/app/agent.py`
- `github_agent/github_agent/agent.py`
- `github_agent/GITHUB_AGENT_GUIDE.md`

## Intended Use

This corpus is designed to help a retrieval system answer questions such as:

- What does `github_agent/github_agent/agent.py` do?
- Which file is the Gemini Enterprise-facing client?
- Which environment variables are required for local execution?
- Why does the client sometimes use a local stub instead of a remote A2A agent?
- What parts of the main GitHub MCP service are still incomplete?
