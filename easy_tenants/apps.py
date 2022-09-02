from django.apps import AppConfig


class EasyTenantsConfig(AppConfig):
    name = "easy_tenants"
    verbose_name = "Easy Tenants"

    def ready(self):
        from django.contrib.auth import views

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
