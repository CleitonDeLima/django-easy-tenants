import pytest

from easy_tenants import tenant_context, get_current_tenant
from easy_tenants.models import TenantAbstract
from tests.models import StoreTenant, Product, Contact


def test_inheritance_tenant_model():
    assert TenantAbstract in Product.__mro__
    assert getattr(Product.objects, 'tenant_manager', False)


def test_create_object(context):
    Product.objects.create(name='prod1')
    assert Product.objects.count()


def test_autoset_current_tenant_in_instance_model(context):
    prod = Product.objects.create(name='prod1')
    assert prod.tenant_id


@pytest.mark.django_db
def test_get_objects_of_tenant():
    store1 = StoreTenant.objects.create()
    store2 = StoreTenant.objects.create()
    with tenant_context(store1):
        Product.objects.create(name='prod1')

    with tenant_context(store2):
        Product.objects.create(name='prod2')

        assert Product.objects.count() == 1


def test_custom_queryset_in_manager(context):
    Contact.objects.create(name='phone 222')
    Contact.objects.create(name='email')

    assert callable(Contact.objects.by_phone)
    assert Contact.objects.by_phone().count() == 1


def test_bulk_create(context):
    objs = [
        Product(name='prod1'),
        Product(name='prod2'),
    ]
    Product.objects.bulk_create(objs)
    tenant = get_current_tenant()

    assert Product.objects.count() == 2
    assert objs[0].tenant == tenant
    assert objs[1].tenant == tenant
