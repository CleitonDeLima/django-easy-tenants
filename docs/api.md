# API reference

## Tenant context

```{eval-rst}
.. autoclass:: easy_tenants.tenant_context

.. autofunction:: easy_tenants.tenant_context_disabled

.. autofunction:: easy_tenants.get_current_tenant

.. autoexception:: easy_tenants.exceptions.TenantError
```

## Models

```{eval-rst}
.. autoclass:: easy_tenants.models.TenantAwareAbstract
   :members: get_tenant_instance

.. autoclass:: easy_tenants.models.TenantManager

.. autoclass:: easy_tenants.models.UniqueTenantConstraint
```

## Middleware

```{eval-rst}
.. autoclass:: easy_tenants.middleware.TenantMiddleware
   :members: get_tenant_id, get_tenant, tenant_not_found, tenant_required,
      get_context

.. autoclass:: easy_tenants.middleware.SessionTenantMiddleware

.. autoclass:: easy_tenants.middleware.HeaderTenantMiddleware
```

## Decorators

```{eval-rst}
.. autofunction:: easy_tenants.decorators.tenant_not_required
```

## Storage

```{eval-rst}
.. autoclass:: easy_tenants.storage.TenantFileSystemStorage
```
