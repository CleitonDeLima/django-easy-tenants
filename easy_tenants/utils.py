import threading
from contextlib import contextmanager

from django.apps import apps

from easy_tenants.conf import settings
from easy_tenants.exceptions import TenantError

state_local = threading.local()


def get_tenant_model():
    return apps.get_model(*settings.EASY_TENANTS_MODEL.split("."))


def get_state():
    state_default = {
        "enabled": True,
        "tenant": None,
    }
    state = getattr(state_local, "state", state_default)
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

    state_local.state = new_state

    try:
        yield
    finally:
        state_local.state = previous_state


@contextmanager
def tenant_context_disabled():
    with tenant_context(enabled=False):
        yield
