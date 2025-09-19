#!/usr/bin/env python3
"""Seed default policies into ops/policies.json."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_POLICIES = {
    "safe-default": {
        "runner": "container",
        "docker": {
            "cpus": 1,
            "memory": "1g",
            "pids_limit": 256,
            "network": "none",
            "read_only_root": True,
            "seccomp": "default",
            "cap_drop": ["ALL"],
            "no_new_privileges": True,
            "tmpfs": {"/tmp": "rw,nosuid,noexec,size=64m"},
        },
    },
    "research": {
        "runner": "container",
        "docker": {
            "cpus": 2,
            "memory": "4g",
            "network": "allowlist",
            "tmpfs": {"/tmp": "rw,nosuid,noexec,size=128m"},
        },
    },
    "experimental": {
        "runner": "container",
        "docker": {
            "cpus": 2,
            "memory": "4g",
            "network": "bridge",
        },
    },
    "dedicated-vm": {
        "runner": "vm",
        "vm": {
            "cpus": 2,
            "memory": "4g",
        },
    },
}


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    policy_file = repo_root / "ops" / "policies.json"
    policy_file.write_text(json.dumps(DEFAULT_POLICIES, indent=2))
    print(f"Seeded policies to {policy_file}")


if __name__ == "__main__":
    main()
