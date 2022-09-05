from django.shortcuts import redirect
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin

from easy_tenants import tenant_context, tenant_context_disabled
from example.app_test.models import Customer

URLS = ["customer-list", "set-tenant"]


class TenantMiddleware(MiddlewareMixin):
    def get_tenant(self, request):
        """Get tenant saved in session request"""
        tenant = None
        tenant_id = request.session.get("tenant_id", None)

        if tenant_id:
            tenant = Customer.objects.filter(id=tenant_id).first()

        return tenant

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # tenant filter is disabled in admin
        if request.path.startswith("/admin/"):
            with tenant_context_disabled():
                return self.get_response(request)

        self.tenant = self.get_tenant(request)

        ignored_path = any(
            resolve(request.path).view_name == url for url in URLS
        )
        if not self.tenant and not ignored_path:
            return redirect("customer-list")

        if self.tenant:
            # views works with tenant
            with tenant_context(self.tenant):
                request.tenant = self.tenant
                return self.get_response(request)

        return self.get_response(request)
