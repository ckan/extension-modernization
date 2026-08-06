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

/// admonition
    type: example

```python title="logic/auth.py"
from __future__ import annotations

from typing import Any
import ckan.plugins.toolkit as tk
from ckan.types import Context

def myextension_item_create(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Authorize myextension_item_create.

    Only administrators are allowed to create items.
    """
    # check if user is admin
    is_admin = tk.check_access("sysadmin", context, {})
    if not is_admin:
        return {"success": False, "msg": "Only sysadmins can create items"}

    return {"success": True}
```

///


### Authorization Shortcuts

By default, sysadmin users bypass all custom authorization checks in CKAN. The
auth function is never called for a sysadmin user. Because of this, if an
action requires sysadmin-only access, the auth function can simply return a
failure payload:

/// admonition | Sysadmin check
    type: example

```python
def myextension_admin_action(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    # Sysadmins bypass this and succeed automatically.
    # Non-sysadmin users will execute this and get blocked.
    return {"success": False, "msg": "Only sysadmins are authorized"}
```

///


To verify that a user is logged in (i.e. not anonymous), decorate the function
with `#!python @tk.auth_disallow_anonymous_access`. If this decorator is
present, you can safely return `#!python {"success": True}`
unconditionally - CKAN will automatically intercept and reject any anonymous
requests before running your code:

/// admonition | Authentication check
    type: example

```python
@tk.auth_disallow_anonymous_access
def myextension_user_profile_edit(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    # Safe to return True unconditionally; CKAN guarantees the user is logged in
    return {"success": True}
```

///


Conversely, if an auth function must be accessible by non-logged-in users, you
must explicitly decorate it with `#!python @tk.auth_allow_anonymous_access`. If this
decorator is missing, CKAN defaults to blocking anonymous requests before
invoking the function:

/// admonition | Anonymous access
    type: example

```python
@tk.auth_allow_anonymous_access
def myextension_public_items_view(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    # Explicitly allowed for anonymous users
    return {"success": True}
```

///

----

## Invoking Actions and Auth Checks

When calling actions or checking permissions within your extension, avoid
importing and directly calling the Python functions. Always use `get_action`
and `check_access`.

### Invoking Actions via `get_action`

Never import action functions directly to execute them in code. Always retrieve
and execute them via `get_action`.

/// admonition
    type: example

```python
import ckan.plugins.toolkit as tk

context = {"user": "johndoe"}
package_dict = tk.get_action("package_show")(context, {"id": package_id})
```

///

#### Automatic Context Population by `get_action`

When you invoke an action through `get_action`, CKAN enriches the `context`
dictionary by populating missing standard entries (such as `user` and
`session`). Because `get_action` guarantees these keys are present in the
context dictionary, your actions can safely access `context["session"]` or
`context["user"]` directly without needing defensive `context.get(...)`
fallbacks.

---

### Authorization Checks via `check_access`

Similarly, perform authorization checks by calling `check_access` rather than
calling auth functions directly:


```python
tk.check_access("myextension_item_create", context, data_dict)
```

#### User Model Injection (`auth_user_obj`)

When `check_access` is executed, it inspects the `context["user"]` string (the
username) and automatically populates `context["auth_user_obj"]` with the
corresponding `ckan.model.User` database object.

This enables custom auth functions or downstream actions to conveniently
inspect user attributes (e.g. `user_obj.email`, `user_obj.sysadmin`) directly
via `context["auth_user_obj"]` without making redundant database queries.

---

## Calling Actions from Within Actions

When implementing specialized wrapper actions or grouping complex, multi-step
logic into a single action, you will often need to invoke nested actions from
within your parent action code.

### The Security Hazard of Context Contamination

The `context` dictionary of the parent action carries active state variables,
authorization caches, and permission modifiers (like `ignore_auth=True` or
administrative user overrides).

