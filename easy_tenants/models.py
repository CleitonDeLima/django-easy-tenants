from django.db import models

from easy_tenants.conf import settings


class TenantMixin(models.Model):
    users = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        related_name='tenants'
    )

    class Meta:
        abstract = True


class TenantAbstract(models.Model):
    tenant = models.ForeignKey(
        to=settings.EASY_TENANTS_MODEL,
        on_delete=models.CASCADE
    )

    all_objects = models.Manager()

    class Meta:
        abstract = True
