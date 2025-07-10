from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.db.models.expressions import BaseExpression

from easy_tenants import get_current_tenant
from easy_tenants.utils import get_state

tenant_field_name = getattr(settings, "EASY_TENANTS_TENANT_FIELD", "tenant")


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

        field = getattr(self.model, tenant_field_name).field.target_field
        filter_kwargs = {tenant_field_name: CurrentTenant(output_field=field)}

        return queryset.filter(**filter_kwargs)

    def bulk_create(self, objs, *args, **kwargs):
        tenant = get_current_tenant()

        if tenant:
            for obj in objs:
                setattr(obj, tenant_field_name, tenant)

        return super().bulk_create(objs, *args, **kwargs)


class TenantAwareAbstract(models.Model):
    """Abstract model that implements the model save defining a tenant"""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Set tenant field on save"""
        setattr(self, tenant_field_name, get_current_tenant())

        super().save(*args, **kwargs)

    def get_tenant_instance(self):
        """Returns the model's tenant instance"""
        return getattr(self, tenant_field_name)


class UniqueTenantConstraint(UniqueConstraint):
    def validate(self, model, instance, *args, **kwargs):
        default_fields = self.fields

        if tenant_field_name not in default_fields:
            self.fields = list(default_fields) + [tenant_field_name]

        setattr(instance, tenant_field_name, get_current_tenant())

        try:
            super().validate(model, instance, *args, **kwargs)
        except ValidationError as e:
            message_fields = [
                field for field in default_fields if field != tenant_field_name
            ]
            use_default_message = (
                self.violation_error_message
                == self.default_violation_error_message
            )
            if use_default_message:
                error = instance.unique_error_message(model, message_fields)
                self.violation_error_message = error.message % error.params

            raise ValidationError(self.violation_error_message) from e
