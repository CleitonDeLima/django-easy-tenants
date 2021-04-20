from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from easy_tenants import tenant_not_required
from example.app_test.models import Customer


@login_required
def home(request):
    html = "<h1>Home page</h1>" '<a href="/admin/">admin</a>'
    return HttpResponse(html)


@login_required
@tenant_not_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "customer_list.html", {"object_list": customers})
