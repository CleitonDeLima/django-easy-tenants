import threading
from contextlib import contextmanager

from django.apps import apps
from django.conf import settings

__version__ = '0.1.0'
thread_local = threading.local()


def get_tenant_model():
    return apps.get_model(*settings.EASY_TENANTS_TENANT_MODEL.split('.'))


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
