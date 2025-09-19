"""Artifact endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from ..core.auth import require_user
from .jobs import get_orchestrator

router = APIRouter()


@router.get("/jobs/{job_id}/artifacts")
async def list_artifacts(
    job_id: str,
    request: Request,
    _: str = Depends(require_user),
) -> list[dict[str, object]]:
    orchestrator = get_orchestrator(request)
    record = orchestrator.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    return orchestrator.list_artifacts(job_id)


@router.get("/jobs/{job_id}/artifacts/{name}")
async def download_artifact(
    job_id: str,
    name: str,
    request: Request,
    _: str = Depends(require_user),
) -> FileResponse:
    orchestrator = get_orchestrator(request)
    record = orchestrator.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    path = orchestrator.storage.get_artifact(job_id, name)
    if not path:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(path)
