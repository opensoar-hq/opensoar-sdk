# OpenSOAR SDK

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
