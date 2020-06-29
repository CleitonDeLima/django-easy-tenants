from django.shortcuts import resolve_url

from easy_tenants import set_current_tenant
from tests.models import StoreTenant


class TestDefaultMiddleware:
    def test_redirect_url_tenant_list(self, logged_client, djasserts,
                                      settings):
        response = logged_client.get('/')
        expected = resolve_url(settings.EASY_TENANTS_REDIRECT_URL)
        djasserts.redirects(response, expected)

    def test_when_user_is_not_authenticated(self, logged_client, djasserts,
                                            settings):
        """Redirect to login url"""
        logged_client.logout()
        response = logged_client.get('/')
        expected = '%s?next=%s' % (resolve_url(settings.LOGIN_URL), '/')

        djasserts.redirects(response, expected)

    def test_with_tenant_in_context(self, logged_client):
        tenant = StoreTenant.objects.create()
        set_current_tenant(tenant)

        session = logged_client.session
        session['tenant_id'] = str(tenant.id)
        session.save()
        response = logged_client.get('/')

        assert response.status_code == 200
        assert hasattr(response, 'request')

    def test_redirect_to_login(self, client, settings):
        response = client.get(resolve_url(settings.LOGIN_URL))
        assert response.status_code == 200
