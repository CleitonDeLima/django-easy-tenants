from django.db import models
from django.db.models import Field

from easy_tenants import get_current_tenant

FAKE_FILTER = 0


@Field.register_lookup
class CurrentTenant(models.Lookup):
    lookup_name = 'ct'

    def as_sqlite(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        tenant = get_current_tenant()
        params = lhs_params
        # fix uuid(id) fields, char(32) without '-'
        tenant_id = str(tenant.id).replace('-', '')

        return "%s = '%s'" % (lhs, tenant_id), params

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        tenant = get_current_tenant()
        params = lhs_params

        return "%s = '%s'" % (lhs, tenant.id), params


class TenantManager(models.Manager):
    tenant_manager = True

    def get_queryset(self):
        return super().get_queryset().filter(tenant__id__ct=FAKE_FILTER)

    def bulk_create(self, objs):
        tenant = get_current_tenant()

        for obj in objs:
            if hasattr(obj, 'tenant_id'):
                obj.tenant = tenant

        return super().bulk_create(objs)
