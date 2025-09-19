from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.docker_runner import DockerRunner
from app.core.settings import settings
from app.core.vm_runner import VMRunner, VMRunResult
from app.main import create_app
from app.core import orchestrator as orchestrator_module


@pytest.fixture(autouse=True)
def _patch_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    policies = {
        "safe-default": {
            "runner": "container",
            "docker": {
                "cpus": 1,
                "memory": "1g",
                "pids_limit": 64,
                "network": "none",
                "read_only_root": True,
                "tmpfs": {"/tmp": "rw,nosuid,noexec,size=64m"},
            },
        }
    }
    policy_file = tmp_path / "policies.json"
    policy_file.write_text(json.dumps(policies))
    monkeypatch.setattr(settings, "policy_file", policy_file)
    job_root = tmp_path / "jobs"
    monkeypatch.setattr(settings, "job_root", job_root)
    job_root.mkdir()


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    def fake_run(
        self: DockerRunner,
        job_id: str,
        image: str,
        command: str,
        workspace: Path,
        policy: dict[str, Any],
        env: dict[str, str] | None = None,
        log_callback: Any | None = None,
    ) -> int:
        (workspace / "out").mkdir(exist_ok=True)
        (workspace / "out" / "result.txt").write_text("ok")
        if log_callback:
            log_callback("hello from container\n")
        return 0

    def fake_vm_run(
        self: VMRunner,
        job_id: str,
        workspace: Path,
        policy: dict[str, Any],
        env: dict[str, str] | None = None,
        log_callback: Any | None = None,
    ) -> VMRunResult:
        if log_callback:
            log_callback("vm log\n")
        return VMRunResult(exit_code=0, command="vm")

    monkeypatch.setattr(DockerRunner, "run", fake_run, raising=False)
    monkeypatch.setattr(VMRunner, "run", fake_vm_run, raising=False)

    original_submit = orchestrator_module.Orchestrator.submit_job

    async def immediate_submit(self, payload):
        record = await original_submit(self, payload)
        task = self.tasks.get(record.id)
        if task:
            await task
        return record

    monkeypatch.setattr(orchestrator_module.Orchestrator, "submit_job", immediate_submit)

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_create_job(client: TestClient) -> None:
    login_resp = client.post(
        "/api/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    assert login_resp.status_code == 200

    resp = client.post(
        "/api/jobs",
        json={
            "name": "hello_python",
            "lang": "python",
            "files": [{"path": "main.py", "content": "print('hi')"}],
            "cmd": "python main.py",
            "policy": "safe-default",
        },
    )
    assert resp.status_code == 201
    job = resp.json()
    assert job["status"] in {"running", "succeeded"}

    job_detail = client.get(f"/api/jobs/{job['id']}")
    assert job_detail.status_code == 200
    assert job_detail.json()["policy"] == "safe-default"

    artifacts = client.get(f"/api/jobs/{job['id']}/artifacts")
    assert artifacts.status_code == 200
    assert artifacts.json()[0]["name"] == "result.txt"
