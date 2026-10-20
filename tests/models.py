import uuid

from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from easy_tenants.models import (
    TenantAwareAbstract,
    TenantManager,
    UniqueTenantConstraint,
)


class ContactQuery(models.QuerySet):
    def by_phone(self):
        return self.filter(name__startswith="phone")


class StoreTenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class TenantModel(TenantAwareAbstract):
    store = models.ForeignKey(
        to=StoreTenant, on_delete=models.CASCADE, editable=False
    )

    objects = TenantManager()

    class Meta:
        abstract = True


class Product(TenantModel):
    name = models.CharField(max_length=10)
    category = models.ForeignKey(
        "tests.Category", null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name


class Category(TenantModel):
    name = models.CharField(max_length=10)

    class Meta:
        constraints = [
            UniqueTenantConstraint(Lower("name"), name="unique_name_store"),
        ]

    def __str__(self):
        return self.name


class Contact(TenantModel):
    name = models.CharField(max_length=10)

    objects = TenantManager.from_queryset(ContactQuery)()


class Order(TenantModel):
    product = models.ForeignKey("tests.Product", on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    sku = models.CharField(max_length=4, blank=True)

    class Meta:
        constraints = [
            UniqueTenantConstraint(fields=["code"], name="unique_code_store"),
            UniqueTenantConstraint(
                fields=["sku"],
                condition=~Q(sku=""),
                name="unique_sku_store",
                violation_error_message="Sku exists!",
                violation_error_code="sku_exists",
            ),
        ]


class Warehouse(models.Model):
    """Tenant whose primary key is not named ``id``."""

    code = models.CharField(primary_key=True, max_length=10)
    slug = models.SlugField(unique=True)


class Shelf(TenantAwareAbstract):
    store = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    objects = TenantManager()


class Bin(TenantAwareAbstract):
    store = models.ForeignKey(
        Warehouse, to_field="slug", on_delete=models.CASCADE
    )

    objects = TenantManager()
