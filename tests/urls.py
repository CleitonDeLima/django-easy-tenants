from django.urls import path, include

from tests.views import home

urlpatterns = [
    path('', home, name='home'),

    path('easy-tenants/', include('easy_tenants.urls')),
]
