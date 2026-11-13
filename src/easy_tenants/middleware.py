from contextlib import nullcontext

from asgiref.sync import (
    iscoroutinefunction,
    markcoroutinefunction,
    sync_to_async,
)
from django.apps import apps
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError

from easy_tenants import tenant_context


class TenantMiddleware:
    """
    Activate the tenant of each request for the rest of the request cycle.

    Subclasses define where the tenant comes from by implementing
    ``get_tenant_id()``. Views that require a tenant (every view, unless
    marked with ``tenant_required = False``) get ``tenant_not_found()`` when
    no tenant is found.
    """

    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    def __call__(self, request):
        if iscoroutinefunction(self):
            return self.__acall__(request)

        request.tenant = self.get_tenant(request)
        with self.get_context(request):
            return self.get_response(request)

    async def __acall__(self, request):
        request.tenant = await sync_to_async(self.get_tenant)(request)
        with self.get_context(request):
            return await self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.tenant is None and self.tenant_required(view_func):
            return self.tenant_not_found(request)

        return None

    def get_tenant_id(self, request):
        """Return the identifier (pk) of the tenant of the request."""
        raise NotImplementedError(
            "Subclasses of TenantMiddleware must implement get_tenant_id()."
        )

    def get_tenant(self, request):
        """
        Return the tenant of the request, or None.

        This is the place to check that the user may access the tenant,
        since the identifier usually comes from the client.
        """
        tenant_id = self.get_tenant_id(request)
        if tenant_id is None or tenant_id == "":
            return None

        TenantModel = apps.get_model(settings.EASY_TENANTS_TENANT_MODEL)
        try:
            return TenantModel._default_manager.get(pk=tenant_id)
        except (
            TenantModel.DoesNotExist,
            ValidationError,
            ValueError,
            TypeError,
        ):
            return None

    def tenant_not_found(self, request):
        """Handle a request without tenant to a view that requires one."""
        raise PermissionDenied("Tenant is required.")

    def tenant_required(self, view_func):
        """Return whether the view requires a tenant (default: True)."""
        view_class = getattr(view_func, "view_class", None)
        default = getattr(view_class, "tenant_required", True)
        return getattr(view_func, "tenant_required", default)

    def get_context(self, request):
        """Return the context manager wrapping the rest of the request."""
        if request.tenant is None:
            return nullcontext()

        return tenant_context(request.tenant)


class SessionTenantMiddleware(TenantMiddleware):
    """Read the tenant identifier from the session."""

    session_key = "tenant_id"

    def get_tenant_id(self, request):
        return request.session.get(self.session_key)


class HeaderTenantMiddleware(TenantMiddleware):
    """Read the tenant identifier from a request header."""

    header_name = "X-Tenant-ID"

    def get_tenant_id(self, request):
        return request.headers.get(self.header_name)
