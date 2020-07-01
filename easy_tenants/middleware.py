from django.contrib.auth.middleware import AuthenticationMiddleware
from django.shortcuts import redirect

from easy_tenants import get_tenant_model, set_current_tenant
from easy_tenants.conf import settings


def _tenant_not_required(view_func):
    """
    By default all views need a defined tenant, not when you have
    tenant_required = False
    """
    if not getattr(view_func, 'tenant_required', True):
        return True

    view_class = getattr(view_func, 'view_class', None)
    if view_class and not getattr(view_class, 'tenant_required', True):
        return True

    return False


def _get_tenant(request):
    """Get tenant saved in session request"""
    tenant = None
    tenant_id = request.session.get(
        settings.EASY_TENANTS_SESSION_KEY, None
    )

    if tenant_id:
        tenant = get_tenant_model().objects.filter(id=tenant_id).first()

    return tenant


class DefaultTenantMiddleware(AuthenticationMiddleware):
    """
    Middleware guarantees that the user will be authenticated and with
    a defined tenant.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        request.tenant = _get_tenant(request)
        set_current_tenant(request.tenant)

        if not request.tenant and not _tenant_not_required(view_func):
            return redirect(settings.EASY_TENANTS_REDIRECT_URL)
