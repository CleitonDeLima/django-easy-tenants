# easy-tenants

![Tests](https://github.com/CleitonDeLima/django-easy-tenants/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/CleitonDeLima/django-easy-tenants/branch/master/graph/badge.svg)](https://codecov.io/gh/CleitonDeLima/django-easy-tenants)
[![PyPI Version](https://img.shields.io/pypi/v/django-easy-tenants.svg)](https://pypi.org/project/django-easy-tenants/)
[![PyPI downloads](https://img.shields.io/pypi/dm/django-easy-tenants.svg)](https://img.shields.io/pypi/dm/django-easy-tenants.svg)


This is a Django app for managing multiple tenants on the same project
instance using a shared approach.


## Background

There are typically three solutions for solving the multitenancy problem:

1. Isolated Approach: Separate Databases. Each tenant has it’s own database.
2. Semi Isolated Approach: Shared Database, Separate Schemas.
One database for all tenants, but one schema per tenant.
3. Shared Approach: Shared Database, Shared Schema. All tenants share
the same database and schema. There is a main tenant-table, where all
other tables have a foreign key pointing to.

This application implements the third approach,  which in our opinion,
is the best solution for a large amount of tenants.

For more information: [Building Multi Tenant Applications with Django
](https://books.agiliq.com/projects/django-multi-tenant/en/latest/)

Below is a demonstration of the features in each approach for an application
with 5000 tenants.

Approach       | Number of DB | Number of Schemas | Django migration time | Public access
-------------- | ------------ | ----------------- | --------------------- | ---------------
Isolated       | 5000         | 5000              | slow (1/DB)           | No
Semi Isolated  | 1            | 5000              | slow (1/Schema)       | Yes
Shared         | 1            | 1                 | fast (1)              | Yes


## Installation
Assuming you have django installed, the first step is to install `django-easy-tenants`.
```bash
python -m pip install django-easy-tenants
```
Now you can import the tenancy module in your Django project.


## Setup
It is recommended to install this app at the beginning of a project.
In an existing project, depending on the structure of the models,
the data migration can be hard.

Add `easy_tenants` to your `INSTALLED_APPS` on `settings.py`.

`settings.py`
```python
INSTALLED_APPS = [
    ...,
    'easy_tenants',
]
```

Create a model which will be the tenant of the application.

`yourapp/models.py`
```python
from django.db import models

class Customer(models.Model):
    ...
```

Your models, which must have isolated data per tenant, we need to add the foreign field from the Customer model.
and objects need to be replaced with `TenantManager()`.


```python
from django.db import models
from easy_tenants.models import TenantManager

class Product(models.Model):
    tenant = models.ForeignKey(Customer, on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=10)

    objects = TenantManager()
```

If you prefer you can use `TenantAwareAbstract` to implement the save method for you,
so when saving an object the tenant will be automatically defined.

```python
class Product(TenantAwareAbstract):
    tenant = models.ForeignKey(Customer, on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=10)

    objects = TenantManager()
```


If your foreign field has a name other than `tenant` you can change it with a settings. (default is `"tenant"`)

```python
# models.py
class Product(TenantAwareAbstract):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=10)

    objects = TenantManager()

# settings.py
EASY_TENANTS_TENANT_FIELD = "customer"
```

To obtain the data for each tenant, it is necessary to define which tenant will be used:

```python
from easy_tenants import tenant_context

with tenant_context(customer):
    Product.objects.all()  # filter by customer
```

To define the tenant to be used, this will depend on the business rule used. Here is an example for creating middleware that defines a tenant:

```python
from django.http import HttpResponse
from easy_tenants import tenant_context

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        customer = get_customer_by_request(request)

        if not customer:
            return HttpResponse("Select tenant")

        with tenant_context(customer):
            return self.get_response(request)
```

If you want to separate the upload files by tenant, you need to change the `DEFAULT_FILE_STORAGE`
configuration (only available for local files).

```python
DEFAULT_FILE_STORAGE = 'easy_tenants.storage.TenantFileSystemStorage'
```


## Running the example project
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Access the page `/admin/`, create a `Customer`.

## Motivation
[django-tenant-schemas](https://github.com/bernardopires/django-tenant-schemas)

[django-tenants](https://github.com/tomturner/django-tenants)

[django-scopes](https://github.com/raphaelm/django-scopes)
