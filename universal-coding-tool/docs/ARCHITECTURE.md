# Architecture Overview

## High-level flow

```
macOS Host ──┐
             │  REST API / WebSockets
             │
         ┌───▼──────────────┐
         │ FastAPI Backend  │
         │  (orchestrator)  │
         └───┬───────▲──────┘
             │       │
   policy    │       │ logs/artifacts
  decision   │       │
             ▼       ▼
      Docker Runner   ──────► Hardened container images (Python/Node/Rust)
             │
             └──► VMware Runner ─► Ubuntu VM (cloud-init) ─► Docker inside VM
```

1. A user submits a job via REST or the React UI.
2. The **policy engine** reads `ops/policies.json` and decides between the
   container runner or the VMware runner.
3. For containers, the orchestrator invokes `docker run` with the hardened
   language image, mounting a per-job workspace at `/work` and enforcing
   seccomp/no-new-privileges/resource limits.
4. For VM runs, the orchestrator uses `vmrun` to revert a snapshot, copy the job
   payload into `/var/lib/uct`, and lets cloud-init + the guest script start the
   job. Artifacts are tarred and copied back to the host.
5. Logs are appended to `~/uct_jobs/<job_id>/logs/run.log` and streamed to the UI
   via Server Sent Events.

## Backend components

- **`core/orchestrator.py`** – tracks job state, writes metadata, schedules
  synchronous execution via the Docker or VM runner and exposes convenience
  helpers for the API.
- **`core/policy_engine.py`** – JSON-backed loader with hot reload capability.
- **`core/docker_runner.py`** – translates policy attributes into CLI flags,
  builds the `docker run` command and streams process output into the storage
  layer.
- **`core/vm_runner.py`** – wraps `vmrun` commands and the helper shell scripts.
- **`core/storage.py`** – ensures consistent workspace layout: `src/`, `out/`,
  `logs/` and `meta.json`.
- **`core/auth.py`** – cookie-based session auth using `itsdangerous` and
  `passlib` for password hashing.

## Front-end

The React application consumes the REST API, showing:

- Job list with filters.
- Job detail view with metadata, log streaming and artifacts.
- Submission form with quick presets.

The UI relies on `EventSource` for live logs and `axios` for REST calls. Styling
is bespoke CSS (no dependency on Tailwind/Material).

## Container images

Each language image is derived from the official runtime base (Python 3.11,
Node 20, Rust 1.80). A shared `entrypoint.sh` creates a `sandbox` user if
missing, enforces timeouts via `/usr/bin/timeout`, and executes commands inside
`/work/src` while writing artifacts to `/work/out`.

## VMware pipeline

1. `vm/scripts/run_in_guest.sh` reverts the VM to `CLEAN_BASE`, starts it, copies
   the job archive and config JSON to `/var/lib/uct` and waits for a
   `/var/lib/uct/status` marker.
2. `cloud-init/user-data.yaml` installs dependencies, unpacks the payload and
   invokes Docker rootless (via the sandbox user) to run the specified container
   image.
3. Artifacts are bundled into `/var/lib/uct/artifacts.tgz` and copied back.

The VMware path is intentionally verbose to make swapping to SSH easy: only the
`run_in_guest.sh` script and `VMRunner` would need to change.

## Decision log

- **Docker CLI vs. SDK**: The runner uses the Docker CLI to avoid additional
  dependencies and to stay compatible with rootless environments. If your stack
  favours the Python SDK, wrap it under the same interface.
- **Session cookies**: Chosen for simplicity (no external identity provider).
  Tokens are signed with `itsdangerous` and stored as HTTP-only cookies.
- **UV lock file**: Although generated manually here, the intent is to standardise
  on `uv` for deterministic installs on macOS.
- **VM automation**: `vmrun` is assumed because VMware Fusion/Workstation expose
  it consistently. SSH-based automation can be swapped in by changing
  `vm/scripts/run_in_guest.sh` and `core/vm_runner.py`.

## Future hooks

- **Model adapters**: `backend/app/adapters` exposes a registry; new adapters can
  extend `ModelAdapter` and self-register.
- **LLM orchestration**: integrate with adapters once business requirements
  exist; the API already exposes stub endpoints for job submission.
- **Policy editor UI**: the front-end can add CRUD views on `ops/policies.json`.
