from easy_tenants import __version__
from easy_tenants import (
    get_tenant_model,
    set_current_tenant,
    get_current_tenant,
    tenant_context
)
from tests.models import StoreTenant


def test_version():
    assert __version__ == '0.1.0'


def test_get_tenant_model():
    assert StoreTenant == get_tenant_model()


def test_get_and_set_current_tenant_thread_local(db):
    tenant = StoreTenant.objects.create()
    set_current_tenant(tenant)

    assert tenant == get_current_tenant()


def test_tenant_context(db):
    tenant1 = StoreTenant.objects.create()
    tenant2 = StoreTenant.objects.create()
    set_current_tenant(tenant1)

    with tenant_context(tenant2):
        assert tenant2 == get_current_tenant()

    assert tenant1 == get_current_tenant()
