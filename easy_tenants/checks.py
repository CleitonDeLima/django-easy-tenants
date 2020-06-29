from django.core import checks

from easy_tenants.conf import settings


def check_settings(app_configs, **kwargs):
    errors = []

    if settings.EASY_TENANTS_MODEL is None:
        errors.append(
            checks.Error(
                'EASY_TENANTS_MODEL must be in settings in order to use the '
                'easy_tenants application.',
                hint='EASY_TENANTS_MODEL = "myapp.TenantCustomModel"',
                obj=settings,
                id='easy_tenants'
            )
        )

    if settings.EASY_TENANTS_REDIRECT_URL is None:
        errors.append(
            checks.Error(
                'EASY_TENANTS_REDIRECT_URL must be in settings in order to '
                'use the easy_tenants application.',
                hint='EASY_TENANTS_REDIRECT_URL = "viewname"',
                obj=settings,
                id='easy_tenants'
            )
        )

    return errors
