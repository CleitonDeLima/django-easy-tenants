from django.conf import settings
from django.db import models

from easy_tenants.models import TenantManager, get_current_tenant


class Customer(models.Model):
    name = models.CharField(max_length=50)
    users = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        related_name="tenants",
    )

    def __str__(self):
        return self.name


class TenantModel(models.Model):
    tenant = models.ForeignKey(
        to=Customer, on_delete=models.CASCADE, editable=False
    )

    objects = TenantManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.tenant_id:
            self.tenant = get_current_tenant()

        super().save(*args, **kwargs)


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
