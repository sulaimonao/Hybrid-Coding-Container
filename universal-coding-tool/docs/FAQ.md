# FAQ & Glossary

## Frequently asked questions

### The job cannot reach the internet. Is that expected?
Yes. The `safe-default` policy disables networking (`--network none`). Switch to
`research` if you need outbound HTTP(S). Update `ops/policies.json` to define a
custom allow-list if required.

### VM runs stay queued forever.
Ensure `vmrun` is on your PATH and that the credentials in `.env` are correct.
Review `vm/scripts/run_in_guest.sh` output for clues. If VMware Tools are not
installed, the script cannot detect job completion—reinstall `open-vm-tools` in
the guest.

### Container jobs fail with "permission denied" when writing files.
Workspaces are mounted with `nosuid,nodev` and owned by the host user. Verify the
container user can write to `/work/out`. You may need to adjust directory
permissions if running the backend as a different UNIX user.

### How do I allocate more CPU or memory to a job?
Create a new policy in `ops/policies.json` (copy `research` and tweak `cpus`,
`memory`, `pids_limit`). Run `make seed` or edit the JSON manually, then restart
the backend or call `/api/policies` to ensure it reloads.

### Can I integrate real LLMs?
Yes, via the adapter registry. Implement a new class in `backend/app/adapters/`
that extends `ModelAdapter` and register it. Wiring the adapter into the API is a
future task.

### Where are logs stored?
Each job keeps `logs/run.log` under `~/uct_jobs/<job_id>`. The UI streams the
same file via SSE.

### How do I clean up?
Stop services with `make down` and delete old job directories from
`UCT_JOB_ROOT`. Remove Docker images with `docker image rm uct-python:latest` and
friends if you no longer need them.

## Glossary

- **Container** – Lightweight runtime that shares the host kernel. Jobs run in
  Docker containers derived from language-specific images.
- **Seccomp** – Linux kernel feature that filters syscalls. The default profile
  is applied to container jobs.
- **Snapshot** – Saved VM state. VMware reverts to the `CLEAN_BASE` snapshot
  before executing dedicated VM jobs.
- **Cloud-init** – Ubuntu service that executes configuration at first boot.
  Used to run job payloads when the VM boots.
- **Policy** – JSON document describing the runner (container vs. VM) and resource
  limits. Stored in `ops/policies.json`.
