"""Test helpers for playbook and integration authors."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from opensoar_sdk.context import RunContext, set_run_context
from opensoar_sdk.models import Alert, AlertStatus, IOC, Severity


def mock_alert(
    *,
    title: str = "Test Alert",
    severity: str | Severity = Severity.MEDIUM,
    status: str | AlertStatus = AlertStatus.NEW,
    source: str = "test",
    source_ip: str | None = None,
    dest_ip: str | None = None,
    raw_event: dict[str, Any] | None = None,
    iocs: list[IOC] | None = None,
    tags: list[str] | None = None,
) -> Alert:
    """Create a mock :class:`Alert` for testing playbooks.

    All fields have sensible defaults so you only need to specify the
    fields relevant to your test.
    """
    if isinstance(severity, str):
        severity = Severity(severity)
    if isinstance(status, str):
        status = AlertStatus(status)

    return Alert(
        id=str(uuid.uuid4()),
        title=title,
        severity=severity,
        status=status,
        source=source,
        source_ip=source_ip,
        dest_ip=dest_ip,
        raw_event=raw_event or {},
        iocs=iocs or [],
        tags=tags or [],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@asynccontextmanager
async def mock_run_context(
    *,
    run_id: str | None = None,
    recorded_actions: list[dict[str, Any]] | None = None,
):
    """Provide a :class:`RunContext` for testing.

    Actions executed inside this context manager will have their calls
    recorded in *recorded_actions* (pass your own list to inspect them
    after the test).

    Example::

        actions: list[dict] = []
        async with mock_run_context(recorded_actions=actions):
            await my_action("arg")
        assert actions[0]["action_name"] == "my_action"
    """
    if recorded_actions is None:
        recorded_actions = []

    async def _record(**kwargs: Any) -> None:
        recorded_actions.append(kwargs)

    ctx = RunContext(
        run_id=run_id or str(uuid.uuid4()),
        record_action=_record,
    )
    set_run_context(ctx)
    try:
        yield ctx
    finally:
        set_run_context(None)
