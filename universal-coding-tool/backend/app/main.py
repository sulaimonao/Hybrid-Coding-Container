"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .adapters import registry  # noqa: F401  # ensure adapters register
from .core.docker_runner import DockerRunner
from .core.logging import configure_logging
from .core.orchestrator import Orchestrator
from .core.policy_engine import PolicyEngine
from .core.settings import settings
from .core.storage import Storage
from .core.vm_runner import VMRunner

configure_logging()


def create_app() -> FastAPI:
    policy_engine = PolicyEngine(settings.policy_file)
    storage = Storage(settings.job_root)
    docker_runner = DockerRunner()
    vm_runner = VMRunner()
    orchestrator = Orchestrator(
        storage_backend=storage,
        policy_engine=policy_engine,
        docker_runner=docker_runner,
        vm_runner=vm_runner,
    )

    app = FastAPI(title="Universal Coding Tool", version="0.1.0")
    app.state.orchestrator = orchestrator

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event() -> None:
        await orchestrator.start()

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        await orchestrator.shutdown()

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
