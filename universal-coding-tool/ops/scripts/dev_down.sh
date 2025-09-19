#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${OPS_DIR}/docker-compose.yml"
DOCKER_COMPOSE_BIN=${DOCKER_COMPOSE:-docker compose}

"${DOCKER_COMPOSE_BIN}" -f "${COMPOSE_FILE}" down "$@"
