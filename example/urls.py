import debug_toolbar
from django.contrib import admin
from django.urls import include, path

from example.app_test.views import (
    category_create,
    category_list,
    customer_list,
    product_create,
    product_list,
    set_tenant,
)

urlpatterns = [
    path("", customer_list, name="customer-list"),
    path("set-tenant/<str:pk>/", set_tenant, name="set-tenant"),
    path("category/new/", category_create, name="category-create"),
    path("category/list/", category_list, name="category-list"),
    path("product/new/", product_create, name="product-create"),
    path("product/list/", product_list, name="product-list"),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
]
