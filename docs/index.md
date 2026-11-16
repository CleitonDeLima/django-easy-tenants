# django-easy-tenants

A Django app for managing multiple tenants in the same project instance
using the shared approach.

## Background

There are typically three approaches to multitenancy:

1. Isolated approach: separate databases. Each tenant has its own database.
2. Semi-isolated approach: shared database, separate schemas. One database
   for all tenants, but one schema per tenant.
3. Shared approach: shared database, shared schema. All tenants share the
   same database and schema. A main tenant table is referenced by a foreign
   key from every other table.

This app implements the third approach which, in our opinion, is the best
solution for a large number of tenants.

For more information, see [Building Multi Tenant Applications with
Django](https://books.agiliq.com/projects/django-multi-tenant/en/latest/).

The table below compares the approaches for an application with 5000
tenants. "Public access" means data that is shared by all tenants (e.g. a
plans table) can be stored once and queried directly.

| Approach      | Databases | Schemas | Django migration time | Public access |
| ------------- | --------- | ------- | --------------------- | ------------- |
| Isolated      | 5000      | 5000    | slow (1/DB)           | No            |
| Semi-isolated | 1         | 5000    | slow (1/schema)       | Yes           |
| Shared        | 1         | 1       | fast (1)              | Yes           |

## Related projects

Other multitenancy libraries for Django that inspired this project:

- [django-tenant-schemas](https://github.com/bernardopires/django-tenant-schemas)
- [django-tenants](https://github.com/tomturner/django-tenants)
- [django-scopes](https://github.com/raphaelm/django-scopes)

```{toctree}
:hidden:

installation
tenant-context
middleware
storage
constraints
management
checks
example-project
api
changelog
```
