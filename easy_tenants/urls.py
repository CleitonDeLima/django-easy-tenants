from django.urls import path

from easy_tenants.views import set_tenant

app_name = 'easy_tenants'

urlpatterns = [
    path('<str:pk>/set-current-tenant/', set_tenant,
         name='set-current-tenant'),
]
