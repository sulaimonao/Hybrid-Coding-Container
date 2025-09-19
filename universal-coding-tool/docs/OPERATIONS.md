# Operations Handbook

## VM lifecycle

- **Template maintenance** – Keep the Ubuntu template patched monthly. Boot the
  VM, run `sudo apt update && sudo apt upgrade`, ensure Docker rootless still
  works, then take a fresh snapshot `CLEAN_BASE`.
- **Snapshot hygiene** – VMware snapshots grow over time. Periodically delete and
  recreate them after patching to avoid disk bloat.
- **Credential rotation** – Update `UCT_VM_GUEST_PASS` in `.env` and inside the
  VM using `sudo passwd sandbox`. Restart jobs after changing credentials.

## Running jobs manually

Use the CLI if you need to debug the orchestrator:

```bash
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"changeme"}'

curl -b cookies.txt -X POST http://localhost:8000/api/jobs \
  -H 'Content-Type: application/json' \
  -d '{"name":"cli","lang":"python","files":[{"path":"main.py","content":"print(123)"}],"cmd":"python main.py","policy":"safe-default"}'
```

## Artifacts & retention

- Job workspaces live under `UCT_JOB_ROOT` (default `~/uct_jobs`). Each contains
  `src/`, `out/`, `logs/`, `meta.json`.
- Delete stale jobs with `rm -rf ~/uct_jobs/<job_id>` after verifying artifacts
  are backed up.
- Archive artifacts centrally by syncing `out/` to object storage.

## Backups

- **Policies** – `ops/policies.json` should be version controlled. Use Git for
  changes and audit trails.
- **VM image** – Store the base VM on redundant storage or export an OVA.
- **Database** – No relational DB is used; job state is file-based. If you need
  persistence across hosts, mount `UCT_JOB_ROOT` on network storage.

## Updating container images

1. Edit the corresponding Dockerfile under `container-images/<lang>/`.
2. Rebuild and tag:
   ```bash
   docker build -t uct-python:latest container-images/python
   docker build -t uct-node:latest container-images/node
   docker build -t uct-rust:latest container-images/rust
   ```
3. Update `settings.default_language_images` if you publish to a registry.
4. Restart the backend to pick up the new image tags.

## CI/CD

- GitHub Actions run linting/tests on push. Backend workflow executes `pytest -m
  "not vm"`, frontend workflow runs ESLint + TypeScript build.
- Add additional checks (security scanning, image builds) as required.

## Rotating API secrets

1. Generate a new random string for `UCT_SESSION_SECRET` (e.g. `openssl rand
   -hex 32`).
2. Update `.env` and restart the backend. Existing sessions become invalid.

## Monitoring

- Expose `/api/health` to your monitoring stack.
- Tail backend logs (`uvicorn` output) for job lifecycle events.
- Track VM operations by logging `vm/scripts/run_in_guest.sh` output.

## Disaster recovery

- Keep offline copies of the VM template and `ops/policies.json`.
- If the orchestrator host is lost, reinstall dependencies, restore `.env` and
  `~/uct_jobs`, and re-run `make seed` to restore policies.
