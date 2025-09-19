#!/usr/bin/env bash
set -euo pipefail

cat <<'MSG'
This helper guides you through preparing the VMware Ubuntu template.

1. Install Ubuntu 22.04 as described in vm/base-image-notes.md.
2. Ensure rootless Docker is configured for the "sandbox" user.
3. Enable the NoCloud datasource and create /var/lib/uct.
4. Shut down the VM and take a snapshot named CLEAN_BASE.

Once the template is ready, export the VMX path and add it to .env:

  export UCT_VM_VMX="/Users/you/Documents/Virtual Machines/UCT.vmwarevm/UCT.vmx"
  export UCT_VM_SNAPSHOT="CLEAN_BASE"
  export UCT_VM_GUEST_USER="sandbox"
  export UCT_VM_GUEST_PASS="<password>"
MSG
