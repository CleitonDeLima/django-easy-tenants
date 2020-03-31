import pytest
from django.conf import settings as dj_settings

from easy_tenants import tenant_context, get_tenant_model


def pytest_configure():
    dj_settings.configure(
        SECRET_KEY='any-key',
        ROOT_URLCONF='tests.urls',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        MIDDLEWARE=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'tests',
        ],
        EASY_TENANTS_MODEL='tests.StoreTenant',
    )


@pytest.fixture
def djasserts():
    from django.test import TestCase
    testcase = TestCase()

    class Asserts:
        redirects = testcase.assertRedirects

    return Asserts()


@pytest.fixture
def context(db):
    tenant = get_tenant_model().objects.create()
    with tenant_context(tenant):
        yield
