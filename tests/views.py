from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView

from easy_tenants import get_current_tenant
from easy_tenants.decorators import tenant_not_required
from tests.models import Contact


@login_required
def home(request):
    return HttpResponse("in home")


@login_required
@tenant_not_required
def store_list(request):
    return HttpResponse("store lists")


def current_tenant(request):
    return HttpResponse(str(get_current_tenant().pk))


async def async_current_tenant(request):
    return HttpResponse(str(get_current_tenant().pk))


@tenant_not_required
def tenant_optional(request):
    return HttpResponse(str(getattr(request.tenant, "pk", "")))


@method_decorator(tenant_not_required, name="dispatch")
class TenantOptionalView(View):
    def get(self, request):
        return HttpResponse("optional")


class ContactListView(ListView):
    template_name = "tests/contact_list.html"
    queryset = Contact.objects.by_phone()


contact_list = ContactListView.as_view()
