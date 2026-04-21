import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from .retrievers import create_search_tool

load_dotenv()

_datastore_path = os.environ["DATASTORE_PATH"]

search_tool = create_search_tool(_datastore_path)

root_agent = Agent(
    name="rag_agent",
    model=Gemini(
        model=os.getenv("MODEL_NAME", "gemini-2.5-pro"),
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a documentation assistant for the google-hackathon project "
        "(agent08_github_a2a_agent_mcp_server). "
        "Always use the search tool before answering any question about the "
        "project's architecture, components, configuration, file paths, execution "
        "flows, or known issues. "
        "After retrieving results, synthesise a clear answer and cite the source "
        "document(s) by filename."
    ),
    tools=[search_tool],
)

app = App(root_agent=root_agent, name="app")
