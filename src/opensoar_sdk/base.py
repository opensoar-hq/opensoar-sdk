"""Base class for OpenSOAR integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HealthCheckResult:
    """Result of an integration health check."""

    healthy: bool
    message: str
    details: dict[str, Any] | None = None


@dataclass
class ActionDefinition:
    """Describes an action exposed by an integration."""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    returns: dict[str, Any] = field(default_factory=dict)


class Integration(ABC):
    """Abstract base class for all OpenSOAR integrations.

    Subclasses must set ``integration_type``, ``display_name``, and
    ``description`` as class-level attributes, and implement the four
    abstract methods below.

    Example::

        class VirusTotal(Integration):
            integration_type = "virustotal"
            display_name = "VirusTotal"
            description = "Look up IPs, domains, and file hashes."

            def _validate_config(self, config):
                if "api_key" not in config:
                    raise ValueError("Missing api_key")

            async def connect(self):
                self.session = aiohttp.ClientSession(...)

            async def health_check(self):
                return HealthCheckResult(healthy=True, message="OK")

            def get_actions(self):
                return [ActionDefinition(name="lookup_ip", description="...")]
    """

    integration_type: str
    display_name: str
    description: str

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._validate_config(self._config)

    @property
    def config(self) -> dict[str, Any]:
        """Return the integration configuration dict."""
        return self._config

    @abstractmethod
    def _validate_config(self, config: dict[str, Any]) -> None:
        """Validate the supplied configuration, raising on errors."""
        ...

    @abstractmethod
    async def connect(self) -> None:
        """Establish connections to the external service."""
        ...

    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """Return a health-check result for this integration."""
        ...

    @abstractmethod
    def get_actions(self) -> list[ActionDefinition]:
        """Return the list of actions this integration provides."""
        ...

    async def disconnect(self) -> None:
        """Tear down connections. Override if cleanup is needed."""
        pass
