# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project

`django-easy-tenants` is a lean Django library (a single app: `easy_tenants`) that implements multitenancy using the *shared database, shared schema* pattern: every tenant-isolated model carries a `ForeignKey` to a Tenant model defined by the project, and the library filters queries by the tenant active in the current context.

The package is published on PyPI; the code lives in `src/easy_tenants/`. The repository also contains an example Django project in `example/` (manual demo) and a Django project in `tests/` used by pytest.

## Project conventions

This library is distributed on PyPI and used by an international community, so **everything that ships from the repository is in English**.

- **Code, identifiers and comments** in `src/`, `tests/` and `example/`: English.
- **Commit messages**: English.
- **Issues, pull requests, descriptions, titles and changelog**: English.
- **Never commit without explicit authorization** from the maintainer. A request to create or change files is not a request to commit: leave the changes in the working tree and ask before committing. The same applies to pushing and opening pull requests.
- **Pull request descriptions must be simple**: a few short sentences or bullets on what changed and why. No headers, test plans, checklists or file-by-file walkthroughs; the diff speaks for itself.
- **Commit messages and pull requests must not mention AI assistants**: no `Co-Authored-By` trailer for an AI, no "Generated with ..." footer, no signature or reference to the assistant. Authorship belongs to the human maintainer.

## Commands

The project uses `uv` and `tox` (with `tox-uv`). The `Makefile` only has `make install`, which installs tox and the pre-commit hooks.

- **Run the whole matrix** (every Python × Django combination in `tox.ini`):
  ```bash
  tox
  ```
- **Run a single environment** (e.g. Python 3.12 + Django 5.2):
  ```bash
  tox -e py312-dj52
  ```
- **Run every environment for one Python version**:
  ```bash
  tox -f py312
  ```
- **Run a single test** — pass args after `--` so tox forwards them to pytest:
  ```bash
  tox -e py312-dj52 -- tests/test_model.py::test_name
  ```
- **Switch the test database** — by default tests use in-memory SQLite; set `DATABASE=postgres` to use the fixed Postgres URL in `tests/settings.py` (`postgres://postgres:postgres@localhost:5432/easy_tenants`):
  ```bash
  DATABASE=postgres tox -e py312-dj52
  ```
- **Lint / format** — ruff is the only linter/formatter (configured in `pyproject.toml`, `line-length = 80`). It runs via pre-commit:
  ```bash
  pre-commit run --all-files
  ```
- **Run the example project**:
  ```bash
  cd example && python manage.py migrate && python manage.py runserver
  ```

The example project needs the package installed (`pip install -e .`) and `example/requirements.txt` (django-debug-toolbar). Its modules are all imported through the `example` package; `manage.py` puts the repository root on `sys.path`.

Pytest configuration lives in `[tool.pytest.ini_options]` in `pyproject.toml`: the settings module is `tests.settings`, `--strict-config` and `--strict-markers` are required, and `xfail_strict = true`. Tox also promotes `ResourceWarning`, `DeprecationWarning` and `PendingDeprecationWarning` to errors — new code must not emit them.

## Architecture

The library is intentionally tiny. Its core behavior is concentrated in three pieces that work together, plus the request integration (middleware), storage, management command and system checks described below:

