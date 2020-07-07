# Changelog

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
