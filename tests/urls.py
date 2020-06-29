from django.urls import path, include
from django.contrib import admin

from tests.views import home, store_list, contact_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('stores/', store_list, name='store-list'),
    path('contacts/', contact_list, name='contact-list'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('easy-tenants/', include('easy_tenants.urls')),
]