### 1. Tenant context — `src/easy_tenants/utils.py`
The "current tenant" is stored in a `contextvars.ContextVar` (`state`) shaped as `{"enabled": bool, "tenant": <Tenant>}`. Two context managers expose it (both also work as decorators, on sync and `async def` functions — the async case is wrapped explicitly because `ContextDecorator`'s wrapper is sync):
- `tenant_context(tenant)` — sets the active tenant inside the block (snapshots and restores the previous state on exit, so it nests correctly).
- `tenant_context_disabled()` — disables the tenant filter inside the block (used for cross-tenant operations, such as `shell_tenant --disable`).

`get_current_tenant()` raises `TenantError` if the filter is enabled but no tenant has been set. Because the state lives in a `ContextVar`, it is async-safe and isolated per task.

### 2. Filtering — `src/easy_tenants/models.py`
- `TenantManager.get_queryset()` injects `filter(<tenant_field>=CurrentTenant(...))` into every queryset. When `state["enabled"]` is `False`, no filter is applied.
- `CurrentTenant` is a `BaseExpression`, **not** an eager value. Its `as_sql()` is what calls `get_current_tenant()`, so the tenant is resolved when the SQL is executed, not when the queryset is built. This is what allows building a queryset outside `tenant_context` and executing it inside one.
- `TenantManager.bulk_create()` stamps `tenant_field_name` on each instance before delegating.
- `TenantAwareAbstract.save()` stamps `tenant_field_name` from the context only on create (`self._state.adding`); on updates the existing tenant is preserved. Application code never assigns the FK manually.
- `UniqueTenantConstraint` subclasses `UniqueConstraint` and automatically prepends the tenant field to `fields`. In `validate()` it also injects the current tenant into the instance and rewrites the violation message with only the user-visible fields (excluding the tenant) when the default message is in use.

### 3. Configurable tenant field/model
Two settings control everything:
- `EASY_TENANTS_TENANT_MODEL` — string in `app_label.ModelName` format pointing to the tenant model. Read at runtime (e.g. in the `shell_tenant` command).
- `EASY_TENANTS_TENANT_FIELD` — name of the FK on isolated models, default `"tenant"`. **Read only once at import time** in `models.py` (`tenant_field_name = getattr(settings, ...)`). The test suite uses `"store"` precisely to ensure this name isn't hardcoded anywhere.

### Storage and management
- `storage.py` — `TenantFileSystemStorage` partitions `MEDIA_ROOT`/`MEDIA_URL` by `<tenant.pk>`. Its properties (`base_location`, `location`, `base_url`) are intentionally **not cached** (the parent `FileSystemStorage` uses `cached_property`); recomputing on every access is what lets the same storage instance produce different paths for different tenants.
- `management/commands/shell_tenant.py` — wraps `shell_plus` (django-extensions) if available, otherwise the standard `shell`, inside `tenant_context(tenant)` or `tenant_context_disabled()`.
- `apps.py` — `ready()` imports `checks.py` (registering the system checks) and marks the built-in `django.contrib.auth` views (`LoginView`, `LogoutView`, password reset flow) with `tenant_required = False`.

### Request integration
- `middleware.py` — `TenantMiddleware` (sync and async capable) resolves `request.tenant` via `get_tenant()` → `get_tenant_id()` (abstract) and wraps the rest of the request in `get_context()` (`tenant_context(tenant)`, or a no-op when there is no tenant). In `process_view()` it calls `tenant_not_found()` (default: `PermissionDenied`) when there is no tenant and the view requires one. Subclasses: `SessionTenantMiddleware` (session key `tenant_id`) and `HeaderTenantMiddleware` (`X-Tenant-ID` header). `get_tenant()` doesn't check whether the user may access the tenant; that's left to integrators.
- `decorators.py` — `tenant_not_required` sets `tenant_required = False` on a view. The middleware reads this attribute from the view function or its `view_class`; every view requires a tenant by default.

### System checks — `src/easy_tenants/checks.py`
`easy_tenants.E001`–`E007` validate `EASY_TENANTS_TENANT_MODEL`, the tenant field of every tenant-aware model (one that inherits `TenantAwareAbstract` or uses `TenantManager`) and that `SessionMiddleware` comes before `SessionTenantMiddleware`. The README documents each ID; keep the table there in sync when adding checks.

## When making changes

- New behavior should follow the same pattern: keep the public API in `src/easy_tenants/__init__.py` minimal (today it only re-exports `get_current_tenant`, `tenant_context`, `tenant_context_disabled`), and resolve the active tenant *as late as possible* — like `CurrentTenant`, which defers until SQL execution.
- Always reference the tenant field via `tenant_field_name` (the module-level value read from settings); never hardcode `"tenant"`. The tests set `EASY_TENANTS_TENANT_FIELD = "store"` precisely to catch regressions here.
- When changing the test matrix, update both `tox.ini` (envlist + Django pin per env) and `.github/workflows/tests-ci.yml` (Python matrix). The classifiers in `pyproject.toml` must also stay in sync.
- Every PR that changes user-facing behavior (features, fixes, supported Python/Django versions) must add a line under `## [Unreleased]` in `CHANGELOG.md`, referencing the PR number.

## Releasing

Versions follow SemVer and are set statically in `pyproject.toml`; tags have no `v` prefix (e.g. `0.10.0`). While the project is on `0.x`, breaking changes (including dropping Python/Django versions) bump the minor version.

1. Open a "Release X.Y.Z" PR containing only:
   - the version bump, via `uv version --bump patch|minor|major` (updates both `pyproject.toml` and `uv.lock` — don't edit the version by hand);
   - in `CHANGELOG.md`, rename `## [Unreleased]` to `## [X.Y.Z] - (YYYY-MM-DD)` and add a new empty `## [Unreleased]` above it.
2. After merging, create a GitHub release on `main` with tag `X.Y.Z`, using the changelog section as release notes.
3. Publishing the release triggers `.github/workflows/publish.yml`, which checks that the tag matches the `pyproject.toml` version, builds with `uv build` and uploads to PyPI via Trusted Publishing (OIDC, `pypi` environment — no API token). Never upload to PyPI manually.
