from django.contrib import admin
from django.urls import path, include

from example.app_test.views import home, customer_list

urlpatterns = [
    path('', home, name='home'),

    path('customers/', customer_list, name='customer-list'),

    path('admin/', admin.site.urls),

    path('easy-tenants/', include('easy_tenants.urls')),
]
