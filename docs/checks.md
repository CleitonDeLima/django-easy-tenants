# System checks

django-easy-tenants registers
[system checks](https://docs.djangoproject.com/en/stable/topics/checks/)
that run with `manage.py check` (and on `runserver`/`migrate`) to catch
misconfiguration early. A model is *tenant-aware* when it inherits
`TenantAwareAbstract` or uses `TenantManager`.

| ID                  | Problem                                                                              |
| ------------------- | ------------------------------------------------------------------------------------ |
| `easy_tenants.E001` | `EASY_TENANTS_TENANT_MODEL` isn't of the form `app_label.ModelName`.                 |
| `easy_tenants.E002` | `EASY_TENANTS_TENANT_MODEL` refers to a model that isn't installed.                  |
| `easy_tenants.E003` | `EASY_TENANTS_TENANT_MODEL` isn't set, but a tenant middleware is in `MIDDLEWARE`.   |
| `easy_tenants.E004` | A tenant-aware model has no field named `EASY_TENANTS_TENANT_FIELD`.                 |
| `easy_tenants.E005` | That field isn't a `ForeignKey` or `OneToOneField`.                                  |
| `easy_tenants.E006` | That field doesn't point to `EASY_TENANTS_TENANT_MODEL`.                             |
| `easy_tenants.E007` | `SessionTenantMiddleware` is in `MIDDLEWARE` without `SessionMiddleware` before it.  |

Models with a foreign key to the tenant that don't use `TenantManager` (e.g.
a `Membership` linking users to tenants) are not reported: they are
unfiltered on purpose.
