# Changelog

## [0.5.1] - (2021-12-16)
- Fixed tox tests
- Fixed RemovedInDjango41Warning default_app_config (#19)

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
