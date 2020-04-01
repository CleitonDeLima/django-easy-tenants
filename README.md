# easy-tenants

![Tests](https://github.com/CleitonDeLima/django-easy-tenants/workflows/Tests/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/CleitonDeLima/django-easy-tenants/badge.svg?branch=github-ci)](https://coveralls.io/github/CleitonDeLima/django-easy-tenants?branch=github-ci)
[![PyPI Version](https://img.shields.io/pypi/v/django-easy-tenants.svg)](https://pypi.org/project/django-easy-tenants/)
[![PyPI downloads](https://img.shields.io/pypi/dm/django-easy-tenants.svg)](https://img.shields.io/pypi/dm/django-easy-tenants.svg)


## Quick start
_(We advise you to make this change at the beginning of a project.)_

Add `easy_tenant` to your `INSTALLED_APPS` setting like this:

```python
INSTALLED_APPS = [
    ...,
    'easy_tenants',
]
```
   
Create your tenant model and define to your `EASY_TENANTS_MODEL` setting like this:

`yourapp/models.py`
```python
from easy_tenants.models import TenantMixin

class CustomModel(TenantMixin):
    ...
```

`settings.py`
```python
EASY_TENANTS_MODEL = 'yourapp.CustomModel'
```

Your models must inherit from `TenantAbstract` and use the manager `TenantManager`:

```python
from django.db import models
from easy_tenants.models import TenantAbstract
from easy_tenants.managers import TenantManager

class Product(TenantAbstract):
    name = models.CharField(max_length=10)

    objects = TenantManager()
```


- Includes url
```python
path('easy-tenants/', include('easy_tenants.urls')),
```
- set middleware


## Run example
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Access `/admin/` page and enjoy
