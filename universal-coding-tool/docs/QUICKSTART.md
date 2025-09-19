# Quickstart (macOS + VMware)

This quickstart walks a non-developer from zero to running the first sandboxed
job. Screenshots referenced below are placeholders—replace them with your own if
you customise the flow.

## 0. Prerequisites

1. **macOS** (Apple Silicon or Intel) with administrator privileges.
2. **Homebrew** installed. If not, run:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. **VMware Fusion** (Apple Silicon: Tech Preview, Intel: Fusion Pro/Player) or
   VMware Workstation on Windows/Linux.
4. **Ubuntu 22.04 ISO** downloaded from Canonical.
5. **Docker Desktop for Mac** installed and running.
6. **uv package manager** (fast Python dependency resolver):
   ```bash
   brew install uv
   ```
7. **jq** command-line JSON processor (used by VM scripts):
   ```bash
   brew install jq
   ```
8. **Node.js 20** (via Homebrew or `nvm`).

## 1. Create the Ubuntu VM template

1. Launch VMware and create a **new custom VM** using the Ubuntu 22.04 ISO.
2. Allocate at least **2 vCPUs, 4 GB RAM and 40 GB disk**.
3. After installation, follow `vm/base-image-notes.md` inside the repository to:
   - Install updates and guest tools.
   - Create the `sandbox` user and configure rootless Docker.
   - Enable the cloud-init NoCloud datasource.
   - Create `/var/lib/uct` (owned by `sandbox`).
4. Shut down the VM and take a snapshot named **`CLEAN_BASE`**.
5. Note the absolute path to the VMX file (e.g.
   `/Users/you/Documents/Virtual Machines/UCT.vmwarevm/UCT.vmx`).

## 2. Clone the repository

```bash
mkdir -p ~/workspace
cd ~/workspace
# Replace with your Git remote
git clone https://example.com/universal-coding-tool.git
cd universal-coding-tool
```

## 3. Configure environment variables

1. Copy the sample environment file and edit it:
   ```bash
   cp .env.example .env
   ```
2. Update the following keys inside `.env`:
   - `UCT_SESSION_SECRET`: change to a long random string.
   - `UCT_ADMIN_EMAIL` / `UCT_ADMIN_PASSWORD`: set the credentials you prefer.
   - `UCT_VM_VMX_PATH`: absolute VMX path from step 1.
   - `UCT_VM_GUEST_PASS`: password for the `sandbox` guest user.

## 4. Install dependencies

Run the helper make target (installs Python deps with `uv` and Node packages):

```bash
make init
```

If prompted about `uv` not found, run `pip install uv` or `brew install uv` and
retry.

## 5. Seed policies

```bash
make seed
```

This writes `ops/policies.json` with the four default policies.

## 6. Launch the dev environment

Start the orchestrator and UI via Docker Compose:

```bash
make up
```

- Backend is available at http://localhost:8000/api/health
- Front-end is served by Vite at http://localhost:5173

Stop the stack with:

```bash
make down
```

## 7. Sign in to the UI

1. Open http://localhost:5173 in a browser.
2. Sign in using the admin email/password configured in `.env`.
3. The dashboard lists jobs (empty at first) and shows the “Submit job” panel.

## 8. Run the sample jobs

### 8.1 Hello Python (container mode)

1. In the “Submit job” panel, set:
   - Name: `hello_python`
   - Language: `Python`
   - Policy: `safe-default`
   - Command: `python main.py`
   - Source code: `print("Hello from sandbox")`
2. Click **Run job**. The job appears in the list with status `running` then
   `succeeded`.
3. Select the job to stream logs and download the generated artifact (if any).

### 8.2 Research policy (network allowlist)

1. Change Policy to `research`.
2. Update source to include a small `requests.get("https://example.com")`.
3. Submit the job—this policy allows outbound networking and demonstrates the
   difference vs. `safe-default`.

### 8.3 Dedicated VM

1. Switch Policy to `dedicated-vm` and run a longer command such as building a
   Rust crate. The orchestrator will revert the VMware snapshot, copy the job
   payload, execute the script inside the VM and collect artifacts back.

> ℹ️ VM runs require the credentials exported in `.env` and will take longer as
> snapshots revert and cloud-init boots.

## 9. Tear down

Stop the stack with `make down` and, if desired, remove any temporary job
workspaces stored under `~/uct_jobs` (configurable via `UCT_JOB_ROOT`).

## 10. Troubleshooting

- **Docker not running** – Start Docker Desktop and retry `make up`.
- **`vmrun` command not found** – Install VMware command line tools or add them
  to your PATH. Fusion ships with `/Applications/VMware Fusion.app/Contents/Library/vmrun`.
- **Jobs stuck in `queued`** – Check backend logs (`backend/app/logs`) and
  verify policies were seeded correctly.

For deeper operational guidance review `docs/OPERATIONS.md` and the FAQ.
