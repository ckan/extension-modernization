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

### When to implement manually:
* **Dynamic Config Keys**: Declaring configuration parameters dynamically (e.g., looping through configured storage backends and generating config options on-the-fly).
* **CKAN Version Checks**: Registering different settings or parameters depending on `tk.check_ckan_version`.
* **Custom Validators**: Clearing validation caches or registering custom schema validators before parsing config keys.

### Implementation Example

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

CKAN's configuration loader automatically inspects system environment variables during startup. Any environment variable prefixed with `CKAN_` (e.g. `CKAN_MYEXT_API_KEY`, `CKAN_S3_BUCKET_NAME`) is registered into the config parser's defaults dictionary.

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

Using `CKAN_` environment variable interpolation is the recommended pattern for 12-factor apps and Docker container deployments. It allows sensitive credentials (such as API tokens, database passwords, or secret keys) to be injected at container runtime without hardcoding secrets in version-controlled configuration files.

Combine environment interpolation with default fallbacks in `config_declaration.yaml` to ensure your extension works out-of-the-box in local development environments.
///

### Automatic Core Environment Mappings

In addition to custom interpolation in `ckan.ini`, CKAN automatically maps several core environment variables directly to config keys during startup without requiring explicit `%(...)s` entries:

* `CKAN_SQLALCHEMY_URL` ➔ `sqlalchemy.url`
* `CKAN_DATASTORE_WRITE_URL` ➔ `ckan.datastore.write_url`
* `CKAN_DATASTORE_READ_URL` ➔ `ckan.datastore.read_url`
* `CKAN_REDIS_URL` ➔ `ckan.redis.url`
* `CKAN_SOLR_URL` ➔ `solr_url`
* `CKAN_SITE_URL` ➔ `ckan.site_url`
* `CKAN_STORAGE_PATH` ➔ `ckan.storage_path`
* `CKAN_MAX_UPLOAD_SIZE_MB` ➔ `ckan.max_resource_size`
* `CKAN_SMTP_SERVER` ➔ `smtp.server`
