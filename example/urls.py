import debug_toolbar
from django.contrib import admin
from django.urls import include, path

from example.app_test.views import customer_list, set_tenant

urlpatterns = [
    path("set-tenant/<str:pk>/", set_tenant, name="set-tenant"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("customers/", customer_list, name="customer-list"),
    path("admin/", admin.site.urls),  # login only
    path("__debug__/", include(debug_toolbar.urls)),
]
