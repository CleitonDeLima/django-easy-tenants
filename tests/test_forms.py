from django import forms

from easy_tenants import tenant_context
from tests.models import Category, Product, StoreTenant


def test_modelfield_contents(tenant_ctx):
    class ProductForm(forms.Form):
        product = forms.ModelChoiceField(queryset=Product.objects.all())

    p1 = Product.objects.create(name="prod1")
    p2 = Product.objects.create(name="prod2")

    other_tenant = StoreTenant.objects.create()
    with tenant_context(other_tenant):
        Product.objects.create(name="prod3")

    form = ProductForm()
    form_template = form.as_p()

    assert f'<option value="{p1.id}">{p1.name}</option>' in form_template
    assert f'<option value="{p2.id}">{p2.name}</option>' in form_template
    assert "prod3" not in form_template


def test_related_field_contents(tenant_ctx):
    class ProductForm(forms.Form):
        category = forms.ModelChoiceField(queryset=Category.objects.all())

    c1 = Category.objects.create(name="cat1")
    c2 = Category.objects.create(name="cat2")

    other_tenant = StoreTenant.objects.create()
    with tenant_context(other_tenant):
        Category.objects.create(name="cat3")

    form = ProductForm()
    form_template = form.as_p()

    assert f'<option value="{c1.id}">{c1.name}</option>' in form_template
    assert f'<option value="{c2.id}">{c2.name}</option>' in form_template
    assert "cat3" not in form_template
