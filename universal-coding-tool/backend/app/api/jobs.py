"""Job related API endpoints."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..core import schemas
from ..core.auth import require_user
from ..core.orchestrator import Orchestrator

router = APIRouter()


def get_orchestrator(request: Request) -> Orchestrator:
    orchestrator: Orchestrator = request.app.state.orchestrator
    return orchestrator


@router.post("/jobs", response_model=schemas.Job, status_code=201)
async def create_job(
    payload: schemas.JobCreate,
    request: Request,
    _: str = Depends(require_user),
) -> schemas.Job:
    orchestrator = get_orchestrator(request)
    record = await orchestrator.submit_job(payload)
    return orchestrator.to_schema(record)


@router.get("/jobs", response_model=List[schemas.Job])
async def list_jobs(
    request: Request,
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(require_user),
) -> List[schemas.Job]:
    orchestrator = get_orchestrator(request)
    records = orchestrator.list_jobs(status=status, limit=limit, offset=offset)
    return [orchestrator.to_schema(record) for record in records]


@router.get("/jobs/{job_id}", response_model=schemas.Job)
async def get_job(
    job_id: str,
    request: Request,
    _: str = Depends(require_user),
) -> schemas.Job:
    orchestrator = get_orchestrator(request)
    record = orchestrator.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")
    return orchestrator.to_schema(record)
