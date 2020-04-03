from easy_tenants.utils import (
    get_tenant_model, get_current_tenant, set_current_tenant, tenant_context
)

__all__ = [
    'get_tenant_model', 'get_current_tenant', 'set_current_tenant',
    'tenant_context',
]

default_app_config = 'easy_tenants.apps.EasyTenantsConfig'
