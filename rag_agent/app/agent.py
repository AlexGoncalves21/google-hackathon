import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from .retriever import KnowledgeBaseRetriever

load_dotenv()

_retriever = KnowledgeBaseRetriever()


def search_knowledge_base(query: str) -> str:
    """Search the project knowledge base for documentation relevant to the query.

    Use this tool to answer questions about the project's architecture, file
    structure, configuration, execution flows, known issues, and components.

    Args:
        query: Natural-language question or topic to search for.

    Returns:
        Relevant documentation excerpts with source file references.
    """
    results = _retriever.search(query, top_k=5)
    if not results:
        return "No relevant documentation found for this query."

    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"<Document {i} source='{r['source']}' score={r['score']}>\n"
            f"{r['text']}\n"
            f"</Document {i}>"
        )
    return "\n\n".join(parts)


root_agent = Agent(
    name="rag_agent",
    model=Gemini(
        model=os.getenv("MODEL_NAME", "gemini-2.5-pro"),
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a documentation assistant for the google-hackathon project "
        "(agent08_github_a2a_agent_mcp_server). "
        "Always call search_knowledge_base before answering any question about the "
        "project's architecture, components, configuration, file paths, execution "
        "flows, or known issues. "
        "After retrieving results, synthesise a clear answer and cite the source "
        "document(s) by filename."
    ),
    tools=[search_knowledge_base],
)

app = App(root_agent=root_agent, name="app")
