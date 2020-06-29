from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, resolve_url
from django.views.generic import RedirectView

from easy_tenants import (
    set_current_tenant,
    get_tenant_model,
    TenantNotRequiredMixin
)
from easy_tenants.conf import settings

Tenant = get_tenant_model()


class SetTenantView(LoginRequiredMixin, TenantNotRequiredMixin, RedirectView):
    def post(self, request, *args, **kwargs):
        tenant = get_object_or_404(Tenant, pk=kwargs['pk'])
        set_current_tenant(tenant)
        request.session[settings.EASY_TENANTS_SESSION_KEY] = kwargs['pk']

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        redirect_url = settings.EASY_TENANTS_SUCCESS_URL
        if redirect_url:
            return resolve_url(redirect_url)

        return super().get_redirect_url(*args, **kwargs)


set_tenant = SetTenantView.as_view()
