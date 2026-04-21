import os

from google.adk.tools import VertexAiSearchTool


def create_search_tool(data_store_path: str) -> VertexAiSearchTool:
    """Return a Vertex AI Search tool pointed at the project knowledge base.

    Args:
        data_store_path: Full resource path of the Vertex AI Search serving config.
            Format: projects/{project}/locations/{location}/collections/
                    default_collection/dataStores/{datastore_id}/
                    servingConfigs/default_search

    Returns:
        A VertexAiSearchTool bound to the given datastore, or a mock callable
        when INTEGRATION_TEST=TRUE.
    """
    if os.getenv("INTEGRATION_TEST") == "TRUE":

        def mock_search(query: str) -> str:
            return "Mock search result for testing purposes."

        return mock_search  # type: ignore[return-value]

    return VertexAiSearchTool(data_store_id=data_store_path)
