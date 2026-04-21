# Copyright 2025 Google, LLC. This software is provided as-is, without
# warranty or representation for any use or purpose. Your use of it is
# subject to your agreement with Google.

# Licensed under the Apache License, Version 2.0 (the "License");

# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
from pathlib import Path
from typing import Any

import yaml
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
PROMPTS_PATH = Path(__file__).resolve().parent / "prompts" / "agent.yaml"


def _load_agent_config() -> dict[str, Any]:
    with PROMPTS_PATH.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


AGENT_CONFIG = _load_agent_config()

# --- Logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- GitHub Config ---
GITHUB_AGENT_URL = os.getenv("GITHUB_AGENT_URL", "http://localhost:8001").rstrip("/")
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()

SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

# --- MCP Config ---
MCP_URL = "https://api.githubcopilot.com/mcp/"
TOOLS = ["search_repositories", "search_issues", "list_issues"]

if not GITHUB_TOKEN:
    raise RuntimeError(
        "GITHUB_PERSONAL_ACCESS_TOKEN is required to start the GitHub A2A service."
    )

root_agent = Agent(
    name=AGENT_CONFIG["agent"]["name"],
    model=os.getenv("MODEL_NAME", "gemini-2.5-pro"),
    description=AGENT_CONFIG["agent"]["description"],
    instruction=AGENT_CONFIG["agent"]["instruction"],
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_URL,
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
            ),
            tool_filter=TOOLS,
        )
    ],
)

agent_card = AgentCard(
    name=AGENT_CONFIG["agent_card"]["name"],
    description=AGENT_CONFIG["agent_card"]["description"],
    url=GITHUB_AGENT_URL,
    version=AGENT_CONFIG["agent_card"]["version"],
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=SUPPORTED_CONTENT_TYPES,
    default_output_modes=SUPPORTED_CONTENT_TYPES,
    skills=[AgentSkill(**skill) for skill in AGENT_CONFIG["agent_card"]["skills"]],
)

a2a_app = to_a2a(root_agent, agent_card=agent_card)
