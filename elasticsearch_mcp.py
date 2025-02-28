import os
from fastmcp import FastMCP
from fastmcp.prompts.base import UserMessage, AssistantMessage
from typing import Union
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

mcp = FastMCP("ES MCP Server")
api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")

es_client = Elasticsearch(
            api_url,
            api_key=api_key,
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
    
@mcp.tool()
def semantic_search(index_name: str, field:str, query: str) -> dict[str, any]:
    try:
        if isinstance(query, str):
            query_body = {
                "query": {
                    "semantic": {
                        "field": field,
                        "query": query
                        }
                }
            }
        else:
            query_body = query
        results = es_client.search(index=index_name, body=query_body)
        return results
    except Exception as e:
        return {"error": f"Semantic Search failed: {str(e)}"}


@mcp.prompt()
def is_elasticsearch_configured() -> list[Message]:
    try:
        status = es_client.health_report()['status']
        return [
            UserMessage(content="Can you reach my Elasticsearch instance?"),
            AssistantMessage(content=f"Let me try connecting to your Elasticsearch instance... Connected! Status: {status}")
        ]
    except Exception as e:
        return [
            UserMessage(content="Can you reach my Elasticsearch instance?"),
            AssistantMessage(content=f"I tried connecting to your Elasticsearch instance, but encountered an error: {str(e)}")
        ]

@mcp.prompt()
def analyze_salesforce_data(index: str) -> list[Message]:
    return [
        UserMessage(content="What can you tell me about this Salesforce data?"),
        UserMessage(content=index),
        AssistantMessage(content="I'll analyze this Salesforce data. Here are some initial observations: ")
    ]

if __name__ == "__main__":
    print(f"MCP server '{mcp.name}' is running...")
    mcp.run()