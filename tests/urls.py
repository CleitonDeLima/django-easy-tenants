from django.contrib import admin
from django.urls import include, path

from tests.views import (
    TenantOptionalView,
    async_current_tenant,
    contact_list,
    current_tenant,
    home,
    store_list,
    tenant_optional,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("stores/", store_list, name="store-list"),
    path("contacts/", contact_list, name="contact-list"),
    path("current-tenant/", current_tenant, name="current-tenant"),
    path(
        "async-current-tenant/",
        async_current_tenant,
        name="async-current-tenant",
    ),
    path("tenant-optional/", tenant_optional, name="tenant-optional"),
    path(
        "tenant-optional-cbv/",
        TenantOptionalView.as_view(),
        name="tenant-optional-cbv",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
]
