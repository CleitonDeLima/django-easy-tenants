from django.apps import apps
from django.conf import settings
from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.module_loading import import_string

from easy_tenants.models import (
    TenantAwareAbstract,
    TenantManager,
    tenant_field_name,
)

TENANT_MIDDLEWARE = "easy_tenants.middleware.TenantMiddleware"
SESSION_TENANT_MIDDLEWARE = "easy_tenants.middleware.SessionTenantMiddleware"
SESSION_MIDDLEWARE = "django.contrib.sessions.middleware.SessionMiddleware"


def get_tenant_model():
    """Return the model named by EASY_TENANTS_TENANT_MODEL, or None."""
    try:
        return apps.get_model(settings.EASY_TENANTS_TENANT_MODEL)
    except (AttributeError, ValueError, LookupError):
        return None


def middleware_index(base_path):
    """
    Return the index of the first MIDDLEWARE entry that is the class at
    ``base_path`` or a subclass of it, or None.
    """
    base = import_string(base_path)
    for index, path in enumerate(settings.MIDDLEWARE):
        try:
            candidate = import_string(path)
        except ImportError:
            # Django reports unimportable middleware on its own.
            continue
        if isinstance(candidate, type) and issubclass(candidate, base):
            return index

    return None


@checks.register(checks.Tags.models)
def check_tenant_model_setting(app_configs=None, **kwargs):
    value = getattr(settings, "EASY_TENANTS_TENANT_MODEL", None)

    if value is None:
        index = middleware_index(TENANT_MIDDLEWARE)
        if index is None:
            return []
        return [
            checks.Error(
                "EASY_TENANTS_TENANT_MODEL must be set when "
                f"'{settings.MIDDLEWARE[index]}' is in MIDDLEWARE.",
                hint="Set it to your tenant model, e.g. 'app.Customer'.",
                id="easy_tenants.E003",
            )
        ]

    app_label, _, model_name = str(value).partition(".")
    if not app_label or not model_name or "." in model_name:
        return [
            checks.Error(
                "EASY_TENANTS_TENANT_MODEL must be of the form "
                "'app_label.ModelName'.",
                hint=f"Got {value!r}.",
                id="easy_tenants.E001",
            )
        ]

    if get_tenant_model() is None:
        return [
            checks.Error(
                f"EASY_TENANTS_TENANT_MODEL refers to model '{value}' that "
                "has not been installed.",
                hint="Check the app label and model name, and that the app "
                "is in INSTALLED_APPS.",
                id="easy_tenants.E002",
            )
        ]

    return []


def is_tenant_aware(model):
    """Return whether the model opted in to tenant isolation."""
    return issubclass(model, TenantAwareAbstract) or any(
        isinstance(manager, TenantManager) for manager in model._meta.managers
    )


def check_model(model):
    """Return the tenant configuration errors of a tenant-aware model."""
    if not is_tenant_aware(model):
        return []

    try:
        field = model._meta.get_field(tenant_field_name)
    except FieldDoesNotExist:
        return [
            checks.Error(
                f"'{model._meta.label}' is tenant-aware but has no "
                f"'{tenant_field_name}' field.",
                hint="Add a ForeignKey to the tenant model named "
                f"'{tenant_field_name}', or change EASY_TENANTS_TENANT_FIELD.",
                obj=model,
                id="easy_tenants.E004",
            )
        ]

    if not isinstance(field, models.ForeignKey):  # OneToOneField included
        return [
            checks.Error(
                f"'{model._meta.label}.{tenant_field_name}' must be a "
                "ForeignKey or OneToOneField to the tenant model.",
                obj=model,
                id="easy_tenants.E005",
            )
        ]

    tenant_model = get_tenant_model()
    related_model = field.related_model
    if (
        tenant_model is not None
        and not isinstance(related_model, str)
        # A proxy of the tenant model shares its table.
        and related_model._meta.concrete_model
        is not tenant_model._meta.concrete_model
    ):
        return [
            checks.Error(
                f"'{model._meta.label}.{tenant_field_name}' refers to "
                f"'{related_model._meta.label}', but "
                f"EASY_TENANTS_TENANT_MODEL is '{tenant_model._meta.label}'.",
                obj=model,
                id="easy_tenants.E006",
            )
        ]

    return []


@checks.register(checks.Tags.models)
def check_tenant_models(app_configs=None, **kwargs):
    if app_configs is None:
        model_list = apps.get_models()
    else:
        model_list = (m for config in app_configs for m in config.get_models())

    return [error for model in model_list for error in check_model(model)]


@checks.register()
def check_session_middleware(app_configs=None, **kwargs):
    tenant_index = middleware_index(SESSION_TENANT_MIDDLEWARE)
    if tenant_index is None:
        return []

    session_index = middleware_index(SESSION_MIDDLEWARE)
    if session_index is not None and session_index < tenant_index:
        return []

    return [
        checks.Error(
            f"'{SESSION_MIDDLEWARE}' must be in MIDDLEWARE before "
            f"'{settings.MIDDLEWARE[tenant_index]}'.",
            id="easy_tenants.E007",
        )
    ]
