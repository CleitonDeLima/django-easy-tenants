from django.apps import AppConfig
from django.core import checks

from easy_tenants.checks import check_settings


class EasyTenantsConfig(AppConfig):
    name = 'easy_tenants'
    verbose_name = 'Easy Tenants'

    def ready(self):
        checks.register(check_settings, checks.Tags.compatibility)
