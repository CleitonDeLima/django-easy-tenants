# Middleware

A middleware activates the tenant of each request, so views don't need
`tenant_context`. Two middlewares are available; add one of them after
{class}`~django.contrib.auth.middleware.AuthenticationMiddleware`:

- {class}`~easy_tenants.middleware.SessionTenantMiddleware` reads the tenant
  id from the session key `"tenant_id"` (e.g. saved by a "choose tenant"
  view).
- {class}`~easy_tenants.middleware.HeaderTenantMiddleware` reads the tenant
  id from the `X-Tenant-ID` header (e.g. for APIs).

```python
MIDDLEWARE = [
    ...,
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "easy_tenants.middleware.SessionTenantMiddleware",
]
```

The tenant is loaded from `EASY_TENANTS_TENANT_MODEL` by primary key and is
available as `request.tenant`. When no tenant is found, views that require a
tenant raise {class}`~django.core.exceptions.PermissionDenied` (HTTP 403).

## Views without a tenant

Every view requires a tenant unless it's marked otherwise with
{func}`~easy_tenants.decorators.tenant_not_required`. The
`django.contrib.auth` login, logout and password reset views are already
marked.

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

## Customizing

:::{warning}
The middlewares don't check whether the user may access the tenant: any
user can activate any tenant by changing the header, or the session value
if your code doesn't validate it before saving. Override `get_tenant()` to
check it, as shown below.
:::

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
{class}`easy_tenants.middleware.TenantMiddleware` and implement
`get_tenant_id(request)`. Both sync and async views are supported.

:::{note}
With token authentication in Django REST framework the user is
authenticated in the view, after the middleware runs, so `request.user` is
still anonymous inside `get_tenant()`.
:::