If you pass the parent action's `context` directly to a nested `get_action`
call, the child action will inherit all of these parameters. This creates
severe authorization leaks (e.g., bypassing permission checks on nested
operations) and cache contamination.

To prevent context leaking, always wrap the parent context using
`tk.fresh_context(context)` before passing it to nested action calls.

`fresh_context` returns a clean, isolated copy of the context dictionary that
retains essential items (like `user` and `session`) but strips out transient
authorization states, user overrides, and local cached data:

```python
from typing import Any
import ckan.plugins.toolkit as tk
from ckan import types

def myextension_item_batch_create(context: types.Context, data_dict: dict[str, Any]) -> list[dict[str, Any]]:
    tk.check_access("myextension_item_batch_create", context, data_dict) # (1)!

    results = []
    for item_data in data_dict["items"]:
        child_context = tk.fresh_context(context) # (2)!


        new_item = tk.get_action("myextension_item_create")(  # (3)!
            child_context, item_data
        )
        results.append(new_item)

    return results
```

1. Authorize the parent batch action
2. Generate a clean context copy for the nested child action call to ensure authorization checks run independently in the sub-call
3. Invoke the child action using the fresh context

---

## Chained Actions

Chained actions allow extensions to intercept, extend, or modify the behavior
of existing core CKAN actions or actions registered by other extensions,
instead of completely replacing them. This enables multiple extensions to hook
into the same action execution sequence.

To define a chained action, use the `@tk.chained_action` decorator. The first
parameter of a chained action function is always the `next_action` (which
refers to the next function in the chain or the core CKAN action).

/// admonition
    type: example

```python title="logic/action.py"
from typing import Any
import ckan.plugins.toolkit as tk
from ckan import types

@tk.chained_action
def package_create(next_action: Any, context: types.Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Intercept package creation to add custom validation or modify payload."""
    # 1. Custom logic before the core action runs
    if "custom_field" not in data_dict:
        data_dict["custom_field"] = "default_value"

    # 2. Call the next action in the chain (or the core action itself)
    result = next_action(context, data_dict)

    # 3. Custom logic after execution (e.g. logging, trigger external sync)
    return result
```

///


/// admonition | Chained Actions vs. Signals for Side-Effects
    type: tip

If you are hooking into an action not to alter its input parameters or output
structure, but purely to perform a side-effect (such as sending an email,
logging, or invalidating external caches on success), **do not use chained
actions**.

Instead, subscribe to CKAN's built-in **`action_succeeded` signal**. This keeps
your code loosely coupled, prevents execution overhead, and avoids polluting
the action execution pipeline. Refer to the [Signals](signals.md) guide for
details on subscribing to event signals.

///

---

## Chained Auth Functions

Similarly, authorization checks can be chained using the
`@tk.chained_auth_function` decorator. This is useful when you want to append
additional permission checks to a core action's authorization rules without
discarding the existing checks.

The first parameter of a chained auth function is always `next_auth` (which
refers to the subsequent auth check in the chain).

/// admonition
    type: example

```python title="logic/auth.py"
from typing import Any
import ckan.plugins.toolkit as tk
from ckan.types import Context

@tk.chained_auth_function
def package_create(next_auth: Any, context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Add extra constraints to package creation authorization."""
    # 1. Perform custom check first
    user = context.get("user")
    if not user:
         return {"success": False, "msg": "Must be logged in to create packages"}

    # 2. Delegate to the remaining auth checks in the chain
    return next_auth(context, data_dict)
```

///



/// admonition | Decorator Interferences
    type: tip


Be careful when combining `@tk.chained_auth_function` with other auth
decorators (like `@tk.auth_allow_anonymous_access`). Ensure they are stacked
correctly so that CKAN's internal security attributes are not stripped or
bypassed by decorator wrapping orders.

///



---

## Auto-Registration

Simply decorate your plugin class with `@blanket.actions` and
`@blanket.auth_functions` in `plugin.py`. This scans your `logic/action.py`
and `logic/auth.py` files and registers them automatically.
