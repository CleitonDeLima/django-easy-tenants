# Installation

Assuming you have Django installed, install `django-easy-tenants`:

```bash
python -m pip install django-easy-tenants
```

## Setup

It is recommended to adopt this app at the beginning of a project. In an
existing project, depending on the structure of the models, migrating the
data can be hard.

Add `easy_tenants` to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "easy_tenants",
]
```

Create the model that will be the tenant of the application:

```python
# yourapp/models.py
from django.db import models


class Customer(models.Model):
    ...
```

```python
# settings.py
EASY_TENANTS_TENANT_MODEL = "yourapp.Customer"
```

Models whose data must be isolated per tenant need a
{class}`~django.db.models.ForeignKey` to the tenant model, must inherit from
{class}`~easy_tenants.models.TenantAwareAbstract` and must use
{class}`~easy_tenants.models.TenantManager` as their manager:

- `TenantManager` filters every query by the active tenant.
- `TenantAwareAbstract` sets the active tenant on the object when it's
  created, so you never assign the foreign key yourself. Without it, you
  must set the tenant before saving.

```python
# yourapp/models.py
from django.db import models
from easy_tenants.models import TenantAwareAbstract, TenantManager


class Product(TenantAwareAbstract):
    tenant = models.ForeignKey(
        Customer, on_delete=models.CASCADE, editable=False
    )
    name = models.CharField(max_length=10)

    objects = TenantManager()
```

## Settings

`EASY_TENANTS_TENANT_MODEL`
: The tenant model, in the form `app_label.ModelName`.

`EASY_TENANTS_TENANT_FIELD`
: The name of the foreign key to the tenant on tenant-aware models. Defaults
  to `"tenant"`. This setting is global: every tenant-aware model must use
  the same field name.

```python
# models.py
class Product(TenantAwareAbstract):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, editable=False
    )
    name = models.CharField(max_length=10)

    objects = TenantManager()


# settings.py
EASY_TENANTS_TENANT_FIELD = "customer"
```
