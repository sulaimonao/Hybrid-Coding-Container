"""Placeholder adapter for future HuggingFace integrations."""
from __future__ import annotations

from typing import Any, Dict

from .base import ModelAdapter, registry


class StubHFAdapter(ModelAdapter):
    name = "huggingface"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "not-implemented",
            "message": "HuggingFace adapter is a stub and does not execute.",
            "payload": payload,
        }


registry.register(StubHFAdapter())
