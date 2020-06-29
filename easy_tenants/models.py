from django.db import models

from easy_tenants import get_current_tenant
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
        on_delete=models.CASCADE,
        editable=False
    )

    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.tenant = get_current_tenant()
        super().save(*args, **kwargs)
