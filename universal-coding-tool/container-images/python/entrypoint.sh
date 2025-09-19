#!/usr/bin/env bash
set -euo pipefail

CMD="$*"
if [[ -z "${CMD}" && -n "${JOB_CMD:-}" ]]; then
  CMD="${JOB_CMD}"
fi

if [[ -z "${CMD}" ]]; then
  echo "No command provided" >&2
  exit 1
fi

TIMEOUT_S=${TIMEOUT_S:-600}
CPU_LIMIT=${CPU_LIMIT:-}
MEM_LIMIT_MB=${MEM_LIMIT_MB:-}

if [[ -n "${CPU_LIMIT}" ]]; then
  if ! ulimit -t "${CPU_LIMIT}" 2>/dev/null; then
    echo "[uct-entrypoint] Warning: unable to enforce CPU_LIMIT=${CPU_LIMIT}" >&2
  fi
fi

if [[ -n "${MEM_LIMIT_MB}" ]]; then
  if [[ "${MEM_LIMIT_MB}" =~ ^[0-9]+$ ]]; then
    if ! ulimit -v "$((MEM_LIMIT_MB * 1024))" 2>/dev/null; then
      echo "[uct-entrypoint] Warning: unable to enforce MEM_LIMIT_MB=${MEM_LIMIT_MB}" >&2
    fi
  else
    echo "[uct-entrypoint] Warning: MEM_LIMIT_MB must be numeric (got ${MEM_LIMIT_MB})" >&2
  fi
fi

if [[ -n "${NET_MODE:-}" ]]; then
  echo "[uct-entrypoint] NET_MODE=${NET_MODE}" >&2
fi

if ! id sandbox &>/dev/null; then
  useradd --create-home --shell /bin/bash sandbox
fi

mkdir -p /work/out /work/src
chown -R sandbox:sandbox /work || true
umask 077

if [[ "$(id -u)" -eq 0 ]]; then
  exec su - sandbox -c "cd /work/src && timeout ${TIMEOUT_S} bash -lc \"${CMD}\""
else
  cd /work/src
  exec timeout "${TIMEOUT_S}" bash -lc "${CMD}"
fi
