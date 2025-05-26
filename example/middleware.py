import re

from django.shortcuts import redirect
from django.urls import clear_url_caches, resolve, set_urlconf
from django.utils.deprecation import MiddlewareMixin

from easy_tenants import tenant_context, tenant_context_disabled
from easy_tenants.urlresolvers import get_subfolder_urlconf
from example.app_test.models import Customer

URLS = ["customer-list", "set-tenant"]


def get_tenant_id_from_path(path: str) -> str:
    path = path.removeprefix("/")

    match = re.match(r"^(\w)/", path)
    if match:
        return match.group(1)

    return ""


class TenantMiddleware(MiddlewareMixin):
    def get_tenant(self, request):
        """Get tenant saved in session request"""
        tenant = None
        tenant_id = get_tenant_id_from_path(request.path)

        if tenant_id:
            try:
                tenant = Customer.objects.filter(id=tenant_id).first()
            except:
                pass

        return tenant

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        # tenant filter is disabled in admin
        if request.path.startswith("/admin/"):
            with tenant_context_disabled():
                return self.get_response(request)

        self.tenant = self.get_tenant(request)

        if not self.tenant:
            ignored_path = any(
                resolve(request.path).view_name == url for url in URLS
            )
            if not ignored_path:
                return redirect("customer-list")

        if self.tenant:
            # views works with tenant
            with tenant_context(self.tenant):
                request.tenant = self.tenant
                urlconf = get_subfolder_urlconf(self.tenant)
                clear_url_caches()

                request.urlconf = urlconf
                set_urlconf(urlconf)

                return self.get_response(request)

        return self.get_response(request)
