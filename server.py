from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import UserMessage, AssistantMessage
from typing import Union
from utils import format_search_response
import es_client

# Initialize FastMCP server for Elasticsearch interactions
mcp = FastMCP("Elastic Demo MCP Server", dependencies=["elasticsearch"])

# Define message type for prompts
Message = Union[UserMessage, AssistantMessage]

# ------------------- MCP Resources (Data Retrieval Endpoints) -------------------


@mcp.resource(
    "elasticsearch://indices",
    name="list_elasticsearch_indices",
    description="Retrieve all Elasticsearch indices.",
)
def fetch_indices() -> list[dict]:
    """Retrieve all Elasticsearch indices.This allows users to get a list of indices from Elasticsearch via MCP."""
    return es_client.get_indices()


@mcp.resource(
    "elasticsearch://indices/{index}",
    name="index_details",
    description="Retrieve details of a specific Elasticsearch index.",
)
def fetch_index_details(index: str) -> dict[str, any]:
    """Retrieve details of a specific Elasticsearch index. This provides metadata and statistics about a given index."""
    return es_client.get_index_details(index)


@mcp.resource(
    "docs://search/{query}",
    name="elasticsearch_documentation",
    description="Perform a semantic search across Elastic documentation for a given query.",
)
def search_elastic_documentation(query: str) -> dict[str, any]:
    """
    Perform a semantic search across Elastic documentation for a given query. The
    data is using sparse embeddings for semantic search so optimzie the query for it.
    You will get titles and links to the documentation pages that might be helpful for user to understand the concepts.
    """
    return es_client.search_crawler_resource("search-elastic-docs", query)


@mcp.resource(
    "search_labs://search/{query}",
    name="elasticsearch_labs_blogs",
    description="Perform a semantic search across Elastic search labs blogs for a given query.",
)
def search_elastic_search_labs_blogs(query: str) -> dict[str, any]:
    """
    Perform a semantic search across Elastic search labs blogs for a given query. The
    data is using sparse embeddings for semantic search so optimzie the query for it.
    You will get titles and links to the blog pages that might be helpful for user to understand the concepts.
    """
    return es_client.search_crawler_resource("search-blog-search-labs", query)


# ------------------- MCP Tools (Actions Users Can Trigger) -------------------


@mcp.tool(
    name="search_elasticsearch_documentation",
    description="Perform a semantic search across Elastic documentation for a given query.",
)
def search_elastic_documentation(query: str) -> str:
    """
    Perform a semantic search across Elastic documentation for a given query. The
    data is using sparse embeddings for semantic search so optimzie the query for it.
    You will get titles and links to the documentation pages that might be helpful for user to understand the concepts.
    """
    return format_search_response(
        es_client.search_crawler_resource("search-elastic-docs", query)
    )


@mcp.tool(
    name="search_elasticsearch_labs_blogs",
    description="Perform a semantic search across Elastic search labs blogs for a given query.",
)
def search_elastic_search_labs_blogs(query: str) -> str:
    """
    Perform a semantic search across Elastic search labs blogs for a given query. The
    data is using sparse embeddings for semantic search so optimzie the query for it.
    You will get titles and links to the blog pages that might be helpful for user to understand the concepts.
    """
    return format_search_response(
        es_client.search_crawler_resource("search-blog-search-labs", query)
    )


# ------------------- MCP Prompts (Predefined Interactions with the Assistant) -------------------


@mcp.prompt()
def is_elasticsearch_configured() -> list[Message]:
    """
    Check if the Elasticsearch instance is reachable.

    This sends a simulated conversation to determine if Elasticsearch is online
    and provides status feedback to the user.
    """
    status = es_client.is_elasticsearch_configured()

    if "Error" in status:
        return [
            UserMessage(content="Can you reach my Elasticsearch instance?"),
            AssistantMessage(
                content=f"I tried connecting, but encountered an error: {status}"
            ),
        ]
    else:
        return [
            UserMessage(content="Can you reach my Elasticsearch instance?"),
            AssistantMessage(
                content=f"Connected successfully! Elasticsearch status: {status}"
            ),
        ]


@mcp.prompt()
def analyze_salesforce_data(index: str) -> list[Message]:
    """
    Request analysis of Salesforce data stored in Elasticsearch.

    This prompt prepares a response where the AI can analyze the given index
    containing Salesforce data and provide insights.
    """
    return [
        UserMessage(content="What can you tell me about this Salesforce data?"),
        UserMessage(content=index),
        AssistantMessage(
            content="I'll analyze this Salesforce data. Here are some initial observations:"
        ),
    ]


# ------------------- MCP Server Execution -------------------

if __name__ == "__main__":
    print(f"MCP server '{mcp.name}' is running...")
    mcp.run()
