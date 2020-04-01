import pytest
from django.shortcuts import resolve_url

from easy_tenants import set_current_tenant
from tests.models import StoreTenant


def test_without_session_middleware(settings, client):
    settings.MIDDLEWARE = ['easy_tenants.middleware.DefaultTenantMiddleware']

    with pytest.raises(AssertionError):
        client.get('/')


def test_without_auth_middleware(settings, client):
    settings.MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'easy_tenants.middleware.DefaultTenantMiddleware',
    ]

    with pytest.raises(AssertionError):
        client.get('/')


def test_redirect_url_by_default_middleware(settings, logged_client,
                                            djasserts):
    settings.MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'easy_tenants.middleware.DefaultTenantMiddleware',
    ]
    settings.EASY_TENANTS_LIST_URL = 'store-list'
    response = logged_client.get('/')

    djasserts.redirects(response, resolve_url('store-list'))


def test_redirect_url_when_user_is_not_authenticated(settings, logged_client,
                                                     djasserts):
    settings.MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'easy_tenants.middleware.DefaultTenantMiddleware',
    ]
    settings.EASY_TENANTS_REDIRECT_URL = 'store-list'
    logged_client.logout()
    response = logged_client.get('/')

    djasserts.redirects(response, resolve_url(settings.LOGIN_URL),
                        fetch_redirect_response=False)


def test_default_middleware_with_tenant_in_context(settings, logged_client):
    settings.MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'easy_tenants.middleware.DefaultTenantMiddleware',
    ]
    settings.EASY_TENANTS_REDIRECT_URL = 'store-list'
    tenant = StoreTenant.objects.create()
    set_current_tenant(tenant)

    session = logged_client.session
    session['tenant_id'] = tenant.id
    session.save()
    response = logged_client.get('/')

    assert response.status_code == 200
    assert hasattr(response, 'request')
