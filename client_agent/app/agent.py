import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

load_dotenv()


def _get_main_agent_base_url() -> str:
    """Resolve the remote main agent URL with backward-compatible env names."""
    return (
        os.getenv("MAIN_AGENT_BASE_URL")
        or os.getenv("GITHUB_AGENT_URL")
        or "http://localhost:8001"
    ).rstrip("/")


def _should_use_local_stub() -> bool:
    """Use a local stub until the real GitHub A2A service exists."""
    base_url = _get_main_agent_base_url().lower()
    return (
        os.getenv("USE_LOCAL_GITHUB_STUB", "").lower() in {"1", "true", "yes"}
        or "localhost" in base_url
        or "127.0.0.1" in base_url
    )


def _build_agent_card_url() -> str:
    base_url = _get_main_agent_base_url()
    from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH

    card_path = AGENT_CARD_WELL_KNOWN_PATH.lstrip("/")
    return f"{base_url}/{card_path}"


if _should_use_local_stub():
    main_agent = Agent(
        name="github_specialist_stub",
        model=Gemini(
            model=os.getenv("MODEL_NAME", "gemini-2.5-pro"),
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
        instruction=(
            "You are a temporary stand-in for the remote GitHub specialist agent. "
            "The live GitHub MCP/A2A backend is not connected yet. "
            "Help the user structure GitHub tasks, draft issue or PR review plans, "
            "identify what repository context is needed, and explain what the real "
            "specialist will do once available. "
            "Do not claim to have fetched live GitHub data or inspected real PRs."
        ),
    )
else:
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

    main_agent = RemoteA2aAgent(
        name="github_specialist",
        description=(
            "Remote GitHub specialist agent that handles GitHub tasks over A2A "
            "using the separately deployed MCP-backed service."
        ),
        agent_card=_build_agent_card_url(),
    )

root_agent = Agent(
    name="github_client_agent",
    model=Gemini(
        model=os.getenv("MODEL_NAME", "gemini-2.5-pro"),
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Gemini Enterprise-facing GitHub assistant. "
        "For repository exploration, issue triage, pull request analysis, codebase "
        "questions, and GitHub workflow questions, delegate to the specialist "
        "sub-agent. "
        "After delegating, return a concise and useful final answer to the user."
    ),
    sub_agents=[main_agent],
)

app = App(root_agent=root_agent, name="app")
