"""Base interface for model adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class ModelAdapter(ABC):
    """Abstract base class for future model integrations."""

    name: str = "base"

    @abstractmethod
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the adapter using the provided payload."""


class AdapterRegistry:
    """Simple in-memory registry for adapters."""

    def __init__(self) -> None:
        self._registry: Dict[str, ModelAdapter] = {}

    def register(self, adapter: ModelAdapter) -> None:
        self._registry[adapter.name] = adapter

    def get(self, name: str) -> ModelAdapter:
        return self._registry[name]

    def available(self) -> Dict[str, ModelAdapter]:
        return dict(self._registry)


registry = AdapterRegistry()
