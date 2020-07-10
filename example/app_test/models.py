import uuid

from django.db import models
from easy_tenants.models import TenantMixin, TenantAbstract
from easy_tenants.managers import TenantManager


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TenantModel(TenantAbstract, BaseModel):
    objects = TenantManager()

    class Meta:
        abstract = True


class CategoryQuerySet(models.QuerySet):
    def start_by_xx(self):
        return self.filter(name__startswith='xxx')


class Customer(TenantMixin, BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(TenantModel):
    name = models.CharField(max_length=50)
    category = models.ForeignKey('app_test.Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Category(TenantModel):
    name = models.CharField(max_length=50)

    objects = TenantManager.from_queryset(CategoryQuerySet)()

    def __str__(self):
        return self.name
