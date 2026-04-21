import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

load_dotenv()

PROMPTS_PATH = Path(__file__).resolve().parent / "prompts" / "agent.yaml"


def _load_agent_config() -> dict[str, Any]:
    with PROMPTS_PATH.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


AGENT_CONFIG = _load_agent_config()


def _get_main_agent_base_url() -> str:
    """Resolve the remote main agent URL with backward-compatible env names."""
    base_url = os.getenv("MAIN_AGENT_BASE_URL") or os.getenv("GITHUB_AGENT_URL")
    if not base_url:
        raise RuntimeError(
            "Set MAIN_AGENT_BASE_URL or GITHUB_AGENT_URL for the client agent."
        )
    return base_url.rstrip("/")


def _build_agent_card_url() -> str:
    base_url = _get_main_agent_base_url()

    card_path = AGENT_CARD_WELL_KNOWN_PATH.lstrip("/")
    return f"{base_url}/{card_path}"


main_agent = RemoteA2aAgent(
    name=AGENT_CONFIG["remote_agent"]["name"],
    description=AGENT_CONFIG["remote_agent"]["description"],
    agent_card=_build_agent_card_url(),
)

root_agent = Agent(
    name=AGENT_CONFIG["root_agent"]["name"],
    model=Gemini(
        model=os.getenv("MODEL_NAME", "gemini-2.5-pro"),
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=AGENT_CONFIG["root_agent"]["instruction"],
    sub_agents=[main_agent],
)

app = App(root_agent=root_agent, name=AGENT_CONFIG["app"]["name"])
