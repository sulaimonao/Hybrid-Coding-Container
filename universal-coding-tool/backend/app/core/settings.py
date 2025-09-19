"""Application settings and configuration helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the backend services.

    Values are loaded from environment variables prefixed with ``UCT_`` and can
    additionally be defined in a ``.env`` file.
    """

    api_prefix: str = Field(default="/api", description="Prefix for API routes")
    job_root: Path = Field(
        default=Path("~/uct_jobs").expanduser(),
        description="Filesystem root where job workspaces are stored.",
    )
    policy_file: Path = Field(
        default=Path("ops/policies.json"),
        description="Path to the policy definition JSON file.",
    )
    docker_socket: str = Field(
        default="unix:///var/run/docker.sock",
        description="Docker socket used by the container runner.",
    )
    default_language_images: Dict[str, str] = Field(
        default_factory=lambda: {
            "python": "uct-python:latest",
            "node": "uct-node:latest",
            "rust": "uct-rust:latest",
        },
        description="Mapping between language identifiers and container images.",
    )
    session_secret_key: str = Field(
        default="change-me",
        description="Secret key used to sign session cookies.",
    )
    session_cookie_name: str = Field(default="uct_session", description="Cookie name")
    admin_email: str = Field(default="admin@example.com")
    admin_password: str = Field(default="changeme")
    log_level: str = Field(default="INFO")
    vm_vmx_path: Path | None = Field(
        default=None,
        description="Path to the base VMware VMX file used for dedicated VMs.",
    )
    vm_snapshot_name: str = Field(
        default="CLEAN_BASE",
        description="Snapshot name that runners revert to between jobs.",
    )
    vm_scripts_dir: Path = Field(
        default=Path("vm/scripts"),
        description="Directory containing host-side helper scripts for VM ops.",
    )
    default_timeout_seconds: int = Field(
        default=600, description="Maximum execution time for a job in seconds."
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="UCT_", case_sensitive=False)

    def model_post_init(self, __context) -> None:
        object.__setattr__(self, "job_root", Path(self.job_root).expanduser())

        project_root = self._discover_project_root()
        policy_path = self._resolve_relative_path(self.policy_file, project_root, "ops/policies.json")
        vm_scripts_path = self._resolve_relative_path(self.vm_scripts_dir, project_root, "vm/scripts")

        object.__setattr__(self, "policy_file", policy_path)
        object.__setattr__(self, "vm_scripts_dir", vm_scripts_path)

    @staticmethod
    def _discover_project_root() -> Path:
        """Return the repository root by searching upwards for the ops folder."""

        for candidate in Path(__file__).resolve().parents:
            if (candidate / "ops").exists():
                return candidate
        return Path.cwd()

    @staticmethod
    def _resolve_relative_path(path_value: Path | str, project_root: Path, default_subpath: str) -> Path:
        """Convert relative configuration paths into absolute ones."""

        raw_path = Path(path_value).expanduser()
        if raw_path.is_absolute():
            return raw_path

        candidates = [
            project_root / raw_path,
            Path.cwd() / raw_path,
            project_root / default_subpath,
            Path.cwd() / default_subpath,
        ]

        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved.exists():
                return resolved

        # Fall back to project root even if the file/directory has not been created yet.
        return (project_root / raw_path).resolve()


settings = Settings()
