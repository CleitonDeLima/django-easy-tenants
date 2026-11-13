# django-easy-tenants

[![Tests](https://github.com/CleitonDeLima/django-easy-tenants/actions/workflows/tests-ci.yml/badge.svg)](https://github.com/CleitonDeLima/django-easy-tenants/actions/workflows/tests-ci.yml)
[![codecov](https://codecov.io/gh/CleitonDeLima/django-easy-tenants/branch/main/graph/badge.svg)](https://codecov.io/gh/CleitonDeLima/django-easy-tenants)
[![PyPI Version](https://img.shields.io/pypi/v/django-easy-tenants.svg)](https://pypi.org/project/django-easy-tenants/)
[![PyPI downloads](https://img.shields.io/pypi/dm/django-easy-tenants.svg)](https://pypistats.org/packages/django-easy-tenants)


A Django app for managing multiple tenants in the same project instance
using the shared approach.


## Background

There are typically three approaches to multitenancy:

1. Isolated approach: separate databases. Each tenant has its own database.
2. Semi-isolated approach: shared database, separate schemas. One database
for all tenants, but one schema per tenant.
3. Shared approach: shared database, shared schema. All tenants share the
same database and schema. A main tenant table is referenced by a foreign key
from every other table.

This app implements the third approach which, in our opinion, is the best
solution for a large number of tenants.

For more information, see [Building Multi Tenant Applications with
Django](https://books.agiliq.com/projects/django-multi-tenant/en/latest/).

The table below compares the approaches for an application with 5000
tenants. "Public access" means data that is shared by all tenants (e.g. a
plans table) can be stored once and queried directly.

Approach       | Databases | Schemas | Django migration time | Public access
-------------- | --------- | ------- | --------------------- | -------------
Isolated       | 5000      | 5000    | slow (1/DB)           | No
Semi-isolated  | 1         | 5000    | slow (1/schema)       | Yes
Shared         | 1         | 1       | fast (1)              | Yes


## Installation
Assuming you have Django installed, install `django-easy-tenants`:

```bash
python -m pip install django-easy-tenants
```


## Setup
It is recommended to adopt this app at the beginning of a project. In an
existing project, depending on the structure of the models, migrating the
data can be hard.

Add `easy_tenants` to `INSTALLED_APPS` in `settings.py`.

`settings.py`
```python
INSTALLED_APPS = [
    ...,
    "easy_tenants",
]
```

Create the model that will be the tenant of the application.

`yourapp/models.py`
```python
from django.db import models

class Customer(models.Model):
    ...
```

`settings.py`
```python
EASY_TENANTS_TENANT_MODEL = "yourapp.Customer"
```

Models whose data must be isolated per tenant need a `ForeignKey` to the
tenant model, must inherit from `TenantAwareAbstract` and must use
`TenantManager` as their manager:

- `TenantManager` filters every query by the active tenant.
- `TenantAwareAbstract` sets the active tenant on the object when it's
  created, so you never assign the foreign key yourself. Without it, you
  must set the tenant before saving.

`yourapp/models.py`
```python
from django.db import models
from easy_tenants.models import TenantAwareAbstract, TenantManager

class Product(TenantAwareAbstract):
    tenant = models.ForeignKey(Customer, on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=10)

    objects = TenantManager()
```

If the foreign key has a name other than `tenant` (the default), set it with
the `EASY_TENANTS_TENANT_FIELD` setting. This setting is global: every
tenant-aware model must use the same field name.

```python
# models.py
class Product(TenantAwareAbstract):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=10)

    objects = TenantManager()

# settings.py
EASY_TENANTS_TENANT_FIELD = "customer"
```


## Tenant context
To query the data of a tenant, activate it with `tenant_context`:

```python
from easy_tenants import tenant_context

with tenant_context(customer):
    Product.objects.all()  # only the products of this customer
    Product.objects.create(name="Shirt")  # saved with tenant=customer
```

Querying a tenant-aware model without an active tenant raises
`easy_tenants.exceptions.TenantError`. To access the data of all tenants,
disable the filter with `tenant_context_disabled`:

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

`get_current_tenant()` returns the active tenant (or `None` when the filter
is disabled):

```python
from easy_tenants import get_current_tenant

tenant = get_current_tenant()
```


## Middleware
A middleware activates the tenant of each request, so views don't need
`tenant_context`. Two middlewares are available; add one of them after
`AuthenticationMiddleware`:

- `easy_tenants.middleware.SessionTenantMiddleware` reads the tenant id from
  the session key `"tenant_id"` (e.g. saved by a "choose tenant" view).
- `easy_tenants.middleware.HeaderTenantMiddleware` reads the tenant id from
  the `X-Tenant-ID` header (e.g. for APIs).

```python
MIDDLEWARE = [
    ...,
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "easy_tenants.middleware.SessionTenantMiddleware",
]
```

The tenant is loaded from `EASY_TENANTS_TENANT_MODEL` by primary key and is
available as `request.tenant`. When no tenant is found, views that require a
tenant raise `PermissionDenied` (HTTP 403). Every view requires a tenant
unless it's marked otherwise (the `django.contrib.auth` login, logout and
password reset views are already marked):

```python
from django.utils.decorators import method_decorator
from django.views import View
from easy_tenants.decorators import tenant_not_required

@tenant_not_required
def choose_tenant(request):
    ...

@method_decorator(tenant_not_required, name="dispatch")
class ChooseTenantView(View):
    ...
```

> [!WARNING]
> The middlewares don't check whether the user may access the tenant: any
> user can activate any tenant by changing the header, or the session value
> if your code doesn't validate it before saving. Override `get_tenant()` to
> check it, as shown below.

Customize the behavior by subclassing:

```python
from django.shortcuts import redirect
from easy_tenants.middleware import SessionTenantMiddleware

class TenantMiddleware(SessionTenantMiddleware):
    session_key = "customer_id"  # or header_name in HeaderTenantMiddleware

    def get_tenant(self, request):
        tenant = super().get_tenant(request)
        if tenant is not None and request.user.customers.contains(tenant):
            return tenant
        return None

    def tenant_not_found(self, request):
        return redirect("choose-tenant")  # or return a JSON error
```

To read the tenant from somewhere else (subdomain, URL, token...), subclass
`easy_tenants.middleware.TenantMiddleware` and implement
`get_tenant_id(request)`. Both sync and async views are supported.

Note that with token authentication in Django REST framework the user is
authenticated in the view, after the middleware runs, so `request.user` is
still anonymous inside `get_tenant()`.


## File storage
To store uploaded files in a separate directory per tenant
(`MEDIA_ROOT/<tenant pk>/`), set `TenantFileSystemStorage` as the default
storage (local files only):

```python
STORAGES = {
    "default": {
        "BACKEND": "easy_tenants.storage.TenantFileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```

Inside `tenant_context_disabled()` files are stored in `MEDIA_ROOT` itself.


## UniqueTenantConstraint
`UniqueTenantConstraint` is a Django constraint that enforces uniqueness
within each tenant. It allows the same values to exist across different
tenants, but not twice in the same tenant.

### How it works
The constraint automatically adds the tenant field to the fields checked for
uniqueness. For example, two tenants can have products with the same name
and SKU, but a single tenant cannot have two products with the same name and
SKU.

### Usage example
To make each product's `name` and `sku` combination unique per tenant:

```python
from django.db import models

from easy_tenants.models import (
    TenantAwareAbstract,
    TenantManager,
    UniqueTenantConstraint,
)


class Product(TenantAwareAbstract):
    tenant = models.ForeignKey(Customer, on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    objects = TenantManager()

    class Meta:
        constraints = [
            UniqueTenantConstraint(
                fields=["name", "sku"],
                name="unique_product_name_sku_per_tenant",
            )
        ]
```

With this constraint:
- Tenant A can have a product with name "Shirt" and SKU "123".
- Tenant B can also have a product with name "Shirt" and SKU "123".
- Tenant A cannot have a second product with name "Shirt" and SKU "123".

### Notes
- The tenant field is added automatically, so don't include it in `fields`.
- Expressions are also supported, e.g.
  `UniqueTenantConstraint(Lower("name"), name="...")`.
- Model validation (`full_clean()`, model forms) raises a `ValidationError`
  when the constraint is violated. Calling `save()` directly without
  validating raises the database's `IntegrityError`.


## Management command
`shell_tenant` opens a Django shell (or `shell_plus`, if
[django-extensions](https://github.com/django-extensions/django-extensions)
is installed) with a tenant already active:

```bash
python manage.py shell_tenant --tenant_id=1  # activate the tenant with pk 1
python manage.py shell_tenant --disable      # access the data of all tenants
```


## System checks
django-easy-tenants registers [system checks](https://docs.djangoproject.com/en/stable/topics/checks/)
that run with `manage.py check` (and on `runserver`/`migrate`) to catch
misconfiguration early. A model is *tenant-aware* when it inherits
`TenantAwareAbstract` or uses `TenantManager`.

| ID | Problem |
|----|---------|
| `easy_tenants.E001` | `EASY_TENANTS_TENANT_MODEL` isn't of the form `app_label.ModelName`. |
| `easy_tenants.E002` | `EASY_TENANTS_TENANT_MODEL` refers to a model that isn't installed. |
| `easy_tenants.E003` | `EASY_TENANTS_TENANT_MODEL` isn't set, but a tenant middleware is in `MIDDLEWARE`. |
| `easy_tenants.E004` | A tenant-aware model has no field named `EASY_TENANTS_TENANT_FIELD`. |
| `easy_tenants.E005` | That field isn't a `ForeignKey` or `OneToOneField`. |
| `easy_tenants.E006` | That field doesn't point to `EASY_TENANTS_TENANT_MODEL`. |
| `easy_tenants.E007` | `SessionTenantMiddleware` is in `MIDDLEWARE` without `SessionMiddleware` before it. |

Models with a foreign key to the tenant that don't use `TenantManager` (e.g. a
`Membership` linking users to tenants) are not reported: they are unfiltered
on purpose.


## Running the example project
From the repository root, with the package installed:

```bash
python -m pip install -e . -r example/requirements.txt
cd example
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `/admin/`, log in and create a `Customer`. Then open `/`, choose the
customer and create categories and products for it.


## Related projects
Other multitenancy libraries for Django that inspired this project:

- [django-tenant-schemas](https://github.com/bernardopires/django-tenant-schemas)
- [django-tenants](https://github.com/tomturner/django-tenants)
- [django-scopes](https://github.com/raphaelm/django-scopes)
