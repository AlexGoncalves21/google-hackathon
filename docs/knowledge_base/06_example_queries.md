# Example Queries

This file contains example natural-language questions that a RAG system should
be able to answer from the mock corpus.

## Architecture Questions

- What is the difference between `client_agent/` and `github_agent/`?
- Which file is the GitHub specialist service?
- Which file wraps the client agent for Agent Engine deployment?
- Does this project use MCP, A2A, or both?
- What is the role of `github_agent/github_agent/agent.py`?

## Configuration Questions

- Which environment variables are required at the project root?
- What does `USE_LOCAL_GITHUB_STUB` do?
- What is `MAIN_AGENT_BASE_URL` used for?
- Which port is used by the local GitHub specialist?
- Where is the GitHub personal access token expected?

## Workflow Questions

- How is a GitHub question supposed to flow through the system?
- How does the client delegate work to the specialist?
- What is the intended Gemini Enterprise deployment flow?
- Which project should be deployed to Agent Engine?
- How do I verify the specialist agent card locally?

## Gap Analysis Questions

- Which parts of the GitHub specialist are still not implemented?
- Does the current GitHub specialist support PR review yet?
- Why might the system return a stubbed answer instead of live GitHub data?
- Which part of the repository is the most complete implementation?

## File Discovery Questions

- Where is the main README for this project?
- Where is the client agent README?
- Where is the pyproject for the main service?
- Where is the pyproject for the Gemini Enterprise-facing client?
- Which directory contains mock RAG documentation?
