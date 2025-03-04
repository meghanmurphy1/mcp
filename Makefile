VENV = .venv
PYTHON = $(VENV)/bin/python

$(VENV)/bin/activate: pyproject.toml
	uv venv $(VENV)

run: $(VENV)/bin/activate
	uv run $(PYTHON) server.py

add-claude-config: $(VENV)/bin/activate
	uv run fastmcp install server.py

format:
	uv pip install black
	$(VENV)/bin/black .

clean:
	rm -rf $(VENV) __pycache__

inspect:
	$(VENV)/bin/mcp dev server.py
