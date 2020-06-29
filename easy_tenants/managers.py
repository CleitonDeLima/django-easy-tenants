from django.db import models
from django.db.models import Field

from easy_tenants import get_current_tenant


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


def _tenant_manager_constructor(manager_class=models.Manager):
    class Manager(manager_class):
        def get_queryset(self):
            return super().get_queryset().filter(tenant__id__ct=0)

        def bulk_create(self, objs):
            tenant = get_current_tenant()

            for obj in objs:
                if hasattr(obj, 'tenant_id'):
                    obj.tenant = tenant

            return super().bulk_create(objs)

    manager = Manager()
    manager.tenant_manager = True

    return manager


TenantManager = _tenant_manager_constructor
