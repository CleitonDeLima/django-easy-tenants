from django.shortcuts import redirect

from easy_tenants import tenant_context_disabled
from easy_tenants.middleware import SessionTenantMiddleware


def is_admin(request):
    return request.path.startswith("/admin/")


class TenantMiddleware(SessionTenantMiddleware):
    def get_tenant(self, request):
        if is_admin(request) or not request.user.is_authenticated:
            return None

        return super().get_tenant(request)

    def get_context(self, request):
        # tenant filter is disabled in admin
        if is_admin(request):
            return tenant_context_disabled()

        return super().get_context(request)

    def tenant_not_found(self, request):
        if is_admin(request):
            return None

        return redirect("customer-list")
