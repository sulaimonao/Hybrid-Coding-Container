#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <vmx_path> <guest_path> <host_destination>" >&2
  exit 1
fi

VMX_PATH="$1"
GUEST_PATH="$2"
HOST_DEST="$3"
VMRUN_BINARY="${VMRUN:-vmrun}"
GUEST_USER="${UCT_VM_GUEST_USER:-sandbox}"
GUEST_PASS="${UCT_VM_GUEST_PASS:-sandbox}"

"${VMRUN_BINARY}" -T fusion -gu "${GUEST_USER}" -gp "${GUEST_PASS}" CopyFileFromGuestToHost "${VMX_PATH}" "${GUEST_PATH}" "${HOST_DEST}"
