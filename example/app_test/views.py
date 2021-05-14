from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from easy_tenants import get_tenant_model
from example.app_test.models import Customer, Product


def tenant_not_required(view_func):
    """
    Decorator for views that marks that the view is accessible without tenants.
    """
    view_func.tenant_required = False
    return view_func


@login_required
def home(request):
    html = (
        "<h1>Home page</h1>"
        '<a href="/admin/">admin</a> <br/>'
        '<a href="/product/new/">new product</a>'
    )
    return HttpResponse(html)


@login_required
@tenant_not_required
def customer_list(request):
    """List all customer/tenants"""
    customers = Customer.objects.all()
    return render(request, "customer_list.html", {"object_list": customers})


@login_required
@require_POST
@tenant_not_required
def set_tenant(request, pk):
    """
    Save tenant in session
    """
    Tenant = get_tenant_model()
    tenant = get_object_or_404(Tenant, pk=pk)
    request.session["tenant_id"] = str(tenant.id)

    return redirect("home")


## products


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category"]


def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("product-list")

    context = {"form": form}
    return render(request, "product_form.html", context)


def product_list(request):
    context = {"object_list": Product.objects.all()}
    return render(request, "product_list.html", context)
