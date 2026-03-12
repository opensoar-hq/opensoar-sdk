"""Tests for SDK data models."""

from __future__ import annotations

from opensoar_sdk.models import (
    Alert,
    AlertStatus,
    Enrichment,
    IOC,
    Severity,
)
from opensoar_sdk.testing import mock_alert


class TestIOC:
    def test_create_ioc(self):
        ioc = IOC(type="ip", value="1.2.3.4", source="virustotal", tags=["malware"])
        assert ioc.type == "ip"
        assert ioc.value == "1.2.3.4"
        assert ioc.tags == ["malware"]

    def test_ioc_defaults(self):
        ioc = IOC(type="domain", value="evil.com")
        assert ioc.source is None
        assert ioc.tags == []
        assert ioc.metadata == {}


class TestEnrichment:
    def test_create_enrichment(self):
        e = Enrichment(source="vt", data={"score": 85}, malicious=True, score=85.0)
        assert e.malicious is True
        assert e.score == 85.0

    def test_enrichment_defaults(self):
        e = Enrichment(source="test", data={})
        assert e.malicious is False
        assert e.score is None
        assert e.tags == []


class TestAlert:
    def test_default_alert(self):
        alert = Alert()
        assert alert.severity == Severity.MEDIUM
        assert alert.status == AlertStatus.NEW
        assert alert.iocs == []

    def test_alert_with_iocs(self):
        ioc = IOC(type="ip", value="10.0.0.1")
        alert = Alert(title="Test", iocs=[ioc])
        assert len(alert.iocs) == 1
        assert alert.iocs[0].value == "10.0.0.1"


class TestMockAlert:
    def test_mock_alert_defaults(self):
        alert = mock_alert()
        assert alert.title == "Test Alert"
        assert alert.severity == Severity.MEDIUM
        assert alert.id  # non-empty

    def test_mock_alert_string_severity(self):
        alert = mock_alert(severity="critical")
        assert alert.severity == Severity.CRITICAL

    def test_mock_alert_custom_fields(self):
        alert = mock_alert(
            title="Brute Force",
            severity="high",
            source_ip="192.168.1.1",
            tags=["brute-force"],
        )
        assert alert.title == "Brute Force"
        assert alert.source_ip == "192.168.1.1"
        assert alert.tags == ["brute-force"]
