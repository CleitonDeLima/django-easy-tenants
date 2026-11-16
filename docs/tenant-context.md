# Tenant context

To query the data of a tenant, activate it with
{class}`~easy_tenants.tenant_context`:

```python
from easy_tenants import tenant_context

with tenant_context(customer):
    Product.objects.all()  # only the products of this customer
    Product.objects.create(name="Shirt")  # saved with tenant=customer
```

Querying a tenant-aware model without an active tenant raises
{class}`easy_tenants.exceptions.TenantError`. To access the data of all
tenants, disable the filter with
{func}`~easy_tenants.tenant_context_disabled`:

```python
from easy_tenants import tenant_context_disabled

with tenant_context_disabled():
    Product.objects.all()  # the products of every tenant
```

Both can also be used as decorators, on regular or `async def` functions:

```python
@tenant_context(customer)
def import_products():
    ...


@tenant_context_disabled()
async def count_all_products():
    return await Product.objects.acount()
```

{func}`~easy_tenants.get_current_tenant` returns the active tenant (or
`None` when the filter is disabled):

```python
from easy_tenants import get_current_tenant

tenant = get_current_tenant()
```

The active tenant is stored in a {class}`~contextvars.ContextVar`, so it's
isolated per thread and per asyncio task, and contexts can be nested.

Querysets resolve the tenant when they are executed, not when they are
built, so a queryset created outside `tenant_context` returns the data of
the tenant active when it's evaluated.
