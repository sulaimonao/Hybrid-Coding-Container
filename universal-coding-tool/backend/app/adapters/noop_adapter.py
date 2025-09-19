"""No-op adapter used for testing and defaults."""
from __future__ import annotations

from typing import Any, Dict

from .base import ModelAdapter, registry


class NoOpAdapter(ModelAdapter):
    name = "noop"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"echo": payload}


registry.register(NoOpAdapter())
