"""Policy engine responsible for selecting execution backends."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable

from .logging import logger


class PolicyEngine:
    """Loads and resolves execution policies from disk."""

    def __init__(self, policy_path: Path) -> None:
        self.policy_path = policy_path
        self._policies: Dict[str, Dict[str, object]] = {}
        self.reload()

    def reload(self) -> None:
        if not self.policy_path.exists():
            logger.warning("Policy file %s not found; using empty policy set", self.policy_path)
            self._policies = {}
            return
        with self.policy_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("Policy file must contain a JSON object")
        self._policies = data
        logger.info("Loaded %s policies", len(self._policies))

    def get_policy(self, name: str) -> Dict[str, object]:
        policy = self._policies.get(name)
        if not policy:
            raise KeyError(f"Unknown policy '{name}'")
        return policy

    def list_policies(self) -> Dict[str, Dict[str, object]]:
        return self._policies

    def available_policies(self) -> Iterable[str]:
        return self._policies.keys()
