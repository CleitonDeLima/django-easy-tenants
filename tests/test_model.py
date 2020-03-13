import pytest

from easy_tenants import set_current_tenant
from easy_tenants.models import TenantAbstract
from tests.models import StoreTenant, Product, Contact


def test_inheritance_tenant_model():
    assert TenantAbstract in Product.__mro__
    assert getattr(Product.objects, 'tenant_manager', False)


@pytest.mark.django_db
def test_create_object():
    store = StoreTenant.objects.create()
    Product.objects.create(name='prod1', tenant=store)
    assert Product.objects.count()


@pytest.mark.django_db
def test_autoset_current_tenant_in_instance_model():
    store = StoreTenant.objects.create()
    set_current_tenant(store)

    prod = Product.objects.create(name='prod1')
    assert prod.tenant_id == store.id


@pytest.mark.django_db
def test_get_objects_of_tenant():
    store1 = StoreTenant.objects.create()
    set_current_tenant(store1)
    Product.objects.create(name='prod1')

    store2 = StoreTenant.objects.create()
    set_current_tenant(store2)
    Product.objects.create(name='prod2')

    assert Product.objects.count() == 1


@pytest.mark.django_db
def test_custom_queryset_in_manager():
    store1 = StoreTenant.objects.create()
    set_current_tenant(store1)
    Contact.objects.create(name='phone 222')
    Contact.objects.create(name='email')

    assert callable(Contact.objects.by_phone)
    assert Contact.objects.by_phone().count() == 1
