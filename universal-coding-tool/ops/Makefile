PYTHON ?= python3
NPM ?= npm
DOCKER_COMPOSE ?= docker compose
ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

init:
@if [ ! -f $(ROOT_DIR)/.env ]; then cp $(ROOT_DIR)/.env.example $(ROOT_DIR)/.env; fi
cd $(ROOT_DIR)/backend && uv pip sync --all-extras
cd $(ROOT_DIR)/frontend && $(NPM) install

up:
$(DOCKER_COMPOSE) -f $(ROOT_DIR)/ops/docker-compose.yml up --build

down:
$(DOCKER_COMPOSE) -f $(ROOT_DIR)/ops/docker-compose.yml down

seed:
$(PYTHON) $(ROOT_DIR)/ops/scripts/seed_policies.py

vm-template:
$(ROOT_DIR)/vm/scripts/build_vm_template.sh

test:
cd $(ROOT_DIR)/backend && $(PYTHON) -m pytest -m "not vm"

.PHONY: init up down seed vm-template test
