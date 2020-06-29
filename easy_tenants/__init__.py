from easy_tenants.utils import (
    get_tenant_model, get_current_tenant, set_current_tenant, tenant_context
)

__all__ = [
    'get_tenant_model', 'get_current_tenant', 'set_current_tenant',
    'tenant_context', 'tenant_not_required', 'TenantNotRequiredMixin',
]

default_app_config = 'easy_tenants.apps.EasyTenantsConfig'


def tenant_not_required(view_func):
    """
    Decorator for views that marks that the view is accessible without tenants.
    """
    view_func.tenant_required = False
    return view_func


class TenantNotRequiredMixin:
    """
    Mixin for CBV that marks that the view is accessible without tenants.
    """
    tenant_required = False
