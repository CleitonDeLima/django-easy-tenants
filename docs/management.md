# Management command

## `shell_tenant`

Opens a Django shell (or `shell_plus`, if
[django-extensions](https://github.com/django-extensions/django-extensions)
is installed) with a tenant already active:

```bash
python manage.py shell_tenant --tenant_id=1  # activate the tenant with pk 1
python manage.py shell_tenant --disable      # access the data of all tenants
```
