#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 <vmx_path> <snapshot_name> <job_id> <workspace> [env_json]" >&2
  exit 1
fi

VMX_PATH="$1"
SNAPSHOT="$2"
JOB_ID="$3"
WORKSPACE="$4"
ENV_JSON="${5:-}"
VMRUN_BINARY="${VMRUN:-vmrun}"
GUEST_USER="${UCT_VM_GUEST_USER:-sandbox}"
GUEST_PASS="${UCT_VM_GUEST_PASS:-sandbox}"

META_FILE="${WORKSPACE}/meta.json"
if [[ ! -f "${META_FILE}" ]]; then
  echo "meta.json missing in workspace" >&2
  exit 1
fi

IMAGE=$(jq -r '.image' "${META_FILE}")
CMD=$(jq -r '.cmd' "${META_FILE}")
POLICY=$(jq -r '.policy' "${META_FILE}")

JOB_ARCHIVE="${WORKSPACE}/${JOB_ID}.tgz"
CONFIG_JSON="${WORKSPACE}/${JOB_ID}-config.json"
tar -czf "${JOB_ARCHIVE}" -C "${WORKSPACE}" src out
jq -n --arg image "${IMAGE}" --arg cmd "${CMD}" --arg policy "${POLICY}" '{image:$image, cmd:$cmd, policy:$policy}' > "${CONFIG_JSON}"

log() {
  printf '[vm-runner] %s\n' "$1"
}

log "Reverting ${VMX_PATH} to snapshot ${SNAPSHOT}"
"${VMRUN_BINARY}" -T fusion revertToSnapshot "${VMX_PATH}" "${SNAPSHOT}"
log "Starting VM"
"${VMRUN_BINARY}" -T fusion start "${VMX_PATH}" nogui

log "Waiting for guest tools"
for _ in {1..60}; do
  if "${VMRUN_BINARY}" -T fusion -gu "${GUEST_USER}" -gp "${GUEST_PASS}" listProcessesInGuest "${VMX_PATH}" >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

log "Copying payload"
"${VMRUN_BINARY}" -T fusion -gu "${GUEST_USER}" -gp "${GUEST_PASS}" CopyFileFromHostToGuest "${VMX_PATH}" "${JOB_ARCHIVE}" "/var/lib/uct/job.tgz"
"${VMRUN_BINARY}" -T fusion -gu "${GUEST_USER}" -gp "${GUEST_PASS}" CopyFileFromHostToGuest "${VMX_PATH}" "${CONFIG_JSON}" "/var/lib/uct/job-config.json"

if [[ -n "${ENV_JSON}" ]]; then
  printf '%s' "${ENV_JSON}" > "${WORKSPACE}/${JOB_ID}-env.json"
  "${VMRUN_BINARY}" -T fusion -gu "${GUEST_USER}" -gp "${GUEST_PASS}" CopyFileFromHostToGuest "${VMX_PATH}" "${WORKSPACE}/${JOB_ID}-env.json" "/var/lib/uct/env.json"
fi

log "Waiting for job completion"
for _ in {1..120}; do
  if "${VMRUN_BINARY}" -T fusion -gu "${GUEST_USER}" -gp "${GUEST_PASS}" fileExistsInGuest "${VMX_PATH}" "/var/lib/uct/status" >/dev/null 2>&1; then
    break
  fi
  sleep 10
done

log "Collecting artifacts"
"${VMRUN_BINARY}" -T fusion -gu "${GUEST_USER}" -gp "${GUEST_PASS}" CopyFileFromGuestToHost "${VMX_PATH}" "/var/lib/uct/artifacts.tgz" "${WORKSPACE}/artifacts.tgz"

log "Stopping VM"
"${VMRUN_BINARY}" -T fusion stop "${VMX_PATH}" soft || true

log "Artifacts extracted to ${WORKSPACE}/artifacts.tgz"
if [[ -f "${WORKSPACE}/artifacts.tgz" ]]; then
  mkdir -p "${WORKSPACE}/out"
  tar -xzf "${WORKSPACE}/artifacts.tgz" -C "${WORKSPACE}/out" || true
  rm -f "${WORKSPACE}/artifacts.tgz"
fi
