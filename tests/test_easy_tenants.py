import pytest

from easy_tenants import __version__
from tests.models import StoreTenant
from easy_tenants import (
    get_tenant_model,
    set_current_tenant,
    get_current_tenant
)


def test_version():
    assert __version__ == '0.1.0'


def test_get_tenant_model():
    assert StoreTenant == get_tenant_model()


@pytest.mark.django_db
def test_get_and_set_current_tenant_thread_local():
    tenant = StoreTenant.objects.create()
    set_current_tenant(tenant)

    assert tenant == get_current_tenant()
