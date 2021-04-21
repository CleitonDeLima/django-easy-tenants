from django.db import models

from easy_tenants import get_current_tenant
from easy_tenants.conf import settings
from easy_tenants.utils import get_state


class TenantManager(models.Manager):
    def get_queryset(self):
        state = get_state()

        if not state.get("enabled", True):
            return super().get_queryset()

        current_tenant = get_current_tenant()
        return super().get_queryset().filter(tenant=current_tenant)

    def bulk_create(self, objs):
        tenant = get_current_tenant()

        for obj in objs:
            if hasattr(obj, "tenant_id"):
                obj.tenant = tenant

        return super().bulk_create(objs)


class TenantAbstract(models.Model):
    tenant = models.ForeignKey(
        to=settings.EASY_TENANTS_MODEL,
        on_delete=models.CASCADE,
        editable=False,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.tenant_id:
            self.tenant = get_current_tenant()

        super().save(*args, **kwargs)
