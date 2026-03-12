"""Lightweight data models for playbook type hints.

These are plain dataclasses with no database dependencies, designed for
use inside playbooks and integration actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert lifecycle statuses."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class IOC:
    """Indicator of Compromise."""

    type: str  # e.g. "ip", "domain", "hash", "url", "email"
    value: str
    source: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Enrichment:
    """Result of enriching an IOC or alert field."""

    source: str
    data: dict[str, Any]
    malicious: bool = False
    score: float | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class Alert:
    """A security alert passed to playbooks.

    This is a lightweight representation suitable for SDK consumers.
    The full server-side model adds database columns and relationships.
    """

    id: str = ""
    title: str = ""
    severity: Severity = Severity.MEDIUM
    status: AlertStatus = AlertStatus.NEW
    source: str = ""
    source_ip: str | None = None
    dest_ip: str | None = None
    raw_event: dict[str, Any] = field(default_factory=dict)
    iocs: list[IOC] = field(default_factory=list)
    enrichments: list[Enrichment] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
