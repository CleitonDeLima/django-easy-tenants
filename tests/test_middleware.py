import uuid

import pytest
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.shortcuts import redirect
from django.test import AsyncClient, RequestFactory

from easy_tenants.middleware import (
    HeaderTenantMiddleware,
    SessionTenantMiddleware,
    TenantMiddleware,
)
from easy_tenants.utils import get_state
from tests.models import StoreTenant

BASE_MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]


class RedirectSessionTenantMiddleware(SessionTenantMiddleware):
    def tenant_not_found(self, request):
        return redirect("store-list")


class MemberSessionTenantMiddleware(SessionTenantMiddleware):
    def get_tenant(self, request):
        tenant = super().get_tenant(request)
        if tenant is not None and request.user.username == "member":
            return tenant
        return None


def use_middleware(settings, path):
    settings.MIDDLEWARE = [*BASE_MIDDLEWARE, path]


@pytest.fixture
def tenant(db):
    return StoreTenant.objects.create()


@pytest.fixture
def session_middleware(settings):
    use_middleware(settings, "easy_tenants.middleware.SessionTenantMiddleware")


@pytest.fixture
def header_middleware(settings):
    use_middleware(settings, "easy_tenants.middleware.HeaderTenantMiddleware")


def set_session_tenant(client, value):
    session = client.session
    session["tenant_id"] = value
    session.save()


def test_session_activates_tenant(session_middleware, logged_client, tenant):
    set_session_tenant(logged_client, str(tenant.pk))

    response = logged_client.get("/current-tenant/")

    assert response.status_code == 200
    assert response.content.decode() == str(tenant.pk)
    assert response.wsgi_request.tenant == tenant


def test_tenant_context_is_restored_after_request(
    session_middleware, logged_client, tenant
):
    set_session_tenant(logged_client, str(tenant.pk))

    logged_client.get("/current-tenant/")

    assert get_state()["tenant"] is None


@pytest.mark.parametrize("value", [None, "", "not-a-uuid", str(uuid.uuid4())])
def test_session_without_valid_tenant_is_forbidden(
    session_middleware, logged_client, value
):
    set_session_tenant(logged_client, value)

    response = logged_client.get("/current-tenant/")

    assert response.status_code == 403
    assert response.wsgi_request.tenant is None


def test_session_key_can_be_customized(tenant):
    class Middleware(SessionTenantMiddleware):
        session_key = "store"

    middleware = Middleware(lambda request: HttpResponse())
    request = RequestFactory().get("/")
    request.session = {"store": str(tenant.pk)}

    assert middleware.get_tenant(request) == tenant


@pytest.mark.parametrize(
    "url", ["/tenant-optional/", "/tenant-optional-cbv/", "/accounts/login/"]
)
def test_view_not_requiring_tenant(session_middleware, client, db, url):
    response = client.get(url)

    assert response.status_code == 200


def test_view_not_requiring_tenant_still_gets_tenant(
    session_middleware, logged_client, tenant
):
    set_session_tenant(logged_client, str(tenant.pk))

    response = logged_client.get("/tenant-optional/")

    assert response.content.decode() == str(tenant.pk)


def test_unknown_url_without_tenant_is_not_found(
    session_middleware, client, db
):
    response = client.get("/does-not-exist/")

    assert response.status_code == 404


def test_tenant_not_found_can_be_customized(settings, logged_client):
    use_middleware(
        settings, "tests.test_middleware.RedirectSessionTenantMiddleware"
    )

    response = logged_client.get("/current-tenant/")

    assert response.status_code == 302
    assert response.url == "/stores/"


@pytest.mark.parametrize(
    ("username", "status_code"), [("member", 200), ("stranger", 403)]
)
def test_get_tenant_can_check_access(
    settings, client, django_user_model, tenant, username, status_code
):
    use_middleware(
        settings, "tests.test_middleware.MemberSessionTenantMiddleware"
    )
    client.force_login(django_user_model.objects.create_user(username))
    set_session_tenant(client, str(tenant.pk))

    response = client.get("/current-tenant/")

    assert response.status_code == status_code


def test_header_activates_tenant(header_middleware, client, tenant):
    response = client.get("/current-tenant/", HTTP_X_TENANT_ID=str(tenant.pk))

    assert response.status_code == 200
    assert response.content.decode() == str(tenant.pk)


def test_header_missing_is_forbidden(header_middleware, client, db):
    response = client.get("/current-tenant/")

    assert response.status_code == 403


def test_header_name_can_be_customized(tenant):
    class Middleware(HeaderTenantMiddleware):
        header_name = "X-Store"

    middleware = Middleware(lambda request: HttpResponse())
    request = RequestFactory().get("/", HTTP_X_STORE=str(tenant.pk))

    assert middleware.get_tenant(request) == tenant


@pytest.mark.parametrize("url", ["/current-tenant/", "/async-current-tenant/"])
def test_async_request_activates_tenant(header_middleware, tenant, url):
    client = AsyncClient()

    response = async_to_sync(client.get)(
        url, headers={"X-Tenant-ID": str(tenant.pk)}
    )

    assert response.status_code == 200
    assert response.content.decode() == str(tenant.pk)


def test_async_request_without_tenant_is_forbidden(header_middleware, db):
    client = AsyncClient()

    response = async_to_sync(client.get)("/async-current-tenant/")

    assert response.status_code == 403


def test_base_middleware_requires_get_tenant_id():
    middleware = TenantMiddleware(lambda request: HttpResponse())

    with pytest.raises(NotImplementedError):
        middleware.get_tenant(RequestFactory().get("/"))
