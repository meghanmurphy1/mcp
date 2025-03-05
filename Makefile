VENV = .venv
PYTHON = $(VENV)/bin/python
NODE_VERSION := $(shell cat .nvmrc)
CURRENT_NODE := $(shell node -v 2>/dev/null || echo "none")

$(VENV)/bin/activate: pyproject.toml
	uv venv $(VENV)

run: $(VENV)/bin/activate
	uv run $(PYTHON) server.py

add-claude-config: $(VENV)/bin/activate
	uv run mcp install server.py --with elasticsearch

format:
	uv pip install black
	$(VENV)/bin/black .

clean:
	rm -rf $(VENV) __pycache__

dev: check-nvm
	uv run mcp dev server.py

check-nvm:
	@if [ "$(CURRENT_NODE)" = "none" ]; then \
		echo "Error: Node.js is not installed or 'nvm' is not available. Please install nvm and run 'nvm use'"; \
		exit 1; \
	fi
	@if [ "$(CURRENT_NODE)" != "$(NODE_VERSION)" ]; then \
		echo "Error: Incorrect Node.js version ($(CURRENT_NODE)). Expected $(NODE_VERSION). Run 'nvm use'."; \
		exit 1; \
	fi
