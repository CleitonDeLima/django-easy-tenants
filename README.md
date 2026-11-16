# django-easy-tenants

[![Tests](https://github.com/CleitonDeLima/django-easy-tenants/actions/workflows/tests-ci.yml/badge.svg)](https://github.com/CleitonDeLima/django-easy-tenants/actions/workflows/tests-ci.yml)
[![codecov](https://codecov.io/gh/CleitonDeLima/django-easy-tenants/branch/main/graph/badge.svg)](https://codecov.io/gh/CleitonDeLima/django-easy-tenants)
[![PyPI Version](https://img.shields.io/pypi/v/django-easy-tenants.svg)](https://pypi.org/project/django-easy-tenants/)
[![PyPI downloads](https://img.shields.io/pypi/dm/django-easy-tenants.svg)](https://pypistats.org/packages/django-easy-tenants)
[![Documentation](https://readthedocs.org/projects/django-easy-tenants/badge/?version=latest)](https://django-easy-tenants.readthedocs.io/)

A Django app for managing multiple tenants in the same project instance
using the shared approach: one database and one schema for all tenants,
with every tenant-isolated table referencing the tenant by a foreign key.

**Documentation:** https://django-easy-tenants.readthedocs.io/


## Installation

```bash
python -m pip install django-easy-tenants
```


## Quickstart

Add the app and point it to your tenant model:

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "easy_tenants",
]

EASY_TENANTS_TENANT_MODEL = "yourapp.Customer"
```

Make the models that must be isolated per tenant tenant-aware:

```python
# yourapp/models.py
from django.db import models
from easy_tenants.models import TenantAwareAbstract, TenantManager


class Customer(models.Model):
    ...


class Product(TenantAwareAbstract):
    tenant = models.ForeignKey(Customer, on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=10)

    objects = TenantManager()
```

Activate a tenant to query and create its data:

```python
from easy_tenants import tenant_context

with tenant_context(customer):
    Product.objects.all()  # only the products of this customer
    Product.objects.create(name="Shirt")  # saved with tenant=customer
```

In views, a middleware activates the tenant of each request:

```python
MIDDLEWARE = [
    ...,
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "easy_tenants.middleware.SessionTenantMiddleware",
]
```

> [!WARNING]
> The middlewares don't check whether the user may access the tenant. See
> [Customizing](https://django-easy-tenants.readthedocs.io/en/latest/middleware.html#customizing)
> to add that check.

See the [documentation](https://django-easy-tenants.readthedocs.io/) for
the middlewares, per-tenant file storage, `UniqueTenantConstraint`, the
`shell_tenant` command, the system checks and the API reference.
