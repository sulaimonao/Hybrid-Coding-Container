"""Docker-based execution backend."""
from __future__ import annotations

import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

from .logging import logger
from .settings import settings


@dataclass
class DockerRunSpec:
    """Derived configuration for running a container."""

    image: str
    command: str
    env: Dict[str, str]
    mounts: Dict[str, Dict[str, str]]
    network_mode: str
    read_only: bool
    security_opts: Iterable[str]
    cap_drop: Iterable[str]
    tmpfs: Dict[str, str]
    extra_args: Dict[str, object]


class DockerRunner:
    """Prepare and execute Docker containers according to a policy."""

    def __init__(self) -> None:
        self.docker_binary = shutil.which("docker")

    def _policy_to_spec(
        self,
        image: str,
        command: str,
        workspace: Path,
        policy: Dict[str, object],
        env: Optional[Dict[str, str]] = None,
    ) -> DockerRunSpec:
        docker_policy = policy.get("docker", {})
        env = dict(env or {})
        env.setdefault("JOB_CMD", command)
        env.setdefault("TIMEOUT_S", str(settings.default_timeout_seconds))
        mounts = {
            str(workspace): {
                "bind": "/work",
                "mode": "rw,nosuid,nodev,noexec",
            }
        }
        network_mode = docker_policy.get("network", "none")
        if network_mode == "allowlist":
            network_mode = docker_policy.get("network_mode", "bridge")
        if network_mode:
            env.setdefault("NET_MODE", str(network_mode))
        read_only = bool(docker_policy.get("read_only_root", False))
        security_opts = []
        if docker_policy.get("no_new_privileges", True):
            security_opts.append("no-new-privileges:true")
        seccomp = docker_policy.get("seccomp")
        if seccomp and seccomp != "default":
            security_opts.append(f"seccomp={seccomp}")
        cap_drop = docker_policy.get("cap_drop", "ALL")
        if isinstance(cap_drop, str):
            cap_drop = [cap_drop]
        tmpfs = docker_policy.get("tmpfs", {})
        extra_args: Dict[str, object] = {}
        if "cpus" in docker_policy:
            extra_args["cpus"] = docker_policy["cpus"]
            env.setdefault("CPU_LIMIT", str(docker_policy["cpus"]))
        if "memory" in docker_policy:
            extra_args["memory"] = docker_policy["memory"]
            memory_mb = self._memory_to_megabytes(str(docker_policy["memory"]))
            if memory_mb:
                env.setdefault("MEM_LIMIT_MB", str(memory_mb))
        if "pids_limit" in docker_policy:
            extra_args["pids_limit"] = docker_policy["pids_limit"]
        extra_args["user"] = docker_policy.get("user", "sandbox")
        extra_args["workdir"] = "/work/src"
        extra_args["env_file"] = None
        return DockerRunSpec(
            image=image,
            command=command,
            env=env,
            mounts=mounts,
            network_mode=network_mode,
            read_only=read_only,
            security_opts=security_opts,
            cap_drop=cap_drop,
            tmpfs=tmpfs,
            extra_args=extra_args,
        )

    def build_docker_command(self, spec: DockerRunSpec) -> Iterable[str]:
        """Build a docker CLI command for the provided run specification."""

        args = [self.docker_binary or "docker", "run", "--rm"]
        if spec.read_only:
            args.append("--read-only")
        for host_path, mount in spec.mounts.items():
            bind = mount.get("bind", "/work")
            mode = mount.get("mode", "ro")
            args.extend(["-v", f"{host_path}:{bind}:{mode}"])
        if spec.network_mode:
            args.extend(["--network", spec.network_mode])
        for cap in spec.cap_drop:
            args.extend(["--cap-drop", cap])
        for opt in spec.security_opts:
            args.extend(["--security-opt", opt])
        for mount_point, tmpfs_opts in spec.tmpfs.items():
            args.extend(["--tmpfs", f"{mount_point}:{tmpfs_opts}"])
        for key, value in spec.env.items():
            args.extend(["-e", f"{key}={value}"])
        if spec.extra_args.get("cpus"):
            args.extend(["--cpus", str(spec.extra_args["cpus"])])
        if spec.extra_args.get("memory"):
            args.extend(["--memory", str(spec.extra_args["memory"])])
        if spec.extra_args.get("pids_limit"):
            args.extend(["--pids-limit", str(spec.extra_args["pids_limit"])])
        args.extend(["--workdir", spec.extra_args.get("workdir", "/work")])
        args.extend(["--user", spec.extra_args.get("user", "sandbox")])
        args.append(spec.image)
        if spec.command:
            args.append(spec.command)
        return args

    @staticmethod
    def _memory_to_megabytes(value: str) -> Optional[int]:
        """Convert Docker memory strings (e.g. 1g, 512m) into megabytes."""

        normalized = value.strip().lower()
        if normalized.endswith("g"):
            try:
                return int(float(normalized[:-1]) * 1024)
            except ValueError:
                return None
        if normalized.endswith("m"):
            try:
                return int(float(normalized[:-1]))
            except ValueError:
                return None
        try:
            # Assume bytes if a raw integer was supplied.
            bytes_value = int(float(normalized))
            return int(bytes_value / (1024 * 1024)) if bytes_value else None
        except ValueError:
            return None

    def run(
        self,
        job_id: str,
        image: str,
        command: str,
        workspace: Path,
        policy: Dict[str, object],
        env: Optional[Dict[str, str]] = None,
        log_callback: Optional[callable] = None,
    ) -> int:
        """Execute the job inside a Docker container and stream logs."""

        spec = self._policy_to_spec(image, command, workspace, policy, env)
        docker_cmd = list(self.build_docker_command(spec))
        logger.info("Executing docker job %s with command: %s", job_id, " ".join(shlex.quote(a) for a in docker_cmd))
        if not self.docker_binary:
            raise RuntimeError("Docker binary not found on PATH")
        process = subprocess.Popen(
            docker_cmd,
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
        return process.returncode


__all__ = ["DockerRunner", "DockerRunSpec"]
