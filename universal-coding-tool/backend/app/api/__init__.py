"""API router aggregation."""
from fastapi import APIRouter

from . import artifacts, auth, health, jobs, logs, policies

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(policies.router)
api_router.include_router(jobs.router)
api_router.include_router(logs.router)
api_router.include_router(artifacts.router)

__all__ = ["api_router"]
