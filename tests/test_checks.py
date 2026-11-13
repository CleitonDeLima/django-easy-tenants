import pytest
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.checks import run_checks
from django.db import models
from django.test import override_settings
from django.test.utils import isolate_apps

from easy_tenants.checks import (
    check_model,
    check_session_middleware,
    check_tenant_model_setting,
    check_tenant_models,
)
from easy_tenants.middleware import SessionTenantMiddleware
from easy_tenants.models import TenantAwareAbstract, TenantManager
from tests.models import StoreTenant, Warehouse

SESSION_MIDDLEWARE = "django.contrib.sessions.middleware.SessionMiddleware"


def ids(errors):
    return [error.id for error in errors]


def active(errors):
    return [error for error in errors if not error.is_silenced()]


@pytest.fixture
def no_tenant_model(settings):
    del settings.EASY_TENANTS_TENANT_MODEL
    return settings


def test_project_has_no_easy_tenants_errors():
    errors = active(run_checks())
    assert [e for e in errors if e.id.startswith("easy_tenants.")] == []


def test_tenant_model_setting_valid():
    assert check_tenant_model_setting() == []


@override_settings(EASY_TENANTS_TENANT_MODEL="StoreTenant")
def test_tenant_model_setting_bad_format():
    assert ids(check_tenant_model_setting()) == ["easy_tenants.E001"]


@override_settings(EASY_TENANTS_TENANT_MODEL="tests.Missing")
def test_tenant_model_setting_not_installed():
    assert ids(check_tenant_model_setting()) == ["easy_tenants.E002"]


def test_tenant_model_setting_unset_without_middleware(no_tenant_model):
    assert check_tenant_model_setting() == []


def test_tenant_model_setting_unset_with_middleware(no_tenant_model):
    no_tenant_model.MIDDLEWARE = [
        SESSION_MIDDLEWARE,
        "easy_tenants.middleware.HeaderTenantMiddleware",
    ]
    assert ids(check_tenant_model_setting()) == ["easy_tenants.E003"]


def test_project_tenant_models_pass():
    assert active(check_tenant_models()) == []


def test_tenant_models_restricted_to_app_configs():
    # tests.Shelf and tests.Bin point to Warehouse (E006, silenced in settings).
    tests_errors = check_tenant_models([apps.get_app_config("tests")])
    auth_errors = check_tenant_models([apps.get_app_config("auth")])

    assert sorted(e.obj.__name__ for e in tests_errors) == ["Bin", "Shelf"]
    assert auth_errors == []


@isolate_apps("tests")
def test_tenant_model_missing_field_reported_once():
    class Model(TenantAwareAbstract):
        objects = TenantManager()

    assert ids(check_model(Model)) == ["easy_tenants.E004"]


@isolate_apps("tests")
def test_tenant_manager_only_missing_field():
    class Model(models.Model):
        objects = TenantManager()

    assert ids(check_model(Model)) == ["easy_tenants.E004"]


@isolate_apps("tests")
def test_tenant_aware_abstract_only_missing_field():
    class Model(TenantAwareAbstract):
        pass

    assert ids(check_model(Model)) == ["easy_tenants.E004"]


@isolate_apps("tests")
def test_tenant_manager_from_queryset_detected():
    class Model(models.Model):
        objects = TenantManager.from_queryset(models.QuerySet)()

    assert ids(check_model(Model)) == ["easy_tenants.E004"]


@isolate_apps("tests")
def test_tenant_field_not_a_foreign_key():
    class Model(TenantAwareAbstract):
        store = models.CharField(max_length=10)
        objects = TenantManager()

    assert ids(check_model(Model)) == ["easy_tenants.E005"]


@isolate_apps("tests")
def test_tenant_field_one_to_one_is_valid():
    class Model(TenantAwareAbstract):
        store = models.OneToOneField(StoreTenant, on_delete=models.CASCADE)
        objects = TenantManager()

    assert check_model(Model) == []


@isolate_apps("tests")
def test_tenant_field_generic_foreign_key():
    class Model(TenantAwareAbstract):
        content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
        object_id = models.CharField(max_length=36)
        store = GenericForeignKey("content_type", "object_id")
        objects = TenantManager()

    assert ids(check_model(Model)) == ["easy_tenants.E005"]


@isolate_apps("tests")
def test_tenant_field_points_to_tenant_proxy():
    class StoreTenantProxy(StoreTenant):
        class Meta:
            proxy = True

    class Model(TenantAwareAbstract):
        store = models.ForeignKey(StoreTenantProxy, on_delete=models.CASCADE)
        objects = TenantManager()

    assert check_model(Model) == []


@isolate_apps("tests")
def test_tenant_field_points_to_other_model():
    class Model(TenantAwareAbstract):
        store = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
        objects = TenantManager()

    assert ids(check_model(Model)) == ["easy_tenants.E006"]


@isolate_apps("tests")
def test_tenant_field_other_model_without_setting(no_tenant_model):
    class Model(TenantAwareAbstract):
        store = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
        objects = TenantManager()

    assert check_model(Model) == []


@isolate_apps("tests")
def test_unfiltered_model_with_tenant_fk_is_ignored():
    class Membership(models.Model):
        store = models.ForeignKey(StoreTenant, on_delete=models.CASCADE)

    assert check_model(Membership) == []


class CustomSessionTenantMiddleware(SessionTenantMiddleware):
    pass


class CustomSessionMiddleware(SessionMiddleware):
    pass


SESSION_TENANT = "easy_tenants.middleware.SessionTenantMiddleware"
CUSTOM_SESSION_TENANT = f"{__name__}.CustomSessionTenantMiddleware"
CUSTOM_SESSION = f"{__name__}.CustomSessionMiddleware"
HEADER_TENANT = "easy_tenants.middleware.HeaderTenantMiddleware"


@pytest.mark.parametrize(
    "middleware",
    [
        [SESSION_MIDDLEWARE, SESSION_TENANT],
        [CUSTOM_SESSION, SESSION_TENANT],
        [HEADER_TENANT],
        ["does.not.Exist", SESSION_MIDDLEWARE, SESSION_TENANT],
    ],
)
def test_session_middleware_order_valid(settings, middleware):
    settings.MIDDLEWARE = middleware
    assert check_session_middleware() == []


@pytest.mark.parametrize(
    "middleware",
    [
        [SESSION_TENANT],
        [SESSION_TENANT, SESSION_MIDDLEWARE],
        [CUSTOM_SESSION_TENANT, SESSION_MIDDLEWARE],
    ],
)
def test_session_middleware_order_invalid(settings, middleware):
    settings.MIDDLEWARE = middleware
    assert ids(check_session_middleware()) == ["easy_tenants.E007"]
