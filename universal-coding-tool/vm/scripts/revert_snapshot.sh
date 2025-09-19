#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <vmx_path> <snapshot_name>" >&2
  exit 1
fi

VMX_PATH="$1"
SNAPSHOT="$2"
VMRUN_BINARY="${VMRUN:-vmrun}"

"${VMRUN_BINARY}" -T fusion revertToSnapshot "${VMX_PATH}" "${SNAPSHOT}"
