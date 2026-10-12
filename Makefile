.DEFAULT_GOAL := help
.PHONY: help install serve build check rovo
PYTHON ?= python3

help:  ## Display this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install pinned documentation and validation dependencies
	$(PYTHON) -m pip install -r requirements-docs.txt

serve:  ## Preview documentation locally
	$(PYTHON) -m zensical serve

build:  ## Build the documentation site
	$(PYTHON) -m zensical build --strict

check:  ## Validate plugin metadata, references, snippets, and documentation
	$(PYTHON) scripts/check.py
	$(MAKE) build PYTHON="$(PYTHON)"

rovo:  ## Regenerate the Rovo Dev review rules from the review checklist
	$(PYTHON) scripts/check.py --write-rovo
