from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import ListView

from easy_tenants import tenant_not_required

from tests.models import Contact


def home(request):
    return HttpResponse('in home')


@login_required
@tenant_not_required
def store_list(request):
    return HttpResponse('store lists')


class ContactListView(ListView):
    template_name = 'tests/contact_list.html'
    queryset = Contact.objects.by_phone()


contact_list = ContactListView.as_view()
