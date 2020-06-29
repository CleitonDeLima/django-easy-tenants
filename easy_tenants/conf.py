"""Settings for easy_tenants"""

from appconf import AppConf
from django.conf import settings  # NOQA

__all__ = ('settings', 'EasyTenantsAppConf')


class EasyTenantsAppConf(AppConf):
    MODEL = None
    IGNORE_URLS = []
    REDIRECT_URL = None
    SUCCESS_URL = None
    SESSION_KEY = 'tenant_id'

    class Meta:
        prefix = 'EASY_TENANTS'
