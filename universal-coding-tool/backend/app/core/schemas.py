"""Pydantic schemas shared across the API surface."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    """Schema used when a client submits a new job."""

    name: str
    lang: Literal["python", "node", "rust"]
    files: List[Dict[str, str]] = Field(
        default_factory=list, description="Collection of source files for the job."
    )
    cmd: str
    policy: Literal["safe-default", "research", "experimental", "dedicated-vm"]
    env: Optional[Dict[str, str]] = None


class Job(BaseModel):
    """Persisted job metadata returned to clients."""

    id: str
    name: str
    status: Literal[
        "queued", "running", "succeeded", "failed", "infra_error", "cancelled"
    ]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    policy: str
    execution_mode: Literal["container", "dedicated-vm"]
    image: str
    limits: Dict[str, object] = Field(default_factory=dict)
    exit_code: Optional[int] = None
    error: Optional[str] = None


class LogChunk(BaseModel):
    """Represents a chunk of log data streamed to clients."""

    offset: int
    data: str


class Artifact(BaseModel):
    """Metadata for an artifact file produced by a job."""

    name: str
    size: int
    download_url: str
