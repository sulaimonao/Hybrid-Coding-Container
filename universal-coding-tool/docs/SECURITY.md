# Security Model

UCT layers multiple controls to protect the host while running untrusted code.

## Defense in depth

1. **Rootless Docker inside Ubuntu VM** – The default execution path runs inside
   a Docker container hosted on the Ubuntu guest VM. Even if the container is
   compromised, the attack stays within the VM, not the macOS host.
2. **Locked-down container runtime** – Policies enforce:
   - `no-new-privileges`
   - Dropped capabilities (`cap_drop: ["ALL"]`)
   - Read-only container root filesystem (`--read-only`)
   - Seccomp default profile
   - Network isolation (`--network none` by default)
   - Resource limits (CPU shares, memory, PID counts, tmpfs for `/tmp`)
3. **Per-job workspace mounts** – Only `/work` is writable and mounted with
   `nosuid,nodev`. Logs and artifacts live under `~/uct_jobs/<job_id>` on the
   host, simplifying cleanup.
4. **Policy-based escalation** – Operators can explicitly opt into relaxed
   policies (`research`, `experimental`) or escalate to the `dedicated-vm`
   policy when user code needs privileged operations.

## VM escalation

- The `dedicated-vm` policy clones/reverts an Ubuntu VM snapshot (`CLEAN_BASE`) so
  each high-risk job starts on a pristine system.
- `vm/scripts/run_in_guest.sh` copies the job payload into `/var/lib/uct`,
  triggers the guest-side script via cloud-init and fetches artifacts. The VM is
  stopped afterwards, ensuring no state persists.
- Credentials for the guest (user/password) are stored in `.env` and can be
  rotated at will.

## Authentication

- API requests require a session cookie signed with `itsdangerous`.
- Passwords are hashed using `passlib` (bcrypt) before storage.
- Health and login endpoints are unauthenticated to support readiness checks.

## Network considerations

- `safe-default` disables outbound networking by using Docker’s `none` network.
- `research` switches to an allow-list friendly configuration. Implement actual
  allow-listing by extending the Docker runner to add `--network bridge` and
  `--add-host` or a custom firewall.
- VM runs rely on the guest network policies; configure Ubuntu’s firewall or
  network namespaces for stricter control.

## Secrets management

- Store secrets in `.env` locally, or preferably in a secrets manager when
  deploying. The `session_secret_key` must be rotated periodically.
- VM credentials should have minimal privileges and be changed after testing.

## Audit & observability

- Every job writes metadata to `meta.json` including exit codes and timestamps.
- Logs are stored in `logs/run.log`. Forward them to your SIEM via filebeat or
  Fluent Bit if required.

## Known gaps

- No automatic malware scanning of uploaded code. Integrate with ClamAV or a
  commercial scanner if required.
- No TLS termination: place a reverse proxy (nginx, traefik, cloud load balancer)
  in front of the backend and UI for production use.
- Policy enforcement does not yet validate commands (e.g. forbidding background
  processes). Extend `DockerRunner` to parse/deny dangerous commands.
