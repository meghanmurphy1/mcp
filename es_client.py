import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

# Load environment variables
load_dotenv()

# Setup Elasticsearch client
api_key = os.getenv("API_KEY")
api_url = os.getenv("ES_URL")

es_client = Elasticsearch(
    api_url,
    api_key=api_key,
)


def get_indices() -> list[dict]:
    """List all available Elasticsearch indices."""
    try:
        indices = es_client.cat.indices(format="json")
        index_names = (
            ",".join(
                [
                    index["index"]
                    for index in indices
                    if not index["index"].startswith(".")
                ]
            )
            if indices
            else "No indices found"
        )
        return index_names
    except Exception as e:
        return {"error": f"Failed to retrieve indices: {str(e)}"}


def get_index_details(index_name: str) -> dict[str, any]:
    """Retrieve details of a specific Elasticsearch index."""
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


def search_index(index_name: str, query: str) -> dict[str, any]:
    """Perform a search query on an Elasticsearch index."""
    try:
        query_body = (
            {"query": {"query_string": {"query": query}}}
            if isinstance(query, str)
            else query
        )

        results = es_client.search(index=index_name, body=query_body)
        return results
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


def semantic_search(index_name: str, field: str, query: str) -> dict[str, any]:
    """Perform a semantic search on an Elasticsearch index."""
    try:
        query_body = (
            {"query": {"semantic": {"field": field, "query": query}}}
            if isinstance(query, str)
            else query
        )

        results = es_client.search(index=index_name, body=query_body)
        return results
    except Exception as e:
        return {"error": f"Semantic Search failed: {str(e)}"}


def search_crawler_resource(
    index_name: str, query: str, size: int = 5
) -> dict[str, any]:
    """Perform a search query on Elasticsearch Index with crawler resource."""
    try:
        query_body = (
            {
                "query": {
                    "semantic": {"query": query, "field": "semantic_body_content"}
                },
                "_source": [
                    "title",
                    "url",
                    "semantic_body_content.inference.chunks.text",
                ],
                "size": size,
            }
            if isinstance(query, str)
            else query
        )

        results = es_client.search(index=index_name, body=query_body)

        # Extract relevant data, selecting up to the top 3 chunks
        hits = []
        for hit in results.get("hits", {}).get("hits", []):
            source = hit["_source"]
            chunks = (
                source.get("semantic_body_content", {})
                .get("inference", {})
                .get("chunks", [])
            )

            # Extract up to 3 chunks
            top_chunks = [chunk.get("text", "") for chunk in chunks[:3]]

            hits.append(
                {
                    "title": source.get("title", "Untitled"),
                    "url": source.get("url", "#"),
                    "content": top_chunks,  # List of up to 3 chunk texts
                }
            )

        return hits

    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


def is_elasticsearch_configured() -> str:
    """Check if Elasticsearch instance is reachable."""
    try:
        return es_client.health_report().get("status", "unknown")
    except Exception as e:
        return f"Error: {str(e)}"
