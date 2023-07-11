from django.db import models
from django.db.models.expressions import BaseExpression

from easy_tenants import get_current_tenant
from easy_tenants.conf import settings
from easy_tenants.utils import get_state

field_name = settings.EASY_TENANTS_TENANT_FIELD


class CurrentTenant(BaseExpression):
    """Expression used to get tenant only when sql is actually executed"""

    def as_sql(self, compiler, connection, *args, **kwargs):
        current_tenant = get_current_tenant()
        tenant_id = str(current_tenant.id)
        value = self.output_field.get_db_prep_value(tenant_id, connection)

        return "%s", [str(value)]


class TenantManager(models.Manager):
    """Responsible for applying the tenants filter in the querysets"""

    def get_queryset(self):
        state = get_state()
        queryset = super().get_queryset()

        if not state.get("enabled", True):
            return queryset

        field = getattr(self.model, field_name).field.target_field
        filter_kwargs = {field_name: CurrentTenant(output_field=field)}

        return queryset.filter(**filter_kwargs)

    def bulk_create(self, objs, *args, **kwargs):
        tenant = get_current_tenant()

        for obj in objs:
            setattr(obj, field_name, tenant)

        return super().bulk_create(objs, *args, **kwargs)


class TenantAwareAbstract(models.Model):
    """Abstract model that implements the model save defining a tenant"""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Set tenant field on save"""
        setattr(self, field_name, get_current_tenant())

        super().save(*args, **kwargs)

    def get_tenant_instance(self):
        """Returns the model's tenant instance"""
        return getattr(self, field_name)
