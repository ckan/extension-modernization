---
icon: lucide/file-code-2
---

# API Actions

CKAN's business logic is exposed through actions in the action API. CKAN
extensions organize actions, validation schemas, and authorization functions
inside a `logic/` package and use automatic decorators to expose them.

---

## Code Layout

Create a `logic/` submodule structure inside your extension:

```
ckanext-myextension/
├── ckanext/
│   └── myextension/
│       ├── plugin.py
│       └── logic/
│           ├── __init__.py
│           ├── action.py          # Action API functions
│           ├── auth.py            # Authorization functions
│           ├── schema.py          # Input validation schemas
│           └── validators.py      # Custom validators (if needed)
```

---

## Naming Patterns

- **Actions**: Must be lowercase, namespaced, and prefixed with the extension's
  name (e.g., `myextension_item_create`, `myextension_item_show`).
- **Auth Functions**: Must have the exact same name as the action they
  authorize (e.g., authorizing action `myextension_item_create` requires an
  auth function named `myextension_item_create`).
- **Schemas**: Usually match the suffix of the actions they validate
  (e.g. `item_create`, `item_show`). There is no strict requirement to prefix
  schema with the name of plugin, because schemas are not registered publicly
  and won't cause naming conflicts.

---

## Defining Schemas

CKAN extensions use the `@validator_args` decorator to define validation
schemas. This decorator inspects parameters and automatically injects standard
validation functions by name, removing the need to fetch them from
`tk.get_validator`.

```python title="logic/schema.py"
from __future__ import annotations

import ckan.plugins.toolkit as tk
from ckan import types

@tk.validator_args
def item_create(
    not_empty: types.Validator,          # (1)!
    unicode_safe: types.Validator,
    default: types.ValidatorFactory,
    boolean_validator: types.Validator,
) -> types.Schema:
    return {
        "name": [not_empty, unicode_safe],
        "description": [unicode_safe],
        "is_active": [default(True), boolean_validator],
    }
```

1. These parameters are automatically resolved and injected by the `@validator_args` decorator.

---

## Adding Actions

Actions should be typed, properly documented, authorize the caller, and validate input using schemas.

```python title="logic/action.py"
from __future__ import annotations

from typing import Any
import ckan.plugins.toolkit as tk
from ckan import types

from . import schema

@tk.validate_action_data(schema.item_create)  # (1)!
def myextension_item_create(context: types.Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Create a new item in myextension.

    :param name: Unique name of the item
    :type name: str
    :param description: Optional description of the item
    :type description: str, optional
    :param is_active: Whether the item is active. Defaults to True.
    :type is_active: bool, optional

    :returns: The created item details.
    :rtype: dict
    """
    # Check authorization. Usually it's the first line of the action
    tk.check_access("myextension_item_create", context, data_dict)

    # Business logic (interacting with models/DB). `data_dict` is validated and safe
    # to use here because of applied schema.
    session = context["session"]
    # ... create object ...

    # Return dictized representation
    return {"id": "123", "name": data_dict["name"]}
```

1. The `@validate_action_data` decorator runs the schema before entering the
   action function and raises `ValidationError` if check fails.

---

## Auth Functions

Auth functions verify if a user in the context is allowed to run the corresponding action.

```python title="logic/auth.py"
from __future__ import annotations

from typing import Any
import ckan.plugins.toolkit as tk
from ckan.types import Context

def myextension_item_create(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Authorize myextension_item_create.

    Only administrators are allowed to create items.
    """
    user = context.get("user")

    # check if user is admin
    is_admin = tk.check_access("sysadmin", context, {})
    if not is_admin:
        return {"success": False, "msg": "Only sysadmins can create items"}

    return {"success": True}
```

/// note

By default, sysadmins skip authorization checks in CKAN. Because of it, the
example above can be rewritten to a simpler form.

```py title="logic/auth.py"

def myextension_item_create(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    return {"success": False, "msg": "Only sysadmins can create items"}

```

For sysadmin this function won't even get called. Any other non-sysadmin user
will receive `False` from it and won't pass the authorization check.

///


---

## Auto-Registration

Simply decorate your plugin class with `@tk.blanket.actions` and
`@tk.blanket.auth_functions` in `plugin.py`. This scans your `logic/action.py`
and `logic/auth.py` files and registers them automatically.
