import functools
from contextlib import ContextDecorator
from contextvars import ContextVar

from asgiref.sync import iscoroutinefunction

from easy_tenants.exceptions import TenantError

state = ContextVar("tenant-state", default=None)


def get_state():
    return state.get() or {"enabled": True, "tenant": None}


def get_current_tenant():
    state = get_state()

    if state["enabled"] and state["tenant"] is None:
        raise TenantError("Tenant is required in context.")

    return state["tenant"]


class tenant_context(ContextDecorator):
    """
    Activate `tenant` (or disable the tenant filter with `enabled=False`)
    inside a `with` block or a decorated function, sync or async.
    """

    def __init__(self, tenant=None, enabled=True):
        self.tenant = tenant
        self.enabled = enabled

    def _recreate_cm(self):
        # Each decorated call gets its own instance, so concurrent or
        # recursive calls don't share the snapshot of the previous state.
        return type(self)(self.tenant, self.enabled)

    def __enter__(self):
        self._previous_state = get_state()

        new_state = self._previous_state.copy()
        new_state["enabled"] = self.enabled
        new_state["tenant"] = self.tenant

        state.set(new_state)

    def __exit__(self, *exc_info):
        state.set(self._previous_state)

    def __call__(self, func):
        if not iscoroutinefunction(func):
            return super().__call__(func)

        # ContextDecorator's wrapper is sync: on an `async def` it would
        # leave the block before the coroutine is awaited.
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            with self._recreate_cm():
                return await func(*args, **kwargs)

        return inner


def tenant_context_disabled():
    return tenant_context(enabled=False)
