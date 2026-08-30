---
name: ckan-actions-auth
description: Cheatsheet for writing modern CKAN Actions, Validation Schemas, and Authorization functions.
---

# CKAN Actions and Authorization

This skill provides comprehensive instructions on implementing, validating, and authorizing business logic actions in CKAN.

---

## Action Development Workflow

Actions must be exposed through the action API. Keep logic functions modular and separate from templates or views.

### File Layout
Organize action, auth, and schema scripts within a `logic/` submodule directory:
```
ckanext-myextension/
├── ckanext/
│   └── myextension/
│       ├── plugin.py
│       └── logic/
│           ├── __init__.py
│           ├── action.py          # Action API definitions
│           ├── auth.py            # Authorization checks
│           └── schema.py          # Validation schemas
```

---

## Writing Validation Schemas

CKAN uses validation schemas to format and validate input data dictionaries before actions process them.

* **Validator Args Decorator**: Apply `@tk.validator_args` to inject core validation functions directly as parameters into the schema definition.
* **Format**: Return a dictionary mapping field names to lists of validator callables.

```python title="logic/schema.py"
from __future__ import annotations

import ckan.plugins.toolkit as tk
from ckan import types

@tk.validator_args
def item_create(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    default: types.ValidatorFactory,
    boolean_validator: types.Validator,
) -> types.Schema:
    """Return schema for item creation."""
    return {
        "name": [not_empty, unicode_safe],
        "description": [unicode_safe],
        "is_active": [default(True), boolean_validator],
    }
```

---

## Implementing Actions

* **Naming**: Prefix action names with the extension name (e.g. `myextension_item_create`).
* **Validation Wrapper**: Decorate the action with `@tk.validate_action_data(schema)` to run validation before executing the action block.
* **Context Access**: Access the database session directly via `context["session"]`.

```python title="logic/action.py"
from typing import Any
import ckan.plugins.toolkit as tk
from ckan import types
from . import schema

@tk.validate_action_data(schema.item_create)
def myextension_item_create(context: types.Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Create a new item in myextension."""
    # 1. Always check authorization first
    tk.check_access("myextension_item_create", context, data_dict)

    # 2. Database transaction logic
    session = context["session"]
    # ... logic ...
    
    return {"id": "123", "name": data_dict["name"]}
```

---

## Authorization Logic and Decorators

Auth functions verify if a user has access rights to run the corresponding action.

### Naming Constraint
The name of the auth function must exactly match the name of the action it protects.

### Sysadmin Rule
Sysadmins bypass all custom authorization checks in CKAN. The auth function is never called for a sysadmin. For sysadmin-only actions, you can return a failure payload (`{"success": False}`) unconditionally:

```python title="logic/auth.py"
def myextension_admin_action(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    # Sysadmins bypass this block. All other users fail.
    return {"success": False, "msg": "Only sysadmins are authorized"}
```

### Anonymous Access Controls
* **Disallowing Anonymous Users**: Use `@tk.auth_disallow_anonymous_access` on functions that require a logged-in user. You can then safely return `True` unconditionally.
* **Allowing Anonymous Users**: Use `@tk.auth_allow_anonymous_access` if the action must be publicly accessible.

```python title="logic/auth.py"
import ckan.plugins.toolkit as tk
from ckan.types import Context

@tk.auth_disallow_anonymous_access
def myextension_item_create(context: Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    # Non-logged-in users are blocked before this runs
    return {"success": True}
```

---

## Action Execution Best Practices

### Calling Actions via `tk.get_action`
Never import action functions directly. Always retrieve and execute actions using the toolkit mapper:

```python
# CORRECT
result = tk.get_action("package_show")(context, {"id": package_id})
```

### Authorization Checks via `tk.check_access`
Always verify permissions using the toolkit wrapper. This automatically queries database models for user credentials:

```python
# CORRECT
tk.check_access("myextension_item_create", context, data_dict)
```

### Nested Actions and `tk.fresh_context`
When calling a nested action inside another action, you must wrap the parent context using `tk.fresh_context` to prevent context contamination (e.g. inheriting administrative privileges or cached errors):

```python
# CORRECT: Create isolated context for the sub-call
sub_context = tk.fresh_context(context)
new_item = tk.get_action("myextension_item_create")(sub_context, item_payload)
```

---

## Chained Actions and Auth Functions

Use chaining when your extension needs to intercept or modify core CKAN operations instead of overriding them completely.

* **Chained Actions**: Signature must be `(original_action, context, data_dict)`.
* **Chained Auth**: Signature must be `(next_auth, context, data_dict)`.

```python title="logic/action.py"
@tk.chained_action
def package_create(original_action, context, data_dict):
    # Pre-processing
    data_dict["checked"] = True
    # Delegate execution
    return original_action(context, data_dict)
```
