# CKAN review checklist

CKAN-specific patterns to look for in the changed code. Each item is a
modernization suggestion unless it also causes a defect, such as a missing
authorization check. Match every suggestion to the project's declared CKAN
versions.

## Code quality and architecture

- **Plugin registrations**: manual `get_actions`, `get_auth_functions`,
  `get_validators`, or `get_helpers` in `plugin.py` → suggest `@tk.blanket`
  decorators (CKAN 2.10+). [Plugins](../../../../docs/development/defining-plugins.md)
- **Logic invocations**: imported action, auth, or helper functions called
  directly → suggest `tk.get_action(...)` and `tk.check_access(...)`.
  [Invoking actions](../../../../docs/development/adding-actions.md#invoking-actions-and-auth-checks)
- **Nested context**: a parent action's `context` passed directly to nested
  `get_action` calls → suggest `tk.fresh_context(context)` (CKAN 2.10+). It
  keeps the user and `ignore_auth`, so also check that a nested call does not
  inherit `ignore_auth=True` unintentionally.
  [Nested actions](../../../../docs/development/adding-actions.md#calling-actions-from-within-actions)
- **Database queries**: legacy `Session.query` / `model.Session.query` →
  suggest `sa.select()` with `session.scalar()` or `session.scalars()`, which
  also work with the SQLAlchemy 1.4 used by CKAN 2.11.
  [Querying models](../../../../docs/development/database-models.md#querying-models)
- **Dictization options**: `dictize` reading options from `context` → suggest
  keyword-only parameters (`*, include_details: bool = False`).
  [Model dictization](../../../../docs/development/database-models.md#model-dictization)
- **Helper queries**: dataset queries through SQLAlchemy inside template
  helpers → suggest `package_search` or `package_show`.
  [Helpers](../../../../docs/development/template-helpers.md#use-action-apis-instead-of-direct-db-queries)

## Security and authorization

- **Action access checks**: a custom action that does not call
  `tk.check_access` at the beginning of its body. Report a defect when the
  action reads protected data or changes state.
  [Actions](../../../../docs/development/adding-actions.md)
- **Auth access decorators**: an auth function without
  `@tk.auth_disallow_anonymous_access` or `@tk.auth_allow_anonymous_access` →
  suggest making anonymous access explicit (CKAN blocks anonymous users by
  default). [Auth shortcuts](../../../../docs/development/adding-actions.md#authorization-shortcuts)
- **Signal mutability**: a signal subscriber that modifies `data_dict`, raises
  validation errors, or returns responses → suggest a CKAN interface. Handler
  exceptions propagate to the caller of the action.
  [Signals](../../../../docs/development/signals.md)
- **Signal connection**: direct `signal.connect(...)` calls → suggest `p.ISignal`
  with `get_signal_subscriptions()` (CKAN 2.10+).
  [Subscribing](../../../../docs/development/signals.md#subscribing-to-signals)

## Testing

- **Test data setup**: creation actions such as `call_action("package_create")`
  used to prepare data → suggest registered factories such as
  `package_factory()`, which keep valid defaults in one place.
  [Test data](../../../../docs/testing/actions.md#initializing-data-for-actions)
- **Mocked internals**: tests that monkeypatch `get_action` or other logic
  internals to assert delegation → suggest black-box assertions on records,
  results, or exceptions.
  [Black-box tests](../../../../docs/testing/actions.md#black-box-action-testing-vs-monkeypatching)
- **Fixture declarations**: `clean_db` or `with_plugins` requested as test
  arguments → suggest `@pytest.mark.usefixtures("with_plugins", "clean_db")`
  at class or module level. [Fixtures](../../../../docs/testing/fixtures.md)
- **Test client logins**: authenticated view tests that pass
  `extra_environ={"REMOTE_USER": ...}` or edit cookies manually → suggest
  `app.set_session_user(user["name"])` on CKAN 2.12+, or an `Authorization`
  header with `api_token` on CKAN 2.11.
  [View authentication](../../../../docs/testing/views.md#authenticating-in-view-tests)
- **Playwright scope**: backend logic, action validation, or plain redirects
  tested with Playwright → suggest standard pytest tests.
  [E2E](../../../../docs/testing/e2e-playwright.md)
- **Missing E2E coverage**: complex interactive components (maps, charts,
  multi-step forms) with only backend tests → suggest Playwright tests.
  [E2E](../../../../docs/testing/e2e-playwright.md)

## Docker environment

- **Plugin variables**: an extension plugin missing from `CKAN__PLUGINS` in
  `.env` or Compose files. The official `ckan/ckan-base` and `ckan/ckan-dev`
  images write `ckan.ini` from `CKAN__PLUGINS`; `CKAN_PLUGINS` is not used.
  [Docker](../../../../docs/environment/docker-development.md#enabling-plugins-with-ckan__plugins)

## Excluded topics

- **Formatting**: do not comment on whitespace, indentation, or import order;
  linting tools handle them.
