# Known Gaps and Troubleshooting

## Current Gaps

### GitHub Tool Coverage Is Still Narrow

The GitHub specialist currently focuses on:

- `search_repositories`
- `search_issues`
- `list_issues`

That means broader use cases such as pull request review, code diff analysis,
or write-back review comments still need additional MCP tools and prompt work.

### The End-To-End Flow Depends On Two Deployments

For live behavior, the system needs both:

- `github_agent/` deployed to Cloud Run
- `client_agent/` deployed to Agent Engine

If either deployment URL is wrong or stale, the user-facing agent can fall back
to generic or stubbed responses.

## What Is Most Complete Right Now

Both top-level apps are independently runnable:

- `client_agent/` is the Gemini Enterprise-facing delegator.
- `github_agent/` is the GitHub MCP-backed specialist.

The client still has the gentler fallback behavior, while the GitHub service is
the component that actually talks to GitHub through MCP.

## Common Questions and Answers

### Why does the client answer with a stub instead of calling GitHub?

The client uses a local stub when:

- `USE_LOCAL_GITHUB_STUB=true`
- the base URL points to localhost
- the base URL points to `127.0.0.1`

In that case the client intentionally avoids claiming that it has queried live
GitHub data.

### Why does the GitHub specialist fail on startup?

The main reason is a missing `GITHUB_PERSONAL_ACCESS_TOKEN`. The specialist
service explicitly raises an error when that token is absent.

### Which files should a developer read first?

Suggested order:

1. `README.md`
2. `github_agent/GITHUB_AGENT_GUIDE.md`
3. `client_agent/README.md`
4. `client_agent/app/agent.py`
5. `client_agent/app/agent_engine_app.py`
6. `github_agent/github_agent/agent.py`

## Troubleshooting Notes

### Symptom: No real GitHub data is returned

Possible causes:

- The client is in local stub mode.
- The specialist service is not deployed or not running.
- The A2A agent card URL is wrong.
- The GitHub toolset does not yet cover the question being asked.

### Symptom: Delegation never reaches the specialist

Possible causes:

- `MAIN_AGENT_BASE_URL` is missing.
- `GITHUB_AGENT_URL` fallback is wrong.
- The specialist card URL is unavailable.
- The remote specialist does not expose a valid A2A card.

### Symptom: Agent Engine deployment works but GitHub answers are generic

Possible causes:

- The client deployed successfully, but it is still using the stub.
- The remote specialist URL still points to localhost.
- The question requires tools that the current GitHub specialist does not yet expose.

## Retrieval-Safe Summary

If a RAG agent is asked which parts of the repository are deployment-ready, the
best answer is:

`client_agent/` and `github_agent/` are both deployment-ready projects, but the
GitHub specialist is currently optimized for repository and issue retrieval
rather than full PR-review coverage.
