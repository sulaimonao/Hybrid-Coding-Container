"""Policy endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.auth import require_user
from ..core.policy_engine import PolicyEngine
from ..core.settings import settings

router = APIRouter()
policy_engine = PolicyEngine(settings.policy_file)


@router.get("/policies")
async def list_policies(_: str = Depends(require_user)) -> dict[str, object]:
    return policy_engine.list_policies()
