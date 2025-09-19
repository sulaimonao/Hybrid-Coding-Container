"""Job orchestration and lifecycle management."""
from __future__ import annotations

import asyncio
import functools
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core import schemas
from .docker_runner import DockerRunner
from .logging import logger
from .policy_engine import PolicyEngine
from .settings import settings
from .storage import Storage, storage
from .vm_runner import VMRunner


TERMINAL_STATUSES = {"succeeded", "failed", "infra_error", "cancelled"}


@dataclass
class JobRecord:
    id: str
    name: str
    lang: str
    cmd: str
    policy_name: str
    execution_mode: str
    image: str
    limits: Dict[str, Any]
    env: Dict[str, str] = field(default_factory=dict)
    status: str = "queued"
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None


class Orchestrator:
    """Coordinate job submission and execution."""

    def __init__(
        self,
        storage_backend: Storage | None = None,
        policy_engine: PolicyEngine | None = None,
        docker_runner: DockerRunner | None = None,
        vm_runner: VMRunner | None = None,
    ) -> None:
        self.storage = storage_backend or storage
        self.policy_engine = policy_engine or PolicyEngine(settings.policy_file)
        self.docker_runner = docker_runner or DockerRunner()
        self.vm_runner = vm_runner or VMRunner()
        self.jobs: Dict[str, JobRecord] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        logger.info("Orchestrator ready; %s existing jobs tracked", len(self.jobs))

    async def shutdown(self) -> None:
        pending = [task for task in self.tasks.values() if not task.done()]
        if pending:
            logger.info("Waiting for %s running jobs to finish", len(pending))
            await asyncio.gather(*pending, return_exceptions=True)

    def _select_image(self, lang: str) -> str:
        try:
            return settings.default_language_images[lang]
        except KeyError as exc:
            raise ValueError(f"Unsupported language '{lang}'") from exc

    def _derive_limits(self, policy: Dict[str, Any], runner: str) -> Dict[str, Any]:
        if runner == "container":
            return policy.get("docker", {})
        return policy.get("vm", {})

    async def submit_job(self, payload: schemas.JobCreate) -> JobRecord:
        policy = self.policy_engine.get_policy(payload.policy)
        runner = policy.get("runner", "container")
        execution_mode = "container" if runner == "container" else "dedicated-vm"
        image = self._select_image(payload.lang)
        job_id = uuid.uuid4().hex
        env = payload.env or {}
        record = JobRecord(
            id=job_id,
            name=payload.name,
            lang=payload.lang,
            cmd=payload.cmd,
            policy_name=payload.policy,
            execution_mode=execution_mode,
            image=image,
            limits=self._derive_limits(policy, runner),
            env=env,
        )
        self.jobs[job_id] = record
        self.storage.create_job_workspace(job_id)
        self.storage.write_files(job_id, payload.files)
        self.storage.write_meta(
            job_id,
            {
                "id": job_id,
                "name": payload.name,
                "policy": payload.policy,
                "execution_mode": execution_mode,
                "image": image,
                "limits": record.limits,
                "cmd": payload.cmd,
                "env": env,
            },
        )
        loop = asyncio.get_event_loop()
        task = loop.create_task(self._run_job(record))
        self.tasks[job_id] = task
        return record

    async def _run_job(self, record: JobRecord) -> None:
        async with self._lock:
            record.status = "running"
            record.started_at = datetime.utcnow()
            self.storage.append_log(record.id, f"[orchestrator] Starting job {record.name}\n")
        policy = self.policy_engine.get_policy(record.policy_name)
        workspace = self.storage.job_path(record.id)

        def log_callback(message: str) -> None:
            self.storage.append_log(record.id, message)

        try:
            loop = asyncio.get_event_loop()
            if record.execution_mode == "container":
                run_callable = functools.partial(
                    self.docker_runner.run,
                    job_id=record.id,
                    image=record.image,
                    command=record.cmd,
                    workspace=workspace,
                    policy=policy,
                    env=record.env,
                    log_callback=log_callback,
                )
                exit_code = await loop.run_in_executor(None, run_callable)
            else:
                run_callable = functools.partial(
                    self.vm_runner.run,
                    job_id=record.id,
                    workspace=workspace,
                    policy=policy,
                    env=record.env,
                    log_callback=log_callback,
                )
                result = await loop.run_in_executor(None, run_callable)
                exit_code = result.exit_code
            record.exit_code = exit_code
            if exit_code == 0:
                record.status = "succeeded"
            else:
                record.status = "failed"
        except Exception as exc:  # noqa: BLE001
            record.status = "infra_error"
            record.error = str(exc)
            logger.exception("Job %s failed: %s", record.id, exc)
            self.storage.append_log(record.id, f"[error] {exc}\n")
        finally:
            record.finished_at = datetime.utcnow()
            self.storage.write_meta(
                record.id,
                {
                    "id": record.id,
                    "name": record.name,
                    "status": record.status,
                    "started_at": record.started_at.isoformat() if record.started_at else None,
                    "finished_at": record.finished_at.isoformat() if record.finished_at else None,
                    "execution_mode": record.execution_mode,
                    "policy": record.policy_name,
                    "exit_code": record.exit_code,
                    "error": record.error,
                    "limits": record.limits,
                },
            )

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        return self.jobs.get(job_id)

    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[JobRecord]:
        records = list(self.jobs.values())
        if status:
            records = [job for job in records if job.status == status]
        records.sort(key=lambda r: r.created_at, reverse=True)
        return records[offset : offset + limit]

    def to_schema(self, record: JobRecord) -> schemas.Job:
        return schemas.Job(
            id=record.id,
            name=record.name,
            status=record.status,
            started_at=record.started_at,
            finished_at=record.finished_at,
            policy=record.policy_name,
            execution_mode=record.execution_mode,
            image=record.image,
            limits=record.limits,
            exit_code=record.exit_code,
            error=record.error,
        )

    def job_logs(self, job_id: str, offset: int = 0) -> str:
        return self.storage.read_log(job_id, offset=offset)

    def list_artifacts(self, job_id: str) -> List[Dict[str, Any]]:
        artifacts = []
        for path in self.storage.list_artifacts(job_id):
            artifacts.append({
                "name": path.name,
                "size": path.stat().st_size,
                "download_url": f"{settings.api_prefix}/jobs/{job_id}/artifacts/{path.name}",
            })
        return artifacts


__all__ = ["Orchestrator", "JobRecord", "TERMINAL_STATUSES"]
