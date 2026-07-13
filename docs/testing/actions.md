---
icon: lucide/cog
---

# Actions

Actions contain the core business logic of a CKAN extension. Tests should verify that actions perform database operations correctly, respect schema validations, and return the expected output structures.

---

## The `call_action` Helper

Use the `call_action` helper from `ckan.tests.helpers` to invoke actions directly. This encapsulates context setup and executes validation rules:

```python title="tests/logic/test_action.py"
from __future__ import annotations

import pytest
from ckan.tests import factories
from ckan.tests.helpers import call_action

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestMyAction:

    def test_item_create_success(self):
        """Verify successful item creation."""
        # 1. Prepare data payload
        data = {
            "name": "test-item",
            "title": "Test Item",
            "notes": "Some description text"
        }

        # 2. Invoke action
        result = call_action("myextension_item_create", **data)

        # 3. Assert outputs
        assert result["name"] == "test-item"
        assert "id" in result
```

---

## Testing Validation Errors

Actions rely on schemas to validate input payloads. Verify that actions raise validation exceptions when required inputs are missing or malformed:

```python
from ckan.plugins.toolkit import ValidationError

def test_item_create_missing_name(self):
    """Verify validation error when 'name' is missing."""
    # Payload lacks the mandatory 'name' key
    data = {
        "title": "Test Item Without Name",
    }

    # Verify ValidationError is raised
    with pytest.raises(ValidationError) as exc_info:
        call_action("myextension_item_create", **data)

    # Assert specific error message content
    assert "name" in exc_info.value.error_dict
    assert "Missing value" in exc_info.value.error_dict["name"]
```

---

## Context Parameters in Actions

By default, `call_action` executes with a default context containing a database session. To test actions under specific circumstances—such as mimicking a non-logged-in user or using a custom context—pass a `context` parameter directly:

```python
def test_item_create_anonymous_user(self):
    """Verify anonymous users cannot create items."""
    context = {
        "user": None,
        "auth_user_obj": None
    }
    data = {"name": "unauthorized-item"}

    # Action should fail authorization
    with pytest.raises(ValidationError):
        call_action("myextension_item_create", context=context, **data)
```
