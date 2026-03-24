export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$(shell pwd)

UV := $(shell command -v uv 2> /dev/null)

BLACK="\033[0;30m"
LIGHT_BLACK="\033[1;30m"
RED="\033[0;31m"
LIGHT_RED="\033[1;31m"
GREEN="\033[0;32m"
LIGHT_GREEN="\033[1;32m"
YELLOW="\033[0;33m"
LIGHT_YELLOW="\033[1;33m"
BLUE="\033[0;34m"
LIGHT_BLUE="\033[1;34m"
PURPLE="\033[0;35m"
LIGHT_PURPLE="\033[1;35m"
CYAN="\033[0;36m"
GRAY="\033[0;37m"
LIGHT_GRAY="\033[1;37m"
NC="\033[0m"

help:
	@echo ${LIGHT_BLUE}'Development shortcuts and commands'${NC}
	@echo ${LIGHT_GRAY}'For more information read the project Readme'${NC}
	@echo
	@echo ${LIGHT_YELLOW}'Usage:'${NC}
	@echo '  make '${LIGHT_GREEN}'<command>'${NC}
	@echo
	@echo ${LIGHT_YELLOW}'Commands:'${NC}
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-uv: ## Install UV
	curl -LsSf https://astral.sh/uv/install.sh | sh

create-venv:
	@uv python install 3.14.3
	@uv venv --python 3.14.3 --clear

init-local: create-venv  ## Initialize the local development environment
	@uv sync --locked --all-groups
	@$(MAKE) lint-fix format

clean: ## Clean local environment
	@find . -name '*.pyc' | xargs rm -rf
	@find . -name '*.pyo' | xargs rm -rf
	@find . -name '__pycache__' -type d | xargs rm -rf
	@find . -name '.pytest_cache' -type d | xargs rm -rf
	@find . -name '.cache' -type d | xargs rm -rf
	@find . -name '.coverage' -type f | xargs rm -f
	@find . -name 'coverage.xml' -type f | xargs rm -f
	@rm -f *.log
	@rm -f *.log.*

install: ## Install production dependencies
	@uv sync --locked

install-quality-check: ## Install quality check dependencies
	@uv sync --locked --group lint --group test

install-dev: ## Install development dependencies
	@uv sync --locked --all-groups

lint: ## Run linters
	@echo ${LIGHT_YELLOW}'Running linters...'${NC}
	@echo ${LIGHT_YELLOW}'Step 1: bandit'${NC}
	@$(UV) run bandit jwks_multi/*.py -iii -ll -s=B308,B703
	@echo ${LIGHT_YELLOW}'Step 2: black'${NC}
	@$(UV) run black --check --config=./pyproject.toml jwks_multi/* tests/*
	@echo ${LIGHT_YELLOW}'Step 3: ruff'${NC}
	@$(UV) run ruff check jwks_multi/*

lint-fix format: ## Fix linters and format
	@echo ${LIGHT_YELLOW}'Fixing linters...'${NC}
	@echo ${LIGHT_YELLOW}'Step 1: black'${NC}
	@$(UV) run black --config=./pyproject.toml jwks_multi/ tests/ --verbose
	@echo ${LIGHT_YELLOW}'Step 2: ruff'${NC}
	@$(UV) run ruff check jwks_multi/* --fix
	@$(MAKE) --silent lint

coverage test-cov test-coverage: clean ## Run the application unit tests with coverage
	@ENVIRONMENT=test $(UV) run pytest --cov=jwks_multi --cov-report term-missing --cov-report=xml

test: clean ## Run the application unit tests. Ex.: make test or make test file=tests/api/healthcheck/views/test_healthcheck.py
	@ENVIRONMENT=test $(UV) run pytest $(if $(file),$(file),)

release-check: ## Validate local release artifacts (build + twine check)
	@echo ${LIGHT_YELLOW}'Running release checks...'${NC}
	@$(UV) sync --locked --group release
	@rm -rf dist build
	@$(UV) run --group release python -m build
	@$(UV) run --group release twine check --strict dist/*

release-major: ## Creates major release (1.0.0)
	@$(MAKE) _release LABEL=major

release-minor: ## Creates minor release (0.1.0)
	@$(MAKE) _release LABEL=minor

release-patch: ## Creates patch release (0.0.1)
	@$(MAKE) _release LABEL=patch

_release:
	@set -e; \
	VERSION_INFO="$$($(UV) run bump2version $(LABEL) --dry-run --no-tag --no-commit --list)"; \
	OLD_VERSION=$$(printf '%s\n' "$$VERSION_INFO" | awk -F= '/^current_version=/{print $$2}'); \
	NEW_VERSION=$$(printf '%s\n' "$$VERSION_INFO" | awk -F= '/^new_version=/{print $$2}'); \
	$(UV) run towncrier build --yes --version "$$NEW_VERSION" && \
	git add CHANGELOG.md && git commit -m "Update CHANGELOG" && \
	$(UV) run bump2version $(LABEL) --no-tag --no-commit && $(UV) lock && \
	git add -u && git commit -m "Bump version: $$OLD_VERSION -> $$NEW_VERSION" && \
	git tag -a "$$NEW_VERSION" -m "Bump version: $$OLD_VERSION -> $$NEW_VERSION";
