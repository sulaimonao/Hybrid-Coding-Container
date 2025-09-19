"""Placeholder adapter for future OpenAI integrations."""
from __future__ import annotations

from typing import Any, Dict

from .base import ModelAdapter, registry


class StubOpenAIAdapter(ModelAdapter):
    name = "openai"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "not-implemented",
            "message": "OpenAI adapter is a stub and does not execute.",
            "payload": payload,
        }


registry.register(StubOpenAIAdapter())
