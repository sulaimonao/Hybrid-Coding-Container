from __future__ import annotations

from pathlib import Path

from app.core.docker_runner import DockerRunner


def test_docker_spec_from_policy(tmp_path: Path) -> None:
    runner = DockerRunner()
    workspace = tmp_path / "job"
    workspace.mkdir()
    policy = {
        "runner": "container",
        "docker": {
            "cpus": 1,
            "memory": "1g",
            "pids_limit": 128,
            "network": "none",
            "read_only_root": True,
            "cap_drop": ["ALL"],
            "no_new_privileges": True,
            "tmpfs": {"/tmp": "rw,nosuid,noexec,size=64m"},
        },
    }

    spec = runner._policy_to_spec(  # type: ignore[attr-defined]
        image="uct-python:latest",
        command="python main.py",
        workspace=workspace,
        policy=policy,
        env={"FOO": "BAR"},
    )

    assert spec.image == "uct-python:latest"
    assert spec.network_mode == "none"
    assert spec.read_only is True
    assert spec.env["FOO"] == "BAR"
    assert spec.env["JOB_CMD"] == "python main.py"
    assert spec.tmpfs["/tmp"].startswith("rw")
    cmd = list(runner.build_docker_command(spec))
    assert "--read-only" in cmd
    assert "--cap-drop" in cmd
