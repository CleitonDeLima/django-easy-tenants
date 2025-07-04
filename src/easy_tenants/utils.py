from contextlib import contextmanager
from contextvars import ContextVar

from easy_tenants.exceptions import TenantError

state_local = ContextVar(
    "tenant-state",
    default={
        "enabled": True,
        "tenant": None,
    },
)


def get_state():
    state = state_local.get()
    return state


def get_current_tenant():
    state = get_state()

    if state["enabled"] and state["tenant"] is None:
        raise TenantError("Tenant is required in context.")

    return state["tenant"]


@contextmanager
def tenant_context(tenant=None, enabled=True):
    previous_state = get_state()

    new_state = previous_state.copy()
    new_state["enabled"] = enabled
    new_state["tenant"] = tenant

    state_local.set(new_state)

    try:
        yield
    finally:
        state_local.set(previous_state)


@contextmanager
def tenant_context_disabled():
    with tenant_context(enabled=False):
        yield
