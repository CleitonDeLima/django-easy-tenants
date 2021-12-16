import django

from easy_tenants.utils import (
    get_current_tenant,
    get_tenant_model,
    tenant_context,
    tenant_context_disabled,
)

__all__ = [
    "get_tenant_model",
    "get_current_tenant",
    "tenant_context",
    "tenant_context_disabled",
]

if django.VERSION < (3, 2):
    default_app_config = "easy_tenants.apps.EasyTenantsConfig"
