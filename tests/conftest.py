import pytest
from django.conf import settings

from easy_tenants import tenant_context, get_tenant_model


def pytest_configure():
    settings.configure(
        SECRET_KEY='any-key',
        ROOT_URLCONF='tests.urls',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'tests',
        ],
        TENANT_MODEL='tests.StoreTenant'
    )


@pytest.fixture
def context(db):
    tenant = get_tenant_model().objects.create()
    with tenant_context(tenant):
        yield
