"""Log streaming endpoints."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from ..core.auth import require_user
from ..core.orchestrator import TERMINAL_STATUSES
from .jobs import get_orchestrator

router = APIRouter()


@router.get("/jobs/{job_id}/logs/stream")
async def stream_logs(
    job_id: str,
    request: Request,
    _: str = Depends(require_user),
) -> StreamingResponse:
    orchestrator = get_orchestrator(request)
    record = orchestrator.get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_stream() -> AsyncIterator[bytes]:
        offset = 0
        while True:
            chunk = orchestrator.job_logs(job_id, offset=offset)
            if chunk:
                offset += len(chunk.encode("utf-8"))
                yield f"data: {chunk}\n\n".encode("utf-8")
            record_ref = orchestrator.get_job(job_id)
            if record_ref and record_ref.status in TERMINAL_STATUSES and not chunk:
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
