from django.shortcuts import resolve_url

from easy_tenants import get_current_tenant
from tests.models import StoreTenant


def test_set_current_tenant(logged_client):
    store = StoreTenant.objects.create()
    url = resolve_url('easy_tenants:set-current-tenant', pk=store.id)
    response = logged_client.post(url)

    assert store == get_current_tenant()
    assert response.status_code == 410


def test_set_current_tenant_required_login(db, client, settings, djasserts):
    store = StoreTenant.objects.create()
    url = resolve_url('easy_tenants:set-current-tenant', pk=store.id)
    response = client.post(url)
    expected_url = '%s?next=%s' % (resolve_url(settings.LOGIN_URL), url)

    djasserts.redirects(response, expected_url, fetch_redirect_response=False)


def test_set_current_tenant_redirect_url(logged_client, settings, djasserts):
    settings.EASY_TENANTS_REDIRECT_URL = 'store-list'
    store = StoreTenant.objects.create()
    url = resolve_url('easy_tenants:set-current-tenant', pk=store.id)
    response = logged_client.post(url)

    djasserts.redirects(response, resolve_url('store-list'))
    assert settings.EASY_TENANTS_SESSION_KEY in logged_client.session
