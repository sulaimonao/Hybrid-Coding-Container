"""Expose adapter registry and ensure stub adapters are loaded."""
from .base import ModelAdapter, registry

# Import adapters to trigger registration side effects.
from . import noop_adapter  # noqa: F401
from . import stub_openai_adapter  # noqa: F401
from . import stub_hf_adapter  # noqa: F401
from . import stub_local_torch_adapter  # noqa: F401

__all__ = ["ModelAdapter", "registry"]
