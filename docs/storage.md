# File storage

To store uploaded files in a separate directory per tenant
(`MEDIA_ROOT/<tenant pk>/`), set
{class}`~easy_tenants.storage.TenantFileSystemStorage` as the default
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
