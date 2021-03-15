from django.conf import settings
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.shortcuts import redirect
from easy_tenants import get_tenant_model, tenant_context


def _tenant_not_required(view_func):
    """
    By default all views need a defined tenant, not when you have
    tenant_required = False
    """
    if not getattr(view_func, "tenant_required", True):
        return True

    view_class = getattr(view_func, "view_class", None)
    if view_class and not getattr(view_class, "tenant_required", True):
        return True

    return False


def _get_tenant(request):
    """Get tenant saved in session request"""
    tenant = None
    tenant_id = request.session.get(settings.EASY_TENANTS_SESSION_KEY, None)

    if tenant_id:
        tenant = get_tenant_model().objects.filter(id=tenant_id).first()

    return tenant


class TenantMiddleware(AuthenticationMiddleware):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        request.tenant = _get_tenant(request)
        if not request.tenant and not _tenant_not_required(view_func):
            return redirect("customer-list")

        with tenant_context(request.tenant):
            return
