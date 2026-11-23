---
icon: lucide/settings
---

# Configuration Management

CKAN extensions declare and validate their configuration options rather than
reading untyped values directly from `ckan.ini`. This provides early validation
of configurations, default fallbacks, and typed access throughout the codebase.

---

## Config Declarations (`config_declaration.yaml`)

Configuration options are declared in a YAML file named
`config_declaration.yaml`. This file defines the keys,
types, defaults, and descriptions for all settings.

```yaml title="ckanext/myextension/config_declaration.yaml"
version: 1
groups:
  - annotation: myextension configuration
    options:

      - key: ckanext.myextension.limits.items
        editable: true # (1)!
        type: int # (2)!
        default: 10 # (3)!
        description: |
          Maximum number of items shown on the list page.

      - key: ckanext.myextension.features.enable_logging
        editable: true
        type: bool
        default: false # (4)!
        description: Enable verbose debug logging.

      - key: ckanext.myextension.api_key
        required: true # (5)!
        description: API Key for extension requests
```

1. This flag has no special effect in CKAN, but it's recommended to enable it
   for options that can be safely modified in runtime. Extensions, such as
   [ckanext-editable-config](https://github.com/ckan/ckanext-editable-config)
   can use it to build config-management interface.
2. `type` sets default validators and value for option. Currently CKAN supports
   3 types: `int`, `bool`, `list`. Corresponding default values are `0`,
   `false` and `[]`. If no type specified, value is treated as optional string
   and can be further transformed by applied validators.
3. Typed values have default value of matching type. Untyped values, with no
   `type` are set to `None` when missing.
4. This default value is not required, as CKAN will add it automatically for
   the `type: bool`. But being explicit never hurts, right?
5. CKAN won't start without required option and will report name of the item that caused the problem.

---

## Auto-Registering Declarations (Blanket)

If your configurations are static, you can use the `@tk.blanket.config_declarations` decorator on your plugin class. This automatically detects, parses, and registers `config_declaration.yaml` into CKAN's core registry.

```python title="plugin.py"
import ckan.plugins as p
import ckan.plugins.toolkit as tk

@tk.blanket.config_declarations  # (1)
class MyExtensionPlugin(p.SingletonPlugin):
    pass
```

1. Blanket automatically registers the static declarations in `config_declaration.yaml` during CKAN initialization.

---

## Manual `IConfigDeclaration` Implementation

While blanket auto-registration works for static configurations, you must manually implement the `IConfigDeclaration` interface when configurations need to be resolved **dynamically**.

When to implement manually:

* **Dynamic Config Keys**: Declaring configuration parameters dynamically (e.g., looping through configured storage backends and generating config options on-the-fly).
* **CKAN Version Checks**: Registering different settings or parameters depending on `tk.check_ckan_version`.
* **Custom Validators**: Clearing validation caches or registering custom schema validators before parsing config keys.

/// admonition
    type: example

```python title="plugin.py"
import os
from typing import Any
import yaml
import ckan.plugins as p
import ckan.plugins.toolkit as tk

from typing_extensions import override

class MyExtensionPlugin(p.IConfigDeclaration, p.SingletonPlugin):

    @override
    def declare_config_options(self, declaration: Any, key: Any):
        # 1. Handle CKAN version differences
        if tk.check_ckan_version("2.12"):
            declaration.declare_bool("ckanext.myextension.feature_2_12")
            return

        # 2. Programmatically load standard static declaration file
        here = os.path.dirname(__file__)
        with open(os.path.join(here, "config_declaration.yaml"), "rb") as src:
            declaration.load_dict(yaml.safe_load(src))

        # 3. Dynamically register config options based on active storage backends
        for storage_name in ["s3", "gcs", "fs"]:
            storage_key = key.from_string(f"ckanext.myextension.storage.{storage_name}")
            declaration.declare(storage_key.url, "").set_description(
                f"Endpoint URL for {storage_name} storage"
            )
```

///

---

## Modifying Configuration with `IConfigurer`

`IConfigurer` is an interface that allows plugins to modify the CKAN configuration object and register frontend asset locations before the environment is fully initialized.

Use `IConfigurer` when your extension needs to:

* **Register template directories**: Make your custom Jinja2 templates available to CKAN using `tk.add_template_directory`.
* **Register static/public assets**: Expose images, icons, and static files via `tk.add_public_directory`.
* **Register WebAssets libraries**: Add your bundle definitions from `webassets.yml` via `tk.add_resource`.
* **Inject or modify configuration settings**: Set default fallback values or alter `config` keys in-place before CKAN validates configuration options against declarations.

### Lifecycle Timing

`IConfigurer.update_config()` is invoked early during the startup process. At this stage:

1. The configuration declarations have been loaded.
2. Webassets and templates have **not** yet been compiled.
3. Database engines and SQLAlchemy models have **not** yet been initialized.

/// admonition | Update In-Place
    type: warning

You must modify the `config` object in-place. Do not reassign or return a new
dictionary. Any return value from `update_config()` is ignored by CKAN:

```python
# Correct: mutates in-place
config.setdefault("ckanext.myextension.custom_setting", "default_value")

# Wrong: does not work
config = {"my_setting": "val"}
```
///

/// admonition | Reverse Iteration Order
    type: note

`IConfigurer` uses reverse iteration order. This means plugins listed earlier
in the `ckan.plugins` configuration setting run **after** plugins listed later,
allowing primary plugins to override the configuration values set by downstream
plugins.

///

/// admonition
    type: example

```python title="ckanext/myextension/plugin.py"
from __future__ import annotations

from typing_extensions import override

import ckan.plugins as p
import ckan.plugins.toolkit as tk

class MyExtensionPlugin(p.IConfigurer, p.SingletonPlugin):

    @override
    def update_config(self, config: tk.CKANConfig) -> None:
        # Register template directories
        tk.add_template_directory(config, "templates")

        # Register public assets folder (static images, fonts)
        tk.add_public_directory(config, "public")

        # Register WebAssets folder containing webassets.yml
        tk.add_resource("assets", "myextension")

        # Set fallback settings in-place
        config.setdefault("ckanext.myextension.theme", "default")
```

///

---

## Post-Initialization Setup with `IConfigurable`

`IConfigurable` is an interface designed for initialization tasks that require
a fully initialized CKAN environment.

Use `IConfigurable` when your extension needs to:

* **Initialize external service clients**: Set up third-party SDK clients, S3 connections, Redis clients, or search engines that rely on validated configuration settings.
* **Initialize plugin singletons**: Populate in-memory caches, service registries, or background clients.
* **Perform startup sanity checks**: Verify external API credentials or connectivity once the database and full configuration are ready.

### Lifecycle Timing

`IConfigurable.configure()` is executed late in CKAN's initialization process:

1. All `IConfigurer.update_config` calls have completed.
2. Configuration options have been normalized and validated against `config_declaration.yaml`.
3. Template paths and WebAssets bundles have already been gathered.
4. The database engine and SQLAlchemy models are fully initialized and ready.

/// admonition | Multi-Process Execution
    type: tip

`IConfigurable.configure()` is executed not only when starting the main web
server, but also when invoking Click CLI commands and background worker
processes, since each process initializes its own CKAN environment. Ensure any
setup code in
`configure()` is safe to execute across separate processes.

///

/// admonition | What NOT to do in `IConfigurable`
    type: caution

* **Do not register templates or assets in `configure()`**: By the time
  `IConfigurable.configure()` is called, CKAN has already compiled template
  directories and asset bundles. Calls to `tk.add_template_directory` or
  `tk.add_resource` inside `configure()` will be ignored or produce errors.
* **Do not mutate core settings expecting subsystem changes**: Subsystems like
  the Jinja2 template loader and SQLAlchemy engine are already instantiated;
  modifying their config keys inside `configure()` will have no effect.

///

/// admonition
    type: example

```python title="ckanext/myextension/plugin.py"
from __future__ import annotations

from typing_extensions import override

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from .services import notification_service

class MyExtensionPlugin(p.IConfigurable, p.SingletonPlugin):

    @override
    def configure(self, config: tk.CKANConfig) -> None:
        # Read final, validated configuration
        api_url = config.get("ckanext.myextension.notification_api_url")
        api_token = config.get("ckanext.myextension.notification_api_token")

        # Initialize external service client
        if api_url and api_token:
            notification_service.init_client(
                url=api_url,
                token=api_token,
            )
```

///

---

## Comparison: `IConfigurer` vs `IConfigurable`

Understanding the distinction between `IConfigurer` and `IConfigurable` ensures that initialization code runs at the appropriate point in the CKAN startup lifecycle:

| Feature                         | `IConfigurer`                                                                                 | `IConfigurable`                                                                                     |
|:--------------------------------|:----------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------|
| **Method**                      | `update_config(config: tk.CKANConfig)`                                                        | `configure(config: tk.CKANConfig)`                                                                  |
| **Execution Point**             | Early startup (before database & asset compilation)                                           | Late startup (after database & models initialized)                                                  |
| **Primary Role**                | Configuration producer & asset registration                                                   | Configuration consumer & service initializer                                                        |
| **Modifies `config`?**          | **Yes** (modifications made in-place)                                                         | **No** (treat configuration as read-only)                                                           |
| **Typical Tasks**               | `add_template_directory`<br>`add_public_directory`<br>`add_resource`<br>Set fallback settings | Initialize third-party SDKs<br>Configure external service clients<br>Initialize caches & singletons |
| **Template/Asset Registration** | **Required location**                                                                         | **Prohibited** (too late; already resolved)                                                         |

/// admonition | Multiple Executions During Application Lifetime
    type: note

Methods from both interfaces can be called **multiple times** during the lifetime of an application.

For example, when application globals are updated through submitting the
configuration form from the admin interface (`/ckan-admin/config`), the
configuration changes according to the form submission and the environment is
refreshed. This reload cycle causes both `IConfigurer.update_config()` and
`IConfigurable.configure()` to be executed again.

Keep your implementations idempotent:

* Avoid repeatedly appending the same values or paths to configuration lists.
* Clean up or re-instantiate existing service connections safely without leaking resources.

///

---

## The Config Module Bridge (`config.py`)

To ensure type-safety and keep templates and logic modules decoupled from
`tk.config` dictionary keys, modern extensions implement a `config.py`
bridge. This file defines getter functions with explicit return type
annotations.

Additionally, it can further process config options, stripping leading slashes
from URL or doing similar tasks. Usually this kind of processing is delegated
to decorators, but sometimes it may be easier to postprocess options inside
`config.py`.

```python title="ckanext/myextension/config.py"
from __future__ import annotations

import ckan.plugins.toolkit as tk

# Define config key constants
LIMIT_ITEMS = "ckanext.myextension.limits.items"
ENABLE_LOGGING = "ckanext.myextension.features.enable_logging"

def limit_items() -> int:
    """Get the maximum number of items from configuration."""
    return tk.config[LIMIT_ITEMS]

def enable_logging() -> bool:
    """Check if verbose logging is enabled."""
    return tk.config[ENABLE_LOGGING]
```

/// note

With functions that return specific options, you don't need names of config
options stored as constants inside `config.py`. But it can come in handy when
you need to patch config during tests.

```py title="test_something.py"
import pytest
from ckanext.myextension import config

@pytest.mark.ckan_config(config.LIMIT_ITEMS, 42)
def test_something():
    assert config.limit_items() == 42
```

///

---

## Environment Variable Interpolation (`CKAN_` Prefix)

CKAN's configuration loader automatically inspects system environment variables
during startup. Any environment variable prefixed with `CKAN_`
(e.g. `CKAN_MYEXT_API_KEY`, `CKAN_S3_BUCKET_NAME`) is registered into the
config parser's defaults dictionary.

### Interpolation Syntax in `ckan.ini`

You can dynamically substitute environment variables inside `ckan.ini` using Python `ConfigParser` interpolation syntax: `%(CKAN_VARIABLE_NAME)s`.

```ini title="ckan.ini"
[app:main]
# Standard configuration options
ckan.site_url = http://localhost:5000

# Interpolating custom extension settings from environment variables
ckanext.myextension.api_key = %(CKAN_MYEXT_API_KEY)s
ckanext.myextension.s3_bucket = %(CKAN_S3_BUCKET_NAME)s
```

When CKAN parses `ckan.ini`, `%(CKAN_MYEXT_API_KEY)s` is resolved to the runtime value of `os.environ["CKAN_MYEXT_API_KEY"]`.

/// admonition | Docker & 12-Factor App Best Practices
    type: tip

Using `CKAN_` environment variable interpolation is the recommended pattern for
12-factor apps and Docker container deployments. It allows sensitive
credentials (such as API tokens, database passwords, or secret keys) to be
injected at container runtime without hardcoding secrets in version-controlled
configuration files.

Combine environment interpolation with default fallbacks in `config_declaration.yaml` to ensure your extension works out-of-the-box in local development environments.
///

### Automatic Core Environment Mappings

In addition to custom interpolation in `ckan.ini`, CKAN automatically maps
several core environment variables directly to config keys during startup
without requiring explicit `%(...)s` entries:

* `CKAN_SQLALCHEMY_URL` ➔ `sqlalchemy.url`
* `CKAN_DATASTORE_WRITE_URL` ➔ `ckan.datastore.write_url`
* `CKAN_DATASTORE_READ_URL` ➔ `ckan.datastore.read_url`
* `CKAN_REDIS_URL` ➔ `ckan.redis.url`
* `CKAN_SOLR_URL` ➔ `solr_url`
* `CKAN_SITE_URL` ➔ `ckan.site_url`
* `CKAN_STORAGE_PATH` ➔ `ckan.storage_path`
* `CKAN_MAX_UPLOAD_SIZE_MB` ➔ `ckan.max_resource_size`
* `CKAN_SMTP_SERVER` ➔ `smtp.server`
