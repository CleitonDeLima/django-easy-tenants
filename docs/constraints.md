# UniqueTenantConstraint

{class}`~easy_tenants.models.UniqueTenantConstraint` is a Django constraint
that enforces uniqueness within each tenant. It allows the same values to
exist across different tenants, but not twice in the same tenant.

## How it works

The constraint automatically adds the tenant field to the fields checked for
uniqueness. For example, two tenants can have products with the same name
and SKU, but a single tenant cannot have two products with the same name and
SKU.

## Usage example

To make each product's `name` and `sku` combination unique per tenant:

```python
from django.db import models

from easy_tenants.models import (
    TenantAwareAbstract,
    TenantManager,
    UniqueTenantConstraint,
)


class Product(TenantAwareAbstract):
    tenant = models.ForeignKey(
        Customer, on_delete=models.CASCADE, editable=False
    )
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

## Notes

- The tenant field is added automatically, so don't include it in `fields`.
- Expressions are also supported, e.g.
  `UniqueTenantConstraint(Lower("name"), name="...")`.
- Model validation (`full_clean()`, model forms) raises a
  {class}`~django.core.exceptions.ValidationError` when the constraint is
  violated. Calling `save()` directly without validating raises the
  database's {class}`~django.db.IntegrityError`.
