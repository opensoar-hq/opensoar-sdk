<p align="center">
  <img src="https://raw.githubusercontent.com/opensoar-hq/opensoar-www/main/public/logo.svg" width="64" height="62" alt="OpenSOAR">
</p>

<h1 align="center">OpenSOAR SDK</h1>

<p align="center"><strong>Build OpenSOAR integrations and playbooks in real Python.</strong></p>

<p align="center">
  <a href="https://pypi.org/project/opensoar-sdk/"><img src="https://img.shields.io/pypi/v/opensoar-sdk?color=3775A9&logo=pypi&logoColor=white" alt="PyPI"></a>
  <a href="https://github.com/opensoar-hq/opensoar-core"><img src="https://img.shields.io/badge/platform-opensoar--core-3fb950" alt="opensoar-core"></a>
</p>

<p align="center"><sub>OpenSOAR is a <a href="https://0sec.ai">0sec Labs</a> product.</sub></p>

---

Python SDK for building integrations and playbooks for the [OpenSOAR](https://github.com/opensoar-hq/opensoar-core) SOAR platform.

## Install

```bash
pip install opensoar-sdk
```

## Build an Integration

```python
from opensoar_sdk import Integration, action

class MyIntegration(Integration):
    name = "my-tool"

    async def connect(self):
        self.client = MyToolClient(self.config["api_key"])

    async def health_check(self) -> bool:
        return await self.client.ping()

    @action(timeout=30, retries=2)
    async def lookup_ip(self, ip: str) -> dict:
        return await self.client.query(ip)
```

## Write a Playbook

```python
from opensoar_sdk import playbook, action

@playbook(trigger="webhook", conditions={"severity": ["high", "critical"]})
async def triage_alert(alert):
    result = await enrich_ip(alert.source_ip)
    if result.malicious:
        await block_ip(alert.source_ip)
        await notify_slack(f"Blocked {alert.source_ip}")
```

## Testing

```python
from opensoar_sdk.testing import mock_alert, mock_run_context

async def test_my_playbook():
    alert = mock_alert(severity="high", source_ip="1.2.3.4")
    async with mock_run_context():
        await triage_alert(alert)
```

## Part of OpenSOAR

See the [main repo](https://github.com/opensoar-hq/opensoar-core) for full documentation.
