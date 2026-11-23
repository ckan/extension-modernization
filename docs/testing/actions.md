---
icon: lucide/cog
---

# Actions

Actions contain the core business logic of a CKAN extension. Tests should
verify that actions perform database operations correctly, respect schema
validations, and return the expected output structures.

---

## The `call_action` Helper

Use the `call_action` helper from `ckan.tests.helpers` to invoke actions
directly, skipping authentication check.

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

/// admonition
    type: note

If you are using schemas and applying them via `@tk.validate_action_data`, it's
recommended to test schema directly and focus only on things that are performed
by action itself when you are testing the action.

///

---

## Context Parameters in Actions

By default, `call_action` executes with a default context containing a database
session and `ignore_auth=True`, so authorization checks are skipped. To test
actions under specific circumstances, such as mimicking a non-logged-in user,
pass a `context` parameter as a second argument to `call_action`:

```python
from ckan.plugins.toolkit import NotAuthorized

def test_item_create_anonymous_user(self):
    """Verify anonymous users cannot create items."""
    context = {
        "user": None,
        "auth_user_obj": None,
        "ignore_auth": False,  # call_action skips auth checks by default
    }
    data = {"name": "unauthorized-item"}

    # Action should fail authorization
    with pytest.raises(NotAuthorized):
        call_action("myextension_item_create", context, **data)
```

/// admonition
    type: note

To test authentication, write separate set of tests inside
`test_auth.py`. Action tests must be focused on the actual action's goal, such
as data creation or retrieval, rather than on additional effects and checks that
can be tested separately (auth, validation, schemas).

///

---

## Initializing Data for Actions

When testing read-only actions (like `item_show` or search queries), you must
populate the database with mock records before calling the action.

### The Antipattern: Using Actions for Data Setup

A common antipattern is to call creation actions (e.g.,
`call_action("item_create")`) to initialize database records for a retrieval or
search test.

/// admonition | Do not do this
    type: warning

```python
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_item_show():
    # Every test that creates items like this must be updated
    # whenever the item_create schema changes.
    item = call_action("myextension_item_create", name="my-item")

    result = call_action("myextension_item_show", id=item["id"])
    assert result["name"] == "my-item"
```


///


### The Solution: Using Factories for Data Setup

Use **test factories** to populate database states. This centralizes your test
data: if your creation action logic changes, single fix of the factory will restore
all the tests. If you are using `*_create` actions directly, you may need to
review every invocation, adding/changing values according to the schema
changes.

```python
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_item_show_with_factory(item_factory):
    # The factory supplies valid defaults and calls the create action for you
    item = item_factory(name="my-item")

    result = call_action("myextension_item_show", id=item["id"])
    assert result["name"] == "my-item"
```

### Specialized Factories vs. Action Parameters

If your tests require various initial states (e.g., a draft item, an active
item, or an item with multiple reviews), avoid passing complex parameters to
creation actions. Instead, define **specialized factory classes** or use
factory overrides:

```python
# In conftest.py
@register(_name="draft_item")
class DraftItemFactory(ItemFactory):
    state = "draft"

@register(_name="active_item")
class ActiveItemFactory(ItemFactory):
    state = "active"
```

In your test, inject these specialized factories directly:

```python
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_list_active_items_only(active_item, draft_item):
    # 'active_item' and 'draft_item' are automatically created in the DB
    result = call_action("myextension_item_list_active")

    assert len(result) == 1
    assert result[0]["name"] == active_item["name"]
```

/// admonition
    type: note

Remember that you can create fixtures inside the test file directly instead of
`conftest.py`. In this way, specialized factories will exist only inside this
file and won't conflict with other factories or pollute factory namespace.

///



### Using Stubs for Creation Action Testing

If you are testing the creation action itself (e.g., `item_create`), you still
need to pass a payload. To avoid hardcoding dictionaries that can easily become
outdated as schemas evolve, use the factory's `.stub()` method:

```python
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_item_create_payload(item_factory):
    # Generates a valid dictionary representation of the item locally
    payload_data = vars(item_factory.stub(title="Custom Title"))

    # Pass the stubbed dictionary payload to the create action
    result = call_action("myextension_item_create", **payload_data)

    assert result["title"] == "Custom Title"
    assert "id" in result
```

---

## Black-Box Action Testing vs. Monkeypatching

Actions are the top-level API entry points for your extension's business
logic. Therefore, you should treat actions as **black boxes**: invoke them with
valid inputs and assert their public return results or external side-effects
(e.g. data created/purged in the database, emails sent).

Unless your action communicates with an external, unavailable third-party
service, **avoid monkeypatching action internals**.

Mocking internal action calls makes tests highly fragile and closely coupled to
implementation details. If the underlying code is refactored, the test will
break even if the behavior remains completely correct.

The following example shows the test that rely in internal implementation of
the action and can break every time the action is changed.

/// admonition | The Fragile Approach
    type: warning

```python
def test_delete_details(self, monkeypatch, sysadmin, package):
    stub = mock.Mock()
    context = {"user": sysadmin["name"]}

    monkeypatch.setattr(actions, "_internal_function", stub)
    helpers.call_action("delete_details", context, id=package["id"])

    stub.assert_called()
```


///


Instead of testing internal steps of the action, verify the actual
side-effects. Ensure that the item is permanently deleted from the database
by attempting to query or fetch it after the action runs:

/// admonition | Stable test
    type: example

```python
def test_delete_details(self, package_factory):
    item = package_factory(type="details") # (1)!

    helpers.call_action("delete_details", id=item["id"]) # (2)!

    with pytest.raises(toolkit.ObjectNotFound): # (3)!
        helpers.call_action("details_show", id=item["id"])
```

1. Initialize data using factories
2. Invoke the delete action (omitting redundant context parameters)
3. Assert side-effect: details record no longer exists in CKAN

///


/// admonition | Omit Redundant Context Parameters
    type: tip

In the correct example above, the `context` dictionary parameter is omitted
from `helpers.call_action`. By default, `call_action` runs with
`ignore_auth=True`, so permission checks are skipped. Passing a custom `context` object to
`call_action` is redundant and clutters the test setup unless you are
explicitly testing permission overrides or auth validation logic (which should
be isolated in `test_auth.py` files).

///
