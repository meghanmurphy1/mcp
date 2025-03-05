def format_search_response(hits: list[dict]) -> str:
    size = len(hits)
    """Format search results into a Markdown-friendly string, dynamically including all keys."""
    if not hits:
        return f"### {size} results"

    formatted_hits = []

    for hit in hits:
        hit_details = "\n".join(
            f"- **{key}:** {str(value)}" for key, value in hit.items()
        )
        formatted_hits.append(f"{hit_details}")

    return f"Here are {size} results:\n\n" + "\n\n".join(formatted_hits)
