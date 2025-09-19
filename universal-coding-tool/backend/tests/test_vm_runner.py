from __future__ import annotations

from pathlib import Path

from app.core.vm_runner import VMRunner


def test_vm_runner_builds_command(tmp_path: Path, monkeypatch) -> None:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    script = scripts_dir / "run_in_guest.sh"
    script.write_text("#!/bin/bash\nexit 0\n")
    from app.core import vm_runner
    monkeypatch.setattr(vm_runner.settings, "vm_scripts_dir", scripts_dir)
    runner = VMRunner(scripts_dir=scripts_dir)
    policy = {"runner": "vm", "vm": {"cpus": 2, "memory": "4g"}}
    spec = runner.build_run_command(
        job_id="job123",
        workspace=tmp_path,
        policy=policy,
        env={"HELLO": "WORLD"},
    )
    assert script.as_posix() in spec["command"][0]
    assert "job123" in spec["command"]
    assert spec["cpus"] == 2
