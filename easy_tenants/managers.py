from django.db import models
from django.utils.functional import SimpleLazyObject

from easy_tenants import get_current_tenant


def _tenant_manager_constructor(manager_class=models.Manager):
    class Manager(manager_class):
        def get_queryset(self):
            return super().get_queryset().filter(
                tenant=SimpleLazyObject(get_current_tenant)
            )

        def contribute_to_class(self, model, name):
            super().contribute_to_class(model, name)

            models.signals.pre_save.connect(_set_tenant, model)

    manager = Manager()
    manager.tenant_manager = True

    return manager


def _set_tenant(instance, **kwargs):
    instance.tenant = get_current_tenant()


TenantManager = _tenant_manager_constructor
