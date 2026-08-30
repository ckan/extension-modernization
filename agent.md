# CKAN Extension Development Guidelines (AI Agent Reference)

This document defines the core standards, coding patterns, testing best
practices, and Docker development workflows for building and maintaining modern
CKAN extensions. AI agents and developers working on CKAN extension codebases
must adhere to these guidelines to ensure code quality, security, and
compatibility.

---

## Reference Documentation
For detailed explanations, configuration parameters, and architectural patterns, refer to the online documentation:
* **Base URL**: [https://extension-modernization.readthedocs.io/en/latest/](https://extension-modernization.readthedocs.io/en/latest/)
* **Development Guides**: `/development/adding-actions`, `/development/database-models`, `/development/validators`
* **Testing Guides**: `/testing/fixtures`, `/testing/actions`, `/testing/views`
* **Docker Environment**: `/environment/docker-development`

---

## Code Registration via Blanket Discovery

Modern CKAN extensions avoid manually writing registration boilerplate inside
`plugin.py`. Instead, they use the `blanket` registration module to
automatically discover and load logical modules.

### Registration Decorators
Apply decorators to the main plugin class (inheriting from `SingletonPlugin`) in `plugin.py`:

```python title="plugin.py"
from typing import Any
from typing_extensions import override

import ckan.plugins as p
import ckan.plugins.toolkit as tk

@tk.blanket.actions            # Automatically registers logic/action.py
@tk.blanket.auth_functions     # Automatically registers logic/auth.py
@tk.blanket.validators         # Automatically registers logic/validators.py
@tk.blanket.helpers            # Automatically registers helpers.py
@tk.blanket.blueprints         # Automatically registers views.py (Blueprints)
class MyExtensionPlugin(p.IConfigurer, p.SingletonPlugin):
    @override
    def update_config(self, config: Any):
        tk.add_template_directory(config, 'templates')
        # Register public assets folder (for static files like images)
        tk.add_public_directory(config, 'public')
        # Register WebAssets folder (containing webassets.yml bundles)
        tk.add_resource('assets', 'myextension')
```

---

## Action and Auth Patterns

Actions implement the business logic of CKAN, and authorization functions control access permissions.

### Writing Actions
* **Naming**: Prefix action names with the extension name (e.g., `myextension_item_create`).
* **Validation**: Decorate actions with `@tk.validate_action_data(schema_func)`
  to run validation schemas before executing function logic.
* **Context**: Always call `tk.check_access` inside actions to handle permissions.

```python title="logic/action.py"
from typing import Any
import ckan.plugins.toolkit as tk
from ckan import types
from . import schema

@tk.validate_action_data(schema.item_create)
def myextension_item_create(context: types.Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Create a new item."""
    tk.check_access("myextension_item_create", context, data_dict)

    session = context["session"]
    # ... business logic ...
    return {"id": "123", "name": data_dict["name"]}
```

### Writing Authorization Functions
* **Naming**: Must match the exact name of the action they protect.
* **Sysadmin Access**: Sysadmins automatically bypass custom authorization
  checks in CKAN. The auth function is never called for a sysadmin. For
  sysadmin-only actions, you can return a failure payload (`{"success":
  False}`) unconditionally since the function is bypassed for sysadmins anyway.
* **Anonymous Checks**:
  * Use `@tk.auth_disallow_anonymous_access` to block non-logged-in users. The function can then unconditionally return `True`.
  * Use `@tk.auth_allow_anonymous_access` if the action must be publicly accessible.

```python title="logic/auth.py"
import ckan.plugins.toolkit as tk
from ckan.types import Context

@tk.auth_disallow_anonymous_access
def myextension_item_create(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    # Under-the-hood checks ensure only logged-in users reach this code block
    return {"success": True}
```

### Invoking Actions and Auth
* **Do not import functions directly**: Never call `myextension_item_create(context, data)` directly in code.
* **Use get_action**: Always retrieve and call actions via
  `tk.get_action("action_name")(context, data)`. This dynamically enriches the
  `context` dictionary with standard variables (like `user`, `session`)
  preventing dictionary key errors.
* **Use check_access**: Always verify access via `tk.check_access("auth_name",
  context, data)`. This automatically queries the DB for `context["user"]` and
  injects `context["auth_user_obj"]` for authorization checks.
* **Avoid Context Contamination**: When calling nested actions from within
  another action, always pass an isolated context using
  `tk.fresh_context(context)` to prevent authorization leaks (e.g. inheriting
  `ignore_auth=True` parameters in sub-calls).

```python
# Calling a nested action safely
child_context = tk.fresh_context(context)
new_dataset = tk.get_action("package_create")(child_context, dataset_payload)
```

### Chained Actions, Auth, and Helpers

If your extension needs to intercept or modify core CKAN action, authorization,
or template helper flows (rather than replacing them), use the
`@tk.chained_action`, `@tk.chained_auth_function`, and `@tk.chained_helper`
decorators:

```python
@tk.chained_action
def package_create(original_action, context, data_dict):
    # Perform pre-checks
    data_dict["custom_flag"] = True
    # Delegate to next handler in the chain
    return original_action(context, data_dict)
```

---

## Custom Validators

Validators clean, transform, and evaluate data before actions process it. CKAN
uses the Nested Attribute Validation Language (NAVL) engine.

### Validator Signatures
1. **1-Argument Signature**: `def valid_fn(value: Any) -> Any:` (Evaluates a
   field value, raises `tk.Invalid`, and returns the cleaned value).
2. **2-Argument Signature**: `def valid_fn(value: Any, context: Context) ->
   Any:` (Accesses context variables like database sessions).
3. **4-Argument Signature**: `def valid_fn(key, data, errors, context):`
   (Modifies `data` or appends error messages into `errors[key]` in-place).

### Validator Exceptions
* `tk.Invalid("Error message")`: Standard validation failure exception.
* `tk.StopOnError`: Immediately halts any subsequent validators in the schema
  chain for the current key.


### In-Place Schema Validation (`tk.navl_validate`)
Execute ad-hoc validation on dictionary payloads outside actions:

```python
converted_data, errors = tk.navl_validate(schema, raw_dict, context)
if errors:
    raise tk.ValidationError(errors)
```

---

## Database Models and Migrations

Extensions declare database tables using SQLAlchemy style definitions
compatible with modern type checkers (like Pyright).

### Model Structure
```python title="model/item.py"
from typing import ClassVar
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from ckan import model
from ckan.lib.dictization import table_dictize


@model.registry.mapped_as_dataclass
class MyExtensionItem:
    __tablename__: ClassVar[str] = "myextension_item"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]

    def dictize(self, *, include_details: bool = False) -> dict[str, Any]:
        """Convert SQLAlchemy model to a plain dictionary."""
        result = table_dictize(self, {})
        if include_details:
             result["details"] = "..."
        return result
```

* **Table Dictization**: Implement a `dictize` method returning
  JSON-serializable dictionaries. Use `table_dictize` for default mapping.
* **Keyword-Only Parameters**: Configuration options for serialization detail
  must be passed as keyword-only parameters (e.g. `*, include_details: bool =
  False`) instead of polluting the `context` dictionary.
* **SQLAlchemy v2 Queries**: Avoid legacy `Session.query` calls. Use modern `select()` and `session.scalar()` syntaxes:
  ```python
  stmt = sa.select(MyExtensionItem).where(MyExtensionItem.title == "Example")
  item = session.scalar(stmt)
  ```

### Database Migrations
* **Generate Migrations**: Create new migrations using:
  ```bash
  ckan generate migration -p PLUGIN_NAME -m "Migration message"
  ```
* **Alembic Isolation**: Extensions must configure version tables in `env.py` to prevent conflicts with core CKAN tables:
  ```python
  context.configure(..., version_table="myextension_alembic_version")
  ```

---

## Signals

Signals implement the publisher-subscriber pattern. They notify observers of core events without modifying execution logic.

* **Observer-Only Constraint**: Signals are read-only observers. They **must
  not** modify data dictionary values, abort execution pipelines, or return
  HTTP responses. If execution logic must be altered, implement a CKAN
  Interface instead.
* **Signal Subscription via `ISignal`**: Plugins must subscribe to signals by
  implementing the `ckan.plugins.interfaces.ISignal` interface and returning a
  subscription dictionary mapping signal objects to handler functions:

  ```python
  from ckan import types
  import ckan.plugins as p
  import ckan.plugins.toolkit as tk
  from typing import Any
  from typing_extensions import override

  class MyPlugin(p.ISignal, p.SingletonPlugin):

      @override
      def get_signal_subscriptions(self) -> types.SignalMapping:
          return {
              # Map signal key to handler callbacks
              tk.signals.action_succeeded: [self.my_success_handler],
          }

      def my_success_handler(self, sender: Any, **kwargs: Any) -> None:
          # Check the event sender name (e.g. 'package_create')
          if sender == "package_create":
              # Perform side-effect operations
              pass
  ```

---

## Template Helpers

Template helpers format variables or query catalogs directly inside Jinja2 view
templates via the `h` global namespace.

* **Prefixing**: Always namespace your helpers (e.g. `myextension_format_date` instead of `format_date`).
* **API Access Only**: Avoid executing direct SQL database queries
  (`Session.query`) inside helpers unless it's done for performance. Prefer
  query datasets via Solr actions (`package_search` / `package_show`).

---

## Frontend Customization

Extensions customize CKAN's look and feel by overriding templates, assets, stylesheets, and Javascript scripts.

### Template Overrides
Create a matching template filename in your extension's `templates/` directory to override it. Extend base templates using `{% ckan_extends %}` to preserve core structures:

```html title="templates/header.html"
{% ckan_extends %}

{% block header_logo %}
  <div class="logo">
    <a href="{{ h.url_for('home.index') }}">
      <img src="{{ h.url_for_static('/images/custom-logo.png') }}" alt="Logo" />
    </a>
  </div>
{% endblock %}
```

### CSS and SASS Assets (WebAssets)
CKAN compiles, minifies, and serves CSS/JS files using WebAssets bundles. All frontend stylesheet and script files must be defined in WebAssets bundles.

1. **Define Bundles in `webassets.yml`**: Create a `webassets.yml` file placed at the root of your `assets/` directory:
   ```yaml title="assets/webassets.yml"
   myextension_theme_css:
     filter: cssmin
     output: myextension/%(version)s-theme.css
     contents:
       - css/theme.css
   ```
2. **Inject Bundle in Templates**: Import the bundle in Jinja2 templates using the `{% asset %}` macro in the format `'resource_name/bundle_name'`:
   ```html
   {% block styles %}
     {{ super() }}
     {% asset 'myextension/myextension_theme_css' %}
   {% endblock %}
   ```

### Javascript Modules
Declare script files in your `public/` directory using the `ckan.module` wrapper, and bind them to HTML elements using the `data-module` attribute:

```javascript title="public/javascript/custom-module.js"
ckan.module('custom-counter', function (jQuery, _) {
  return {
    initialize: function () {
      console.log('Module initialized on element:', this.el);
    }
  };
});
```

```html
<div data-module="custom-counter">Loading counter...</div>
```

---

## Testing Standards and Pytest Fixtures

The test suite runs on Pytest and relies heavily on fixtures and factories for test isolation.

### Recommended Test Structure
```python title="tests/test_actions.py"
import pytest
from ckan.tests import factories
from ckan.tests.helpers import call_action

# Prefer usefixtures at the class/function level rather than injecting clean_db in parameters
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestActions:

    def test_show_action(self, item_factory):
        # 1. Initialize data using factories (Black-Box approach)
        item = item_factory()

        # 2. Call action (Omit redundant context parameters)
        result = call_action("myextension_item_show", id=item["id"])

        # 3. Assert side-effects/results
        assert result["name"] == item["name"]
```

### Critical Pytest Fixtures
* `ckan_config`: Accesses and patches configuration parameters safely for the duration of a test via `@pytest.mark.ckan_config`.
* `with_plugins`: Loads and unloads plugins specified in config options before and after tests.
* `app`: Flask test client instance for testing blueprints and views.
* `cli` / `with_extended_cli`: Click command runners. Apply `with_extended_cli` to register dynamic commands from plugins.
* `clean_db` / `clean_index` / `clean_redis`: Wipes database tables, Solr indexes, and Redis keys before running a test.

### Factoryboy Methods
Registered factories (e.g., `user_factory`, `package_factory`) expose three essential helper methods:
1. **Instance**: Call the factory directly to write the record to the DB and return a dictionary (`package_factory()`).
2. **`.model()`**: Writes to the DB but returns the SQLAlchemy database object instead of a dictionary (`package_factory.model()`).
3. **`.stub()`**: Generates valid mock attributes locally **without** writing to the database or running action validations (`package_factory.stub()`).
4. **`.create_batch(size)`**: Instantiates multiple records sequentially (`package_factory.create_batch(10)`).

### E2E Testing with Playwright
For a subset of tests that verify complex frontend user interactions (such as interactive map bounding boxes, charting widgets, dynamic form state changes, or multi-step wizard processes), use **Playwright**.

* **Rule**: Do not use Playwright to test backend API logic, action parameter validation, or standard page redirects. These must be tested using fast, standard backend tests (`call_action` or `app`).
* **Fixture Configuration**: Add base URL parameters to `browser_context_args` in `conftest.py` mapping to `ckan.site_url`.
* **Shared Authentication**: Authenticate using the `login` helper which appends an API Authorization header to the page context instead of performing slow web logins.

```python title="tests/e2e/test_ui.py"
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestInteractiveUI:

    def test_bounding_box_selection(self, page: Page, login):
        # 1. Log in via API header
        login("sysadmin")

        # 2. Open spatial search form
        page.goto("/dataset/new")

        # 3. Draw bounding box on leaflet map
        map_canvas = page.locator(".leaflet-container")
        expect(map_canvas).to_be_visible()
        # Simulate interactions...
```

---

## Docker Development

Local environments run on Docker Compose and configure settings via env files.

### Extension Setup Workflow
1. Clone your extension into the `src/` directory of your local `ckan-docker` workspace.
2. Compile and link the extension to the container's environment:
   ```bash
   bin/install_src
   ```
3. Restart the container process:
   ```bash
   bin/restart
   ```

### Configurations Mapping (.env File)
Map `ckan.ini` keys to `.env` using uppercase syntax, double underscores (`__`), and standard `KEY=VALUE` assignments:
* `CKAN___SCHEMING__DATASET_SCHEMAS=ckanext.scheming:dataset.json`

### `CKAN_PLUGINS` vs. `CKAN__PLUGINS`
To avoid startup issues where custom plugins are not initialized, define both variables in your `.env` file:
* **`CKAN_PLUGINS`**: Read by `prerun.py` setup script to write database structures and initialize migrations.
* **`CKAN__PLUGINS`**: Read by `ckanext-envvars` at runtime to bind plugins inside Python.

---

## Common Anti-Patterns and Refactoring Fixes

Avoid these common development mistakes inside CKAN extension codebases.

### 1. The Action-Setup Antipattern
* **Bad**: Calling a creation action inside a test function to set up database state for checking a search or show action.
  ```python
  # BAD
  dataset = call_action("package_create", name="my-dataset")
  result = call_action("package_show", id=dataset["id"])
  ```
* **Good**: Utilize a test factory to write directly to the DB, ensuring that failures in `package_create` do not cause unrelated read tests to fail.
  ```python
  # GOOD
  dataset = dataset_factory(name="my-dataset")
  result = call_action("package_show", id=dataset["id"])
  ```

### 2. Direct Python Function Invocations
* **Bad**: Importing and calling action/auth/helper Python functions directly.
  ```python
  # BAD
  from ckanext.myextension.logic.action import myextension_item_create
  result = myextension_item_create(context, data)
  ```
* **Good**: Always use the toolkit registries to execute actions, verifying permissions and filling standard context variables automatically.
  ```python
  # GOOD
  result = tk.get_action("myextension_item_create")(context, data)
  ```

### 3. Database Queries in Template Helpers
* **Bad**: Performing raw SQL queries (`Session.query(model.Package)`) inside a helper function.
  ```python
  # BAD
  def my_helper():
      return model.Session.query(model.Package).all()
  ```
* **Good**: Always query catalogs via Solr search actions (`package_search` / `package_show`) to preserve search indexing caches and avoid database schema dependencies.
  ```python
  # GOOD
  def my_helper():
      return tk.get_action("package_search")({}, {"q": "*:*"})["results"]
  ```

### 4. Monkeypatching Action Internals
* **Bad**: Overriding `get_action` or mocking internal function calls during action tests to verify delegating behavior.
  ```python
  # BAD
  monkeypatch.setattr(toolkit, "get_action", mock_get_action)
  call_action("ckanext_showcase_delete", id=showcase_id)
  ```
* **Good**: Treat actions as black boxes, verifying the database state or external side-effects (e.g. asserting that querying the deleted object raises a `NotFound` exception).
  ```python
  # GOOD
  call_action("ckanext_showcase_delete", id=showcase_id)
  with pytest.raises(toolkit.ObjectNotFound):
      call_action("package_show", id=showcase_id)
  ```

### 5. Passing Polluted Contexts to Serialization
* **Bad**: Passing the raw `context` dictionary containing database sessions and transaction variables into models' dictization methods.
  ```python
  # BAD
  def dictize(self, context):
      return table_dictize(self, context)
  ```
* **Good**: Keep serialization structures isolated. Declare configurations as keyword-only parameters to ensure clean, type-checked parameter contracts.
  ```python
  # GOOD
  def dictize(self, *, include_details: bool = False):
      result = table_dictize(self, {})
      ...
  ```
