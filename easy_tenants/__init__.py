__version__ = '0.1.0'

import threading

from django.apps import apps
from django.conf import settings

thread_local = threading.local()


def get_tenant_model():
    return apps.get_model(*settings.TENANT_MODEL.split('.'))


def get_current_tenant():
    return getattr(thread_local, 'tenant', None)


def set_current_tenant(tenant):
    setattr(thread_local, 'tenant', tenant)
