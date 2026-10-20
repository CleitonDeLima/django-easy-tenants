# Changelog

## [Unreleased]
- Added support for Django 6.0, 6.1 and Python 3.13, 3.14, 3.15 (#138)
- Dropped support for Python < 3.11 and Django < 5.2 (#138)
- Added GitHub Actions workflow to publish the package to PyPI on release
- Fixed `TenantManager.bulk_create()` creating nothing when given a generator
- Added support for expressions in `UniqueTenantConstraint`
- Fixed `UniqueTenantConstraint.validate()` overwriting the tenant of existing
  instances (e.g. clearing it inside `tenant_context_disabled()`)
- Fixed `UniqueTenantConstraint` dropping the error `code` and freezing the
  default message in the language of the first violation
- Fixed tenants whose primary key isn't named `id`, or that are referenced
  through a `to_field`; `TenantFileSystemStorage` silently stored their files
  in the shared `MEDIA_ROOT`
- `shell_tenant` now raises a clear error when neither `--tenant_id` nor
  `--disable` is given, or when the tenant doesn't exist

## [0.9.7] - (2026-07-27)
- `TenantAwareAbstract.save()` now sets the tenant only on create and
  preserves it on updates (#134)

## [0.9.6] - (2025-07-17)
- Fixed fields initialization in `UniqueTenantConstraint` (#127)

## [0.9.5] - (2025-07-11)
- Fixed `UniqueTenantConstraint` validation when the tenant field is in
  `exclude` (e.g. in model forms) (#126)
- Fixed the default tenant state not being initialized in new contexts (#126)

## [0.9.4] - (2025-07-10)
- Added `UniqueTenantConstraint` (#123)
- Removed `django-appconf` dependency (#124)
- Dropped support for Python 3.8 and Django < 4.2; added Django 5.2 (#123)

## [0.9.3] - (2025-07-04)
- Added support for Django 5.1 and Python 3.13 (#117)
- Dropped support for Django 3.2 and 4.1 (#117)
- Migrated packaging from Poetry to uv with a `src/` layout (#120)
- Added ruff and pre-commit (#121)

## [0.9.2] - (2024-03-25)
- Fixed `bulk_create` without a tenant context (#103)

## [0.9.1] - (2023-12-20)
- Added support for Django 5.0 and Python 3.12 (#97)

## [0.9.0] - (2023-12-19)
- Replaced `threading.local` with `ContextVar` to store the tenant state,
  making it async-safe (#93)

## [0.8.0] - (2023-07-11)
- Added `shell_tenant` management command (#86)
- Fixed `bulk_create` not forwarding extra arguments (#84)
- Added tests for Python 3.11 (#62)

## [0.7.1] - (2022-09-05)
- Added `TenantAwareAbstract` model and `EASY_TENANTS_TENANT_FIELD` setting,
  removing the hardcoded tenant field name (#53)
- Updated example project (#54)

## [0.7.0] - (2022-09-05)
- Removed `TenantAbstract` model and `EASY_TENANTS_MODEL` setting
- Dropped support for Django 2.2 (#41)

## [0.6.1] - (2021-12-16)
- Fixed project version

## [0.6.0] - (2021-12-16)
- Fixed tox tests

## [0.5.1] - (2021-12-16)
- Fixed tox tests
- Fixed RemovedInDjango41Warning default_app_config (#19)

## [0.5.0] - (2021-04-21)
- Removed `set_current_tenant`
- Added `tenant_context_disabled` to access objects from all tenants

## [0.4.0] - (2021-03-16)
- Remove middleware dependency in project (#16)

## [0.3.3] - (2020-07-28)
- Fix storage

## [0.3.2] - (2020-07-07)

- Include tenant_required=False in LogoutView
- Simplified TenantManager
- Fix database tests

## [0.3.1] - (2020-07-01)

- Removes middleware redirect to login responsibility

## [0.3.0] - (2020-07-01)

- Changed how to ignore the use of tenants in views (using decorators and mixin)
- Fix some methods to filter and assign a tenant to an object
- Updated example project
- Added CI tests for others databases
