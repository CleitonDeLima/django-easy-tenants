from django.apps import apps
from django.core import checks

from easy_tenants.conf import settings


def check_settings(app_configs, **kwargs):
    from easy_tenants.models import TenantAbstract, TenantManager

    errors = []

    if settings.EASY_TENANTS_MODEL is None:
        errors.append(
            checks.Error(
                "EASY_TENANTS_MODEL must be in settings in order to use the "
                "easy_tenants application.",
                hint='EASY_TENANTS_MODEL = "myapp.TenantCustomModel"',
                obj=settings,
                id="easy_tenants",
            )
        )

    # Checks if the models are properly configured
    for model in apps.get_models():
        if (
            issubclass(model, TenantAbstract)
            and hasattr(model, "objects")
            and not isinstance(model.objects, TenantManager)
        ):
            errors.append(
                checks.Error(
                    "Required TenantManager in objects manager.",
                    hint="objects = TenantManager()",
                    obj=model,
                    id="easy_tenants",
                )
            )

    return errors
