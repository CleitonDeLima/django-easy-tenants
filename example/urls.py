from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from example.app_test.views import home, customer_list

urlpatterns = [
    path('', home, name='home'),

    path('customers/', customer_list, name='customer-list'),

    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),
    path('easy-tenants/', include('easy_tenants.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
