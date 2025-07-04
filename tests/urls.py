from django.contrib import admin
from django.urls import include, path

from tests.views import contact_list, home, store_list

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("stores/", store_list, name="store-list"),
    path("contacts/", contact_list, name="contact-list"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("easy-tenants/", include("easy_tenants.urls")),
]
