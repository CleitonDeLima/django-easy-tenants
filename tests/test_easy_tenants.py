import asyncio

import pytest

from easy_tenants import (
    get_current_tenant,
    tenant_context,
    tenant_context_disabled,
)
from easy_tenants.utils import get_state
from tests.models import StoreTenant

DEFAULT_STATE = {"enabled": True, "tenant": None}


def test_get_and_set_current_tenant_thread_local(db):
    tenant = StoreTenant.objects.create()
    with tenant_context(tenant):
        assert tenant == get_current_tenant()


def test_tenant_context(db):
    tenant1 = StoreTenant.objects.create()
    tenant2 = StoreTenant.objects.create()

    with tenant_context(tenant1):
        with tenant_context(tenant2):
            assert tenant2 == get_current_tenant()

        assert tenant1 == get_current_tenant()


def test_tenant_context_disabled():
    with tenant_context_disabled():
        assert get_state() == {"enabled": False, "tenant": None}

    assert get_state() == DEFAULT_STATE


def test_tenant_context_decorator_sync():
    tenant = object()

    @tenant_context(tenant)
    def func():
        return get_state()

    assert func() == {"enabled": True, "tenant": tenant}
    assert get_state() == DEFAULT_STATE


def test_tenant_context_decorator_async():
    tenant = object()

    @tenant_context(tenant)
    async def func():
        await asyncio.sleep(0)
        return get_state()

    assert asyncio.run(func()) == {"enabled": True, "tenant": tenant}
    assert get_state() == DEFAULT_STATE


def test_tenant_context_disabled_decorator_sync():
    @tenant_context_disabled()
    def func():
        return get_state()

    assert func() == {"enabled": False, "tenant": None}
    assert get_state() == DEFAULT_STATE


def test_tenant_context_disabled_decorator_async():
    @tenant_context_disabled()
    async def func():
        await asyncio.sleep(0)
        return get_state()

    assert asyncio.run(func()) == {"enabled": False, "tenant": None}
    assert get_state() == DEFAULT_STATE


def test_decorator_can_be_called_repeatedly():
    tenant1 = object()
    tenant2 = object()

    @tenant_context(tenant2)
    def func():
        return get_current_tenant()

    with tenant_context(tenant1):
        assert func() is tenant2
        assert func() is tenant2
        assert get_current_tenant() is tenant1


def test_decorator_sync_restores_state_after_exception():
    tenant = object()

    @tenant_context(tenant)
    def func():
        assert get_current_tenant() is tenant
        raise ValueError

    with tenant_context_disabled():
        with pytest.raises(ValueError):
            func()

        assert get_state() == {"enabled": False, "tenant": None}

    assert get_state() == DEFAULT_STATE


def test_decorator_async_restores_state_after_exception():
    tenant = object()

    @tenant_context(tenant)
    async def func():
        await asyncio.sleep(0)
        assert get_current_tenant() is tenant
        raise ValueError

    async def main():
        with tenant_context_disabled():
            with pytest.raises(ValueError):
                await func()

            return get_state()

    assert asyncio.run(main()) == {"enabled": False, "tenant": None}
    assert get_state() == DEFAULT_STATE


def test_disabled_decorator_async_restores_state_after_exception():
    tenant = object()

    @tenant_context_disabled()
    async def func():
        await asyncio.sleep(0)
        assert get_state()["enabled"] is False
        raise ValueError

    async def main():
        with tenant_context(tenant):
            with pytest.raises(ValueError):
                await func()

            return get_state()

    assert asyncio.run(main()) == {"enabled": True, "tenant": tenant}
    assert get_state() == DEFAULT_STATE


def test_decorator_async_concurrent_calls_restore_their_own_state():
    tenant1 = object()
    tenant2 = object()

    @tenant_context_disabled()
    async def func(started, release):
        started.set()
        await release.wait()
        return get_state()["enabled"]

    async def call(tenant, started, release):
        with tenant_context(tenant):
            assert await func(started, release) is False
            return get_current_tenant()

    async def main():
        started1, started2 = asyncio.Event(), asyncio.Event()
        release1, release2 = asyncio.Event(), asyncio.Event()
        task1 = asyncio.create_task(call(tenant1, started1, release1))
        task2 = asyncio.create_task(call(tenant2, started2, release2))
        await started1.wait()
        await started2.wait()
        release1.set()
        result1 = await task1
        release2.set()
        result2 = await task2
        return result1, result2

    assert asyncio.run(main()) == (tenant1, tenant2)
    assert get_state() == DEFAULT_STATE
