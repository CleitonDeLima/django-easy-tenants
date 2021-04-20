from django.apps import AppConfig
from django.core import checks

from easy_tenants.checks import check_settings


class EasyTenantsConfig(AppConfig):
    name = "easy_tenants"
    verbose_name = "Easy Tenants"

    def ready(self):
        from django.contrib.auth import views

        checks.register(check_settings, checks.Tags.compatibility)

        login_not_required_views = (
            views.LoginView,
            views.LogoutView,
            views.PasswordResetView,
            views.PasswordResetDoneView,
            views.PasswordResetConfirmView,
            views.PasswordResetCompleteView,
        )
        for view in login_not_required_views:
            view.tenant_required = False
