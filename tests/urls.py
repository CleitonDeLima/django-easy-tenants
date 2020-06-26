from django.urls import path, include

from tests.views import home, store_list, contact_list

urlpatterns = [
    path('', home, name='home'),
    path('stores/', store_list, name='store-list'),
    path('contacts/', contact_list, name='contact-list'),

    path('easy-tenants/', include('easy_tenants.urls')),
]
