from django.contrib.auth.decorators import login_required
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from example.app_test.models import Category, Customer, Product


def tenant_not_required(view_func):
    """
    Decorator for views that marks that the view is accessible without tenants.
    """
    view_func.tenant_required = False
    return view_func


@login_required
@tenant_not_required
def customer_list(request):
    """List all customer/tenants"""
    customers = Customer.objects.all()
    return render(request, "customer_list.html", {"customer_list": customers})


@login_required
@require_POST
@tenant_not_required
def set_tenant(request, pk):
    """
    Save tenant in session
    """
    tenant = get_object_or_404(Customer, pk=pk)
    request.session["tenant_id"] = str(tenant.id)

    return redirect("product-list")


CategoryForm = modelform_factory(Category, fields=["name"])
ProductForm = modelform_factory(Product, fields=["name", "category"])


@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("product-list")

    context = {"form": form}
    return render(request, "product_form.html", context)


@login_required
def product_list(request):
    context = {"product_list": Product.objects.all()}
    return render(request, "product_list.html", context)


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("category-list")

    context = {"form": form}
    return render(request, "category_form.html", context)


@login_required
def category_list(request):
    context = {"category_list": Category.objects.all()}
    return render(request, "category_list.html", context)
