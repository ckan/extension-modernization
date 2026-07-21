---
icon: lucide/check-check
---

# Validators

Validators inspect, format, convert, and sanitize input payload entries before
actions process them or persist records to the database.

---

## Validator Function Signatures

CKAN supports three validator function signatures depending on how much context
or raw data structure your validation logic requires.

### 1-Argument Signature (Value-Based)

Accepts only the field's current value. It returns the transformed value or raises `tk.Invalid` if validation fails.

/// admonition
    type: example

```python
import ckan.plugins.toolkit as tk

def lowercase_string(value: Any) -> str:
    """Ensure string is lowercase."""
    if not isinstance(value, str):
        raise tk.Invalid("Must be a string")
    return value.lower()
```

///

### 2-Argument Signature (Value and Context)

Accepts the field's current `value` as the first parameter and the execution
`context` dictionary as the second parameter. This is useful when validation
depends on contextual state (such as accessing the database `session` or
checking the current `user`).

/// admonition
    type: example

```python
from typing import Any
import ckan.plugins.toolkit as tk
from ckan import model
from ckan.types import Context

def valid_user_id(value: str, context: Context) -> str:
    """Verify that a user ID exists in the database."""
    session = context["session"]
    user = session.get(model.User, value)
    if not user:
        raise tk.Invalid("User does not exist")
    return value
```

///


### 4-Argument Signature

It receives `key`, `data`, `errors`, and `context`. Instead of returning a
value or raising exceptions, it mutates `data` or appends error messages
directly into `errors[key]`.

/// admonition
    type: example

```python
from typing import Any
import ckan.plugins.toolkit as tk
from ckan import types

def ensure_unique_slug(
    key: types.FlattenKey,
    data: types.FlattenDataDict,
    errors: types.FlattenErrorDict,
    context: types.Context,
):
    """Check slug uniqueness against DB."""
    value = data.get(key)
    if value and slug_exists(value, session=context["session"]):
        errors[key].append("Slug is already taken")
```


///

---

## Validator Factories

A validator factory is a higher-order function that accepts configuration
parameters and returns a configured validator function. Built-in functions like
`default(...)` are examples of validator factories.

### Creating a Custom Validator Factory
To create a custom factory, write a function that accepts options and returns a validator:

```python
from typing import Any, Callable
import ckan.plugins.toolkit as tk

def min_length(limit: int) -> Callable[..., Any]:
    """Validator factory ensuring a minimum string length."""
    def validator(value: str) -> str:
        if not isinstance(value, str) or len(value) < limit:
            raise tk.Invalid(f"Must be at least {limit} characters long")
        return value
    return validator
```

---

## Exceptions in Validators

Validators use specific exceptions to signal validation failures or control schema execution flow:

### `tk.Invalid`

Raised by 1-argument or 2-argument validators when a field fails
validation. CKAN catches `Invalid` and automatically appends the exception
message to the field's `errors` list.

```python
raise tk.Invalid("Invalid email address format")
```

### `tk.StopOnError`

Raised to immediately halt the execution of any remaining validators in the
chain for the current key. For example, if a field is missing or invalid,
`StopOnError` prevents subsequent validators from running unnecessary format
checks.

```python
def ignore_missing(key, data, errors, context):
    if not data.get(key):
        raise tk.StopOnError
```

### `tk.UnknownValidator`
Raised by CKAN's schema loader if a schema references a validator name string that has not been registered in the system.

---

## In-Place Validation with `tk.navl_validate`

You can run validation schemas dynamically against any python dictionary using `tk.navl_validate`. This is useful for ad-hoc validation outside of formal action workflows:

```python
import ckan.plugins.toolkit as tk
from ckan.types import Context

def validate_custom_payload(raw_dict: dict[str, Any], context: Context):
    # 1. Define an in-place validation schema
    schema = {
        "title": [tk.get_validator("not_empty")],
        "age": [tk.get_validator("ignore_missing"), tk.get_validator("int_validator")],
    }

    # 2. Run navl_validate
    converted_data, errors = tk.navl_validate(schema, raw_dict, context)

    # 3. Handle errors
    if errors:
        raise tk.ValidationError(errors)

    return converted_data
```

---

## Writing and Registering Validators

Place custom validators inside `logic/validators.py` and register them using `@tk.blanket.validators` in your extension's `plugin.py`.

### 1. Write Validators
```python title="logic/validators.py"

import ckan.plugins.toolkit as tk

def valid_hex_color(value: str) -> str:
    """Validate hex color codes."""
    if not value.startswith("#") or len(value) not in (4, 7):
        raise tk.Invalid("Must be a valid hex color code (e.g. #FF0000)")
    return value
```

### 2. Auto-Registration in Plugin
```python title="plugin.py"
import ckan.plugins as p
import ckan.plugins.toolkit as tk

@tk.blanket.validators  # Automatically registers logic/validators.py
class MyPlugin(p.SingletonPlugin):
    ...
```

### 3. Use in Schemas
```python title="logic/schema.py"
import ckan.plugins.toolkit as tk
from ckan import types

@tk.validator_args
def item_schema(
    not_empty: types.Validator,
    valid_hex_color: types.Validator, # Automatically injected by validator_args
) -> types.Schema:
    return {
        "color_code": [not_empty, valid_hex_color],
    }
```
