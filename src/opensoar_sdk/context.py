"""Run context management via contextvars."""

from __future__ import annotations

import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class RunContext:
    """Execution context for a playbook run.

    Stores the current run ID and an optional callback that actions use
    to report their execution results back to the engine.
    """

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    record_action: Callable[..., Any] | None = None


_run_context: ContextVar[RunContext | None] = ContextVar(
    "_run_context", default=None
)


def get_run_context() -> RunContext | None:
    """Return the current run context, or ``None`` outside a playbook run."""
    return _run_context.get(None)


def set_run_context(ctx: RunContext | None) -> None:
    """Set (or clear) the run context for the current task."""
    _run_context.set(ctx)
