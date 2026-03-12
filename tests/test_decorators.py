"""Tests for @action and @playbook decorators."""

from __future__ import annotations

import asyncio

import pytest

from opensoar_sdk import action, playbook
from opensoar_sdk.decorators import ActionMeta, PlaybookMeta, get_playbook_registry
from opensoar_sdk.testing import mock_run_context


# ---------------------------------------------------------------------------
# @action
# ---------------------------------------------------------------------------


class TestAction:
    @pytest.mark.asyncio
    async def test_basic_call_without_context(self):
        @action()
        async def greet(name: str) -> str:
            return f"hello {name}"

        result = await greet("world")
        assert result == "hello world"

    @pytest.mark.asyncio
    async def test_action_meta_attached(self):
        @action(name="custom_name", timeout=10, retries=3, description="desc")
        async def do_thing():
            return True

        meta: ActionMeta = do_thing._soar_action
        assert meta.name == "custom_name"
        assert meta.timeout == 10
        assert meta.retries == 3
        assert meta.description == "desc"

    @pytest.mark.asyncio
    async def test_action_records_success(self):
        @action()
        async def add(a: int, b: int) -> dict:
            return {"sum": a + b}

        actions: list[dict] = []
        async with mock_run_context(recorded_actions=actions):
            result = await add(2, 3)

        assert result == {"sum": 5}
        assert len(actions) == 1
        assert actions[0]["status"] == "success"
        assert actions[0]["action_name"] == "add"
        assert actions[0]["output_data"] == {"sum": 5}

    @pytest.mark.asyncio
    async def test_action_records_failure(self):
        @action()
        async def fail():
            raise ValueError("boom")

        actions: list[dict] = []
        async with mock_run_context(recorded_actions=actions):
            with pytest.raises(ValueError, match="boom"):
                await fail()

        assert len(actions) == 1
        assert actions[0]["status"] == "failed"
        assert actions[0]["error"] == "boom"

    @pytest.mark.asyncio
    async def test_action_retries(self):
        call_count = 0

        @action(retries=2, retry_backoff=0.01)
        async def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("not yet")
            return "ok"

        actions: list[dict] = []
        async with mock_run_context(recorded_actions=actions):
            result = await flaky()

        assert result == "ok"
        assert call_count == 3
        assert actions[0]["status"] == "success"
        assert actions[0]["attempt"] == 3

    @pytest.mark.asyncio
    async def test_action_timeout(self):
        @action(timeout=0.05)
        async def slow():
            await asyncio.sleep(10)

        actions: list[dict] = []
        async with mock_run_context(recorded_actions=actions):
            with pytest.raises(asyncio.TimeoutError):
                await slow()

        assert actions[0]["status"] == "failed"


# ---------------------------------------------------------------------------
# @playbook
# ---------------------------------------------------------------------------


class TestPlaybook:
    def test_playbook_registers(self):
        @playbook(trigger="webhook", conditions={"severity": ["high"]})
        async def my_playbook(alert):
            pass

        registry = get_playbook_registry()
        assert "my_playbook" in registry
        entry = registry["my_playbook"]
        assert entry.meta.trigger == "webhook"
        assert entry.meta.conditions == {"severity": ["high"]}
        assert entry.func is my_playbook

    def test_playbook_meta_attached(self):
        @playbook(name="custom", description="a playbook")
        async def another(alert):
            pass

        meta: PlaybookMeta = another._soar_playbook
        assert meta.name == "custom"
        assert meta.description == "a playbook"
