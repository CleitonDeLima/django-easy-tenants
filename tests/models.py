from django.db import models
from django.db.models import Manager

from easy_tenants.managers import TenantManager
from easy_tenants.models import TenantAbstract


class ContactQuery(models.QuerySet):
    def by_phone(self):
        return self.filter(name__startswith='phone')


class StoreTenant(models.Model):
    pass


class Product(TenantAbstract):
    name = models.CharField(max_length=10)

    objects = TenantManager()


class Contact(TenantAbstract):
    name = models.CharField(max_length=10)

    objects = TenantManager(Manager.from_queryset(ContactQuery))
