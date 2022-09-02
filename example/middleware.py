from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from easy_tenants import tenant_context
from example.app_test.models import Customer


class TenantMiddleware(MiddlewareMixin):
    def tenant_not_required(self, view_func):
        """
        By default all views need a defined tenant, not when you have
        tenant_required = False
        """
        if not getattr(view_func, "tenant_required", True):
            return True

        return False

    def get_tenant(self, request):
        """Get tenant saved in session request"""
        SESSION_KEY = "tenant_id"
        tenant = None
        tenant_id = request.session.get(SESSION_KEY, None)

        if tenant_id:
            tenant = Customer.objects.filter(id=tenant_id).first()

        return tenant

    def process_view(self, request, view_func, view_args, view_kwargs):
        # avoid loop in customer-list
        if (
            request.user.is_authenticated
            and not self.tenant
            and not self.tenant_not_required(view_func)
        ):
            return redirect("customer-list")

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        self.tenant = self.get_tenant(request)

        if not self.tenant:
            return self.get_response(request)

        # views works with tenant
        with tenant_context(self.tenant):
            return self.get_response(request)
