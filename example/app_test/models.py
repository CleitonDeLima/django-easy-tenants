from django.db import models

from easy_tenants.models import TenantAwareAbstract, TenantManager


class Customer(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TenantModel(TenantAwareAbstract):
    tenant = models.ForeignKey(to=Customer, on_delete=models.CASCADE)

    objects = TenantManager()

    class Meta:
        abstract = True


class CategoryQuerySet(models.QuerySet):
    def start_by_xx(self):
        return self.filter(name__startswith="xxx")


class Product(TenantModel):
    name = models.CharField(max_length=50)
    category = models.ForeignKey("app_test.Category", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Category(TenantModel):
    name = models.CharField(max_length=50)

    objects = TenantManager.from_queryset(CategoryQuerySet)()

    def __str__(self):
        return self.name
