---
icon: lucide/lock
---

# Auth Functions

Auth functions define authorization rules, determining which users can call
specific actions. Tests should verify permissions for different user roles:
sysadmins, organization members, and anonymous users.

---

## Testing via `call_auth`

The standard way to test authorization rules is to call the `call_auth`
helper. This mimics CKAN's internal authorization middleware:

```python title="tests/logic/test_auth.py"
import pytest
from ckan.tests.helpers import call_auth
from ckan.plugins.toolkit import NotAuthorized

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestMyAuthRules:

    def test_item_create_sysadmin_allowed(self, sysadmin):
        """Verify sysadmin users can create items."""
        # Verify access is granted (returns True or does not raise exception)
        assert call_auth("myextension_item_create", {"user": sysadmin["name"]})

    def test_item_create_anonymous_denied(self):
        """Verify anonymous users cannot create items."""
        with pytest.raises(NotAuthorized):
            call_auth("myextension_item_create", {"user": None})
```

---

## Testing Auth Functions Directly

You can test the auth functions directly by importing them. This may be faster
because it avoids routing through CKAN's registration layer, but generally it's
not recommended approach.

```python
from ckanext.myextension.logic.auth import myextension_item_create

def test_direct_auth_check(self, user):
    context = {"user": user["name"]}

    # Call function directly
    result = myextension_item_create(context, {})

    # Assert return structure
    assert not result["success"]
    assert "Must be a sysadmin" in result["msg"]
```

---

## Parametrized Authorization Checks

An extension often registers multiple actions and auth functions that share
identical permission rules (for instance, a set of administrative actions that
should only be accessible to sysadmins and blocked for anonymous users).

Instead of copying and pasting the same tests for each auth function, use
Pytest's `@pytest.mark.parametrize` decorator to run the check over all
corresponding action names in a loop.

### Code Example

```python title="tests/logic/test_auth.py"
import pytest
from ckan.tests.helpers import call_auth
from ckan.plugins.toolkit import NotAuthorized

# Define list of actions sharing the same access policy
ADMIN_ACTIONS = [
    "myextension_item_create",
    "myextension_item_update",
    "myextension_item_delete",
]

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestAdminAuthorizationRules:

    @pytest.mark.parametrize("action_name", ADMIN_ACTIONS)
    def test_admin_actions_sysadmin_allowed(self, action_name, sysadmin):
        """Verify sysadmin users can call all administrative actions."""
        assert call_auth(action_name, {"user": sysadmin["name"]})


    @pytest.mark.parametrize("action_name", ADMIN_ACTIONS)
    def test_admin_actions_anonymous_denied(self, action_name):
        """Verify anonymous users are denied access to all administrative actions."""
        with pytest.raises(NotAuthorized):
            call_auth(action_name, {"user": None})
```
