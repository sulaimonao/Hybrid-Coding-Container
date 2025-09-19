"""VM-based execution backend using VMware command line tooling."""
from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .logging import logger
from .settings import settings


@dataclass
class VMRunResult:
    """Information about a VM-backed execution."""

    exit_code: int
    command: str


class VMRunner:
    """Coordinate execution inside a dedicated or shared VMware VM."""

    def __init__(self, scripts_dir: Path | None = None) -> None:
        self.scripts_dir = scripts_dir or settings.vm_scripts_dir

    def _script(self, name: str) -> Path:
        return (self.scripts_dir / name).resolve()

    def build_run_command(
        self,
        job_id: str,
        workspace: Path,
        policy: Dict[str, object],
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, object]:
        vm_policy = policy.get("vm", {})
        script = self._script("run_in_guest.sh")
        args = [
            str(script),
            str(settings.vm_vmx_path or ""),
            settings.vm_snapshot_name,
            job_id,
            str(workspace),
        ]
        if env:
            args.append(json_dumps(env))
        return {
            "command": args,
            "cpus": vm_policy.get("cpus"),
            "memory": vm_policy.get("memory"),
        }

    def run(
        self,
        job_id: str,
        workspace: Path,
        policy: Dict[str, object],
        env: Optional[Dict[str, str]] = None,
        log_callback: Optional[callable] = None,
    ) -> VMRunResult:
        spec = self.build_run_command(job_id, workspace, policy, env)
        args = spec["command"]
        logger.info("Executing VM job %s via %s", job_id, " ".join(shlex.quote(a) for a in args))
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            if log_callback:
                log_callback(line)
        process.wait()
        return VMRunResult(exit_code=process.returncode or 0, command=" ".join(args))


def json_dumps(data: Dict[str, str]) -> str:
    """Serialize dictionaries deterministically for transmission."""

    import json

    return json.dumps(data, sort_keys=True)


__all__ = ["VMRunner", "VMRunResult"]
