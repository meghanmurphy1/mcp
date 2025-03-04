from fastmcp import FastMCP
from fastmcp.prompts.base import UserMessage, AssistantMessage
from typing import Union
import es_client

# Initialize FastMCP server for Elasticsearch interactions
mcp = FastMCP("Elastic Demo MCP Server", dependencies=["elasticsearch"])

# Define message type for prompts
Message = Union[UserMessage, AssistantMessage]

# ------------------- MCP Resources (Data Retrieval Endpoints) -------------------


@mcp.resource(
    uri="elasticsearch://indices",
    name="Elasticsearch Indices",
    description="Retrieve all Elasticsearch indices.",
)
def fetch_indices() -> list[dict]:
    """Retrieve all Elasticsearch indices.This allows users to get a list of indices from Elasticsearch via MCP."""
    return es_client.get_indices()


@mcp.resource(
    uri="elasticsearch://indices/{index}",
    name="Index Details",
    description="Retrieve details of a specific Elasticsearch index.",
)
def fetch_index_details(index: str) -> dict[str, any]:
    """Retrieve details of a specific Elasticsearch index. This provides metadata and statistics about a given index."""
    return es_client.get_index_details(index)


# ------------------- MCP Tools (Actions Users Can Trigger) -------------------


#  IMO the search tools (semantic search) should be actually resources
# 
# TODO: define actual tools

@mcp.tool()
def search_elastic_documentation(query: str) -> dict[str, any]:
    """
    Perform a semantic search across Elastic documentation for a given query. The
    data is using sparse embeddings for semantic search so optimzie the query for it.
    You will get titles and links to the documentation pages that might be helpful for user to understand the concepts.
    """
    return es_client.search_crawler_resource("search-elastic-docs", query)

@mcp.tool()
def search_elastic_search_labs_blogs(query: str) -> dict[str, any]:
    """
    Perform a semantic search across Elastic search labs blogs for a given query. The
    data is using sparse embeddings for semantic search so optimzie the query for it.
    You will get titles and links to the blog pages that might be helpful for user to understand the concepts.
    """
    return es_client.search_crawler_resource("search-blog-search-labs", query)


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


# ------------------- DEBUG: Print Registered Resources -------------------

def debug_registered_resources():
    """Print all registered MCP resources for debugging."""
    print("\n🔍 Registered MCP Resources:")
    for resource in mcp._resource_manager.list_resources():
        print(f" - {resource.name}")
    for resource in mcp._resource_manager.list_templates():
        print(f" - {resource.name}")

# ------------------- DEBUG: Print Registered Tools -------------------

def debug_registered_tools():
    """Print all registered MCP tools for debugging."""
    print("\n🔍 Registered MCP Tools:")
    for tool in mcp._tool_manager.list_tools():
        print(f" - {tool.name}")

# ------------------- DEBUG: Print Registered Prompts -------------------

def debug_registered_prompts():
    """Print all registered MCP prompts for debugging."""
    print("\n🔍 Registered MCP Prompts:")
    for prompt in mcp._prompt_manager.list_prompts():
        print(f" - {prompt.name}")


# ------------------- MCP Server Execution -------------------

if __name__ == "__main__":
    debug_registered_resources()
    debug_registered_prompts()
    debug_registered_tools()
    print(f"\n MCP server '{mcp.name}' is running...")
    mcp.run()
