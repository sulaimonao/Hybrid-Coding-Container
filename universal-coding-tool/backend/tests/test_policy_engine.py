from __future__ import annotations

import json
from pathlib import Path

from app.core.policy_engine import PolicyEngine


def test_policy_engine_loads(tmp_path: Path) -> None:
    policy_file = tmp_path / "policies.json"
    policy_file.write_text(
        json.dumps(
            {
                "safe-default": {
                    "runner": "container",
                    "docker": {"cpus": 1},
                }
            }
        )
    )

    engine = PolicyEngine(policy_file)
    policy = engine.get_policy("safe-default")
    assert policy["runner"] == "container"
    assert "docker" in policy
    assert "safe-default" in list(engine.available_policies())
