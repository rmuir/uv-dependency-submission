SHELL := /bin/bash
.SHELLFLAGS := -norc -euo pipefail -c
.DEFAULT_GOAL := help

.PHONY: all
all: lint ## Run all checks

.PHONY: lint lint-ruff lint-ruff-format lint-ruff-problems lint-basedpyright
lint: lint-ruff lint-basedpyright ## Lint problems in sources

lint-ruff: lint-ruff-format lint-ruff-problems ## Check python with ruff

lint-ruff-format: ## Validate python formatting
	# validate python formatting, 'make -k fix' will address issues
	uv run ruff format --diff

lint-ruff-problems: ## Check python for problems
	# check python for problems, 'make -k fix' may address some issues
	uv run ruff check

lint-basedpyright: ## Type-check python with basedpyright
	# check python types
	uv run basedpyright

# Autofixing
.PHONY: fix fix-ruff fix-ruff-format fix-ruff-problems
fix: fix-ruff ## Fix problems in sources

.NOPARALLEL: fix-ruff
fix-ruff: fix-ruff-problems fix-ruff-format ## Fix python with ruff

fix-ruff-format: ## Fix python formatting
	# reformat python sources
	uv run ruff format

fix-ruff-problems: ## Fix python problems
	# autofix python sources: safe fixes only
	uv run ruff check --fix

.PHONY: help
help: ## Display this help screen
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
