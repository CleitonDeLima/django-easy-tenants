import uuid

from django.db import models

from easy_tenants.models import TenantAbstract, TenantManager


class ContactQuery(models.QuerySet):
    def by_phone(self):
        return self.filter(name__startswith="phone")


class StoreTenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Product(TenantAbstract):
    name = models.CharField(max_length=10)
    category = models.ForeignKey(
        "tests.Category", null=True, on_delete=models.SET_NULL
    )

    objects = TenantManager()

    def __str__(self):
        return self.name


class Category(TenantAbstract):
    name = models.CharField(max_length=10)

    objects = TenantManager()

    def __str__(self):
        return self.name


class Contact(TenantAbstract):
    name = models.CharField(max_length=10)

    objects = TenantManager.from_queryset(ContactQuery)()
