"""Filesystem helpers for job workspaces, logs and artifacts."""
from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import Dict, Iterable, List, Optional

from .settings import settings


class Storage:
    """Persist job files, metadata and logs on disk."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or settings.job_root).expanduser()
        self._lock = Lock()
        self.root.mkdir(parents=True, exist_ok=True)

    def job_path(self, job_id: str) -> Path:
        return self.root / job_id

    def src_path(self, job_id: str) -> Path:
        return self.job_path(job_id) / "src"

    def out_path(self, job_id: str) -> Path:
        return self.job_path(job_id) / "out"

    def log_file(self, job_id: str) -> Path:
        return self.job_path(job_id) / "logs" / "run.log"

    def meta_file(self, job_id: str) -> Path:
        return self.job_path(job_id) / "meta.json"

    def create_job_workspace(self, job_id: str) -> None:
        job_dir = self.job_path(job_id)
        for sub in ("src", "out", "logs"):
            (job_dir / sub).mkdir(parents=True, exist_ok=True)
        # ensure restrictive permissions by default
        os.chmod(job_dir, 0o755)

    def write_files(self, job_id: str, files: Iterable[Dict[str, str]]) -> None:
        base = self.src_path(job_id)
        for file in files:
            path = file.get("path")
            content = file.get("content", "")
            if not path:
                continue
            target = base / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)

    def write_meta(self, job_id: str, data: Dict[str, object]) -> None:
        meta_path = self.meta_file(job_id)
        with meta_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True, default=str)

    def read_meta(self, job_id: str) -> Dict[str, object]:
        meta_path = self.meta_file(job_id)
        if not meta_path.exists():
            return {}
        with meta_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def append_log(self, job_id: str, message: str) -> int:
        log_path = self.log_file(job_id)
        with self._lock:
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(message)
            return log_path.stat().st_size

    def read_log(self, job_id: str, offset: int = 0) -> str:
        log_path = self.log_file(job_id)
        if not log_path.exists():
            return ""
        with self._lock:
            with log_path.open("r", encoding="utf-8") as fh:
                fh.seek(offset)
                return fh.read()

    def list_artifacts(self, job_id: str) -> List[Path]:
        out_dir = self.out_path(job_id)
        if not out_dir.exists():
            return []
        return [p for p in out_dir.iterdir() if p.is_file()]

    def get_artifact(self, job_id: str, name: str) -> Optional[Path]:
        path = self.out_path(job_id) / name
        if path.exists() and path.is_file():
            return path
        return None


storage = Storage()
