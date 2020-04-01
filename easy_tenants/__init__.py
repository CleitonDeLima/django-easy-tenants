import threading
from contextlib import contextmanager

from django.apps import apps

from easy_tenants.conf import settings

thread_local = threading.local()


def get_tenant_model():
    return apps.get_model(*settings.EASY_TENANTS_MODEL.split('.'))


def get_current_tenant():
    return getattr(thread_local, 'tenant', None)


def set_current_tenant(tenant):
    setattr(thread_local, 'tenant', tenant)


@contextmanager
def tenant_context(tenant):
    previous_tenant = get_current_tenant()
    set_current_tenant(tenant)
    yield
    set_current_tenant(previous_tenant)
