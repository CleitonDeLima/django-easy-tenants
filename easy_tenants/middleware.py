from django.shortcuts import redirect
from django.urls import resolve

from easy_tenants import get_tenant_model, set_current_tenant
from easy_tenants.conf import settings


class DefaultTenantMiddleware:
    """
    Middleware guarantees that the user will be authenticated and with
    a defined tenant.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        assert hasattr(request, 'user'), (
            "The easy_tenants middleware requires authentication middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.auth.middleware.AuthenticationMiddleware' before "
            "'easy_tenants.middleware.DefaultTenantMiddleware'."
        )
        response = None

        request.tenant = self.get_tenant(request)
        set_current_tenant(request.tenant)

        if not request.tenant or not request.user.is_authenticated:
            response = response or self.redirect_to(request)

        response = response or self.get_response(request)

        return response

    def redirect_to(self, request):
        """
        Redirect to EASY_TENANTS_REDIRECT_URL or ignore when the view it is
        defined in EASY_TENANTS_IGNORE_URLS
        :param request
        :return: HttpResponseRedirect
        """
        ignore_urls = settings.EASY_TENANTS_IGNORE_URLS[:]
        ignore_urls.append(settings.EASY_TENANTS_LIST_URL)
        ignore_urls.append(settings.LOGIN_URL)
        ignore_urls.append('easy_tenants:set-current-tenant')

        view_name = resolve(request.path).view_name
        is_valid_url = view_name not in ignore_urls

        if is_valid_url:
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)

            return redirect(settings.EASY_TENANTS_LIST_URL)

    def get_tenant(self, request):
        """Get tenant saved in session request"""
        tenant = None
        tenant_id = request.session.get(
            settings.EASY_TENANTS_SESSION_KEY, None
        )

        if tenant_id:
            tenant = get_tenant_model().objects.filter(id=tenant_id).first()

        return tenant
