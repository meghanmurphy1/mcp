from fastmcp import FastMCP
from fastmcp.prompts.base import UserMessage, AssistantMessage
from typing import Union
from elasticsearch import Elasticsearch

mcp = FastMCP("ES MCP Server")

es_client = Elasticsearch(
            API_URL,
            api_key=API_KEY,
        )
Message = Union[UserMessage, AssistantMessage]

@mcp.resource("elasticsearch://indices")
def get_indices() -> list[dict]:
    try:
        indices = es_client.cat.indices(format='json')
        if indices:
            return indices
        else:
            return {"error": "No indices found"}
    except Exception as e:
        return {"error": f"Failed to retrive indices: {str(e)}"}

@mcp.resource("elasticsearch://indices/{index_name}")
def get_index_details(index_name: str) -> dict[str, any]:
    try:
        if not es_client.indices.exists(index=index_name):
            return {"error": f"Index '{index_name}' does not exist"}

        stats = es_client.indices.stats(index=index_name)     
        
        return {
            "name": index_name,
            "stats": stats,
        }
    except Exception as e:
        return {"error": f"Failed to retrieve index details: {str(e)}"}

@mcp.tool()
def search_index(index_name: str, query: str) -> dict[str, any]:
    try:
        if isinstance(query, str):
            query_body = {
                "query": {
                    "query_string": {
                        "query": query
                    }
                }
            }
        else:
            query_body = query
        results = es_client.search(index=index_name, body=query_body)
        return results
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

@mcp.prompt()
def analyze_salesforce_data(index: str) -> list[Message]:
    return [
        UserMessage(content="What can you tell me about this Salesforce data?"),
        UserMessage(content=index),
        AssistantMessage(content="I'll analyze this Salesforce data. Here are some initial observations: ")
    ]

if __name__ == "__main__":
    mcp.run()