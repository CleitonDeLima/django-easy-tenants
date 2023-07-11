"""Settings for easy_tenants"""

from appconf import AppConf
from django.conf import settings  # NOQA

__all__ = ("settings", "EasyTenantsAppConf")


class EasyTenantsAppConf(AppConf):
    TENANT_FIELD = "tenant"
    TENANT_MODEL = ""

    class Meta:
        prefix = "EASY_TENANTS"
