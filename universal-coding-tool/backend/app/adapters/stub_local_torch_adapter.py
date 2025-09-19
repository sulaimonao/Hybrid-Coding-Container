"""Placeholder adapter for future local PyTorch integrations."""
from __future__ import annotations

from typing import Any, Dict

from .base import ModelAdapter, registry


class StubLocalTorchAdapter(ModelAdapter):
    name = "local-torch"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "not-implemented",
            "message": "Local torch adapter is a stub and does not execute.",
            "payload": payload,
        }


registry.register(StubLocalTorchAdapter())
