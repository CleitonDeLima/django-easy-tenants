from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from example.app_test.views import (
    customer_list,
    home,
    product_create,
    product_list,
    set_tenant,
)

urlpatterns = [
    path("", home, name="home"),
    path("customers/", customer_list, name="customer-list"),
    path("set-tenant/<str:pk>/", set_tenant, name="set-tenant"),
    path("product/new/", product_create, name="product-create"),
    path("product/list/", product_list, name="product-list"),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
