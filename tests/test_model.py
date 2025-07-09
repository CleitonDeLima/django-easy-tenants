import pytest
from django.core.exceptions import ValidationError

from easy_tenants import (
    get_current_tenant,
    tenant_context,
    tenant_context_disabled,
)
from easy_tenants.exceptions import TenantError
from tests.models import Contact, Order, Product, StoreTenant


def test_create_object(tenant_ctx):
    Product.objects.create(name="prod1")
    assert Product.objects.count()


def test_set_tenant_in_instance_model(tenant_ctx):
    prod = Product.objects.create(name="prod1")
    assert prod.get_tenant_instance()


def test_get_objects_of_tenant(db):
    store1 = StoreTenant.objects.create()
    store2 = StoreTenant.objects.create()
    with tenant_context(store1):
        Product.objects.create(name="prod1")

    with tenant_context(store2):
        Product.objects.create(name="prod2")

        assert Product.objects.count() == 1


def test_custom_queryset_in_manager(tenant_ctx):
    Contact.objects.create(name="phone 222")
    Contact.objects.create(name="email")

    assert callable(Contact.objects.by_phone)
    assert Contact.objects.by_phone().count() == 1


def test_bulk_create(tenant_ctx):
    objs = [
        Product(name="prod1"),
        Product(name="prod2"),
    ]
    Product.objects.bulk_create(objs)
    tenant = get_current_tenant()

    assert Product.objects.count() == 2
    assert objs[0].get_tenant_instance() == tenant
    assert objs[1].get_tenant_instance() == tenant


@pytest.mark.django_db
def test_bulk_create_without_context():
    store1 = StoreTenant.objects.create()
    store2 = StoreTenant.objects.create()

    objs = [
        Product(name="prod1", store=store1),
        Product(name="prod2", store=store2),
    ]
    with tenant_context_disabled():
        objs = Product.objects.bulk_create(objs)

        assert Product.objects.count() == 2
        assert objs[0].get_tenant_instance() == store1
        assert objs[1].get_tenant_instance() == store2


def test_all_objects(db):
    store1 = StoreTenant.objects.create()
    store2 = StoreTenant.objects.create()
    with tenant_context(store1):
        Product.objects.create(name="prod1")
        assert Product.objects.count() == 1

    with tenant_context(store2):
        Product.objects.create(name="prod2")
        assert Product.objects.count() == 1

    with tenant_context_disabled():
        assert Product.objects.count() == 2


def test_tenant_required_error(db):
    with pytest.raises(TenantError), tenant_context():
        Product.objects.create(name="prod1")


@pytest.mark.django_db
class TestUniqueTenantConstraint:
    def test_unique_validate(self):
        store = StoreTenant.objects.create()
        with tenant_context(store):
            product = Product.objects.create(name="prod")
            Order.objects.create(product=product, code="1")
            o = Order(product=product, code="1")

            with pytest.raises(ValidationError) as exc_info:
                o.full_clean()
            assert exc_info.value.messages == [
                "Order with this Code already exists."
            ]

    def test_custom_params(self):
        store = StoreTenant.objects.create()
        with tenant_context(store):
            product = Product.objects.create(name="prod")
            Order.objects.create(product=product, code="1", sku="SUV")
            Order.objects.create(product=product, code="2", sku="")
            o = Order(product=product, code="3", sku="SUV")

            with pytest.raises(ValidationError) as exc_info:
                o.full_clean()

            assert exc_info.value.messages == ["Sku exists!"]
