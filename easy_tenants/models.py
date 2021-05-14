from django.db import models
from django.db.models.expressions import BaseExpression
from django.db.models.functions import Cast

from easy_tenants import get_current_tenant
from easy_tenants.conf import settings
from easy_tenants.utils import get_state


class CurrentTenant(BaseExpression):
    def as_sql(self, compiler, connection, *args, **kwargs):
        current_tenant = get_current_tenant()
        tenant_id = str(current_tenant.id)
        value = self.output_field.get_db_prep_value(tenant_id, connection)
        return "%s", [str(value)]


class TenantManager(models.Manager):
    def get_queryset(self):
        state = get_state()
        queryset = super().get_queryset()

        if not state.get("enabled", True):
            return queryset

        field = self.model.tenant.field.target_field
        cr = CurrentTenant(output_field=field)
        queryset = queryset.filter(tenant_id=Cast(cr, output_field=field))
        return queryset

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
