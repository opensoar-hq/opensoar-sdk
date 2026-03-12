"""Decorators for defining SOAR actions and playbooks."""

from __future__ import annotations

import asyncio
import functools
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from opensoar_sdk.context import get_run_context

logger = logging.getLogger(__name__)


@dataclass
class ActionMeta:
    """Metadata attached to an @action-decorated function."""

    name: str
    timeout: int = 300
    retries: int = 0
    retry_backoff: float = 1.0
    description: str = ""


@dataclass
class PlaybookMeta:
    """Metadata attached to an @playbook-decorated function."""

    name: str
    trigger: str | None = None
    conditions: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    enabled: bool = True


@dataclass
class RegisteredPlaybook:
    """A playbook registered in the global registry."""

    meta: PlaybookMeta
    func: Callable
    module: str


_PLAYBOOK_REGISTRY: dict[str, RegisteredPlaybook] = {}


def get_playbook_registry() -> dict[str, RegisteredPlaybook]:
    """Return the global playbook registry."""
    return _PLAYBOOK_REGISTRY


def action(
    name: str | None = None,
    *,
    timeout: int = 300,
    retries: int = 0,
    retry_backoff: float = 1.0,
    description: str = "",
) -> Callable:
    """Decorate an async function as a SOAR action.

    Actions gain automatic timeout enforcement, retry logic, and execution
    tracking when run inside a :class:`RunContext`.

    Args:
        name: Override the action name (defaults to the function name).
        timeout: Maximum seconds the action may run before being cancelled.
        retries: Number of retry attempts after an initial failure.
        retry_backoff: Exponential back-off base in seconds between retries.
        description: Human-readable description of the action.
    """

    def decorator(func: Callable) -> Callable:
        meta = ActionMeta(
            name=name or func.__name__,
            timeout=timeout,
            retries=retries,
            retry_backoff=retry_backoff,
            description=description,
        )

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = get_run_context()

            # Outside a run context, just call the function directly.
            if ctx is None:
                return await func(*args, **kwargs)

            started_at = datetime.now(timezone.utc)
            last_error: str | None = None

            for attempt in range(1, meta.retries + 2):
                try:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs), timeout=meta.timeout
                    )

                    if ctx.record_action:
                        await ctx.record_action(
                            action_name=meta.name,
                            status="success",
                            started_at=started_at,
                            finished_at=datetime.now(timezone.utc),
                            output_data=(
                                result if isinstance(result, dict) else {"result": result}
                            ),
                            attempt=attempt,
                        )
                    return result

                except asyncio.TimeoutError:
                    last_error = f"Timeout after {meta.timeout}s"
                    if attempt <= meta.retries:
                        await asyncio.sleep(meta.retry_backoff ** attempt)
                        continue

                    if ctx.record_action:
                        await ctx.record_action(
                            action_name=meta.name,
                            status="failed",
                            started_at=started_at,
                            finished_at=datetime.now(timezone.utc),
                            error=last_error,
                            attempt=attempt,
                        )
                    raise

                except Exception as e:
                    last_error = str(e)
                    if attempt <= meta.retries:
                        await asyncio.sleep(meta.retry_backoff ** attempt)
                        continue

                    if ctx.record_action:
                        await ctx.record_action(
                            action_name=meta.name,
                            status="failed",
                            started_at=started_at,
                            finished_at=datetime.now(timezone.utc),
                            error=last_error,
                            attempt=attempt,
                        )
                    raise

            raise RuntimeError(
                f"Action {meta.name} failed after {meta.retries + 1} attempts"
            )

        wrapper._soar_action = meta  # type: ignore[attr-defined]
        return wrapper

    return decorator


def playbook(
    trigger: str | None = None,
    *,
    conditions: dict[str, Any] | None = None,
    description: str = "",
    name: str | None = None,
) -> Callable:
    """Decorate an async function as a SOAR playbook.

    Playbooks are automatically registered in a global registry so the
    engine can discover and invoke them.

    Args:
        trigger: Event type that triggers this playbook (e.g. ``"webhook"``).
        conditions: Dict of field-name to acceptable values for auto-trigger.
        description: Human-readable description of the playbook.
        name: Override the playbook name (defaults to the function name).
    """

    def decorator(func: Callable) -> Callable:
        meta = PlaybookMeta(
            name=name or func.__name__,
            trigger=trigger,
            conditions=conditions or {},
            description=description,
        )
        func._soar_playbook = meta  # type: ignore[attr-defined]

        _PLAYBOOK_REGISTRY[meta.name] = RegisteredPlaybook(
            meta=meta,
            func=func,
            module=func.__module__,
        )

        return func

    return decorator
