install:
	pip install -r requirements.txt
	uv run fastmcp install --with fastmcp --with elasticsearch elasticsearch_mcp.py

run:
	python3 elasticsearch_mcp.py