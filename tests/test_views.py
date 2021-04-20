import pytest
from django.contrib.auth import views as auth_views
from django.shortcuts import resolve_url

from easy_tenants import get_current_tenant
from tests.models import StoreTenant, Contact


class TestSetCurrentTenant:
    def test_post(self, logged_client, settings):
        settings.EASY_TENANTS_SUCCESS_URL = ""
        store = StoreTenant.objects.create()
        url = resolve_url("easy_tenants:set-current-tenant", pk=store.id)
        response = logged_client.post(url)

        assert store == get_current_tenant()
        assert response.status_code == 410

    def test_redirect_url(self, logged_client, settings, djasserts):
        settings.EASY_TENANTS_REDIRECT_URL = "store-list"
        settings.EASY_TENANTS_SUCCESS_URL = "home"
        store = StoreTenant.objects.create()
        url = resolve_url("easy_tenants:set-current-tenant", pk=store.id)
        response = logged_client.post(url)

        djasserts.redirects(response, resolve_url("home"))

    def test_has_session_key(self, logged_client, settings, djasserts):
        settings.EASY_TENANTS_REDIRECT_URL = "store-list"
        store = StoreTenant.objects.create()
        url = resolve_url("easy_tenants:set-current-tenant", pk=store.id)
        logged_client.post(url)

        assert settings.EASY_TENANTS_SESSION_KEY in logged_client.session

    def test_required_login(self, db, client, settings, djasserts):
        store = StoreTenant.objects.create()
        url = resolve_url("easy_tenants:set-current-tenant", pk=store.id)
        response = client.post(url)
        expected_url = "%s?next=%s" % (resolve_url(settings.LOGIN_URL), url)

        djasserts.redirects(
            response, expected_url, fetch_redirect_response=False
        )


class TestViewsTenantContext:
    def test_declare_queryset_attr(self, tenant_ctx, logged_client, settings):
        session = logged_client.session
        session[settings.EASY_TENANTS_SESSION_KEY] = str(tenant_ctx.id)
        session.save()

        Contact.objects.create(name="phone1")
        Contact.objects.create(name="email")
        response = logged_client.get(resolve_url("contact-list"))
        assert len(response.context["object_list"]) == 1


class TestAuthView:
    @pytest.mark.parametrize(
        "view",
        [
            auth_views.LoginView,
            auth_views.LogoutView,
            auth_views.PasswordResetView,
            auth_views.PasswordResetDoneView,
            auth_views.PasswordResetConfirmView,
            auth_views.PasswordResetCompleteView,
        ],
    )
    def test_has_tenant_required_with_false(self, view):
        assert hasattr(view, "tenant_required")
        assert not getattr(view, "tenant_required")
