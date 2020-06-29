import pytest


@pytest.fixture
def djasserts():
    from django.test import TestCase
    testcase = TestCase()

    class Asserts:
        redirects = testcase.assertRedirects

    return Asserts()


@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user('usertest')
    return user


@pytest.fixture
def logged_client(user, client):
    """A Django test client instance with a new user authenticated."""
    client.force_login(user)
    return client


@pytest.fixture
def tenant_ctx(db):
    """Create a tenant a set context"""
    from easy_tenants import tenant_context, get_tenant_model

    tenant = get_tenant_model().objects.create()
    with tenant_context(tenant):
        yield tenant
