# Universal Coding Tool

The Universal Coding Tool (UCT) is a hybrid execution platform that runs user
supplied code inside hardened containers or isolated Ubuntu VMs. It was designed
for macOS operators who rely on VMware Fusion/Workstation for the inner guest
OS. UCT ships with:

- **FastAPI orchestrator** that schedules jobs, enforces security policies and
  exposes REST APIs for job management, logs and artifacts.
- **React + Vite front-end** with real-time log streaming, policy visibility and
  a responsive dashboard for less technical reviewers.
- **Hardened language runtimes** (Python, Node, Rust) packaged as Docker images
  with a common entrypoint that enforces timeouts and non-root execution.
- **VM automation scripts** that integrate with `vmrun` to revert snapshots,
  seed job payloads via cloud-init and collect artifacts from the guest.
- **Policy engine** backed by JSON definitions and a seed script for the default
  set (`safe-default`, `research`, `experimental`, `dedicated-vm`).

UCT emphasises defense-in-depth: all jobs start inside rootless Docker
containers and can be escalated to a dedicated VM when the risk profile calls
for stronger isolation.

## Repository layout

```
universal-coding-tool/
  backend/           # FastAPI app, tests and Dockerfile
  frontend/          # React web UI (Vite + TypeScript)
  container-images/  # Hardened language runtimes
  vm/                # VMware + cloud-init automation assets
  ops/               # Dev tooling (Makefile, compose, seed script)
  docs/              # Operator and architecture docs
  .github/           # CI pipelines
```

## Quick links

- [Quickstart guide](./QUICKSTART.md)
- [Architecture overview](./ARCHITECTURE.md)
- [Security deep dive](./SECURITY.md)
- [Operations handbook](./OPERATIONS.md)
- [UI walkthrough](./UI_GUIDE.md)
- [FAQ](./FAQ.md)

## Minimum requirements

- macOS with VMware Fusion/Workstation capable of running Ubuntu 22.04
- Docker Desktop (for building/running containers locally)
- Python 3.11+ with [`uv`](https://github.com/astral-sh/uv)
- Node.js 20 (for the front-end dev server)

Refer to the quickstart for the end-to-end installation instructions tailored
for non-coders.
