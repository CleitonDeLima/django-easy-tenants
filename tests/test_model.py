from easy_tenants import get_current_tenant, tenant_context
from easy_tenants.models import TenantAbstract
from tests.models import Contact, Product, StoreTenant


def test_inheritance_tenant_model():
    assert TenantAbstract in Product.__mro__


def test_create_object(tenant_ctx):
    Product.objects.create(name="prod1")
    assert Product.objects.count()


def test_autoset_current_tenant_in_instance_model(tenant_ctx):
    prod = Product.objects.create(name="prod1")
    assert prod.tenant_id


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
    assert objs[0].tenant == tenant
    assert objs[1].tenant == tenant


def test_all_objects(db):
    store1 = StoreTenant.objects.create()
    store2 = StoreTenant.objects.create()
    with tenant_context(store1):
        Product.objects.create(name="prod1")

    with tenant_context(store2):
        Product.objects.create(name="prod2")

    assert Product.all_objects.count() == 2
