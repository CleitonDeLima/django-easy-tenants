from django.conf import settings
from django.shortcuts import get_object_or_404, resolve_url
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin

from easy_tenants import set_current_tenant, get_tenant_model

Tenant = get_tenant_model()


class SetTenantView(LoginRequiredMixin, RedirectView):
    def post(self, request, *args, **kwargs):
        tenant = get_object_or_404(Tenant, pk=kwargs['pk'])
        set_current_tenant(tenant)

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        redirect_url = getattr(settings, 'EASY_TENANTS_REDIRECT_URL', None)
        if redirect_url:
            return resolve_url(redirect_url)

        return super().get_redirect_url(*args, **kwargs)


set_tenant = SetTenantView.as_view()
