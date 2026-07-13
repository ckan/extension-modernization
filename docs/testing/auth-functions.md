---
icon: lucide/lock
---

# Auth Functions

Auth functions define authorization rules, determining which users can call specific actions. Tests should verify permissions for different user roles: sysadmins, organization members, and anonymous users.

---

## Testing via `check_access`

The standard way to test authorization rules is to call the `check_access` helper. This mimics CKAN's internal authorization middleware:

```python title="tests/logic/test_auth.py"
from __future__ import annotations

import pytest
from ckan.tests import factories
from ckan.tests.helpers import check_access
from ckan.plugins.toolkit import NotAuthorized

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestMyAuthRules:

    def test_item_create_sysadmin_allowed(self):
        """Verify sysadmin users can create items."""
        # Create a sysadmin user
        admin = factories.Sysadmin()
        
        context = {
            "user": admin["name"],
            "auth_user_obj": admin
        }
        
        # Verify access is granted (returns True or does not raise exception)
        result = check_access("myextension_item_create", context, {})
        assert result is True

    def test_item_create_anonymous_denied(self):
        """Verify anonymous users cannot create items."""
        context = {
            "user": None,
            "auth_user_obj": None
        }

        # Verify access raises NotAuthorized
        with pytest.raises(NotAuthorized):
            check_access("myextension_item_create", context, {})
```

---

## Testing Auth Functions Directly

Alternatively, you can test the auth functions directly by importing them. This is faster and avoids routing through CKAN's registration layer, which is useful for focused unit tests:

```python
from ckanext.myextension.logic.auth import myextension_item_create

def test_direct_auth_check(self):
    user = factories.User()
    context = {
        "user": user["name"],
        "model": None,  # Mock if needed
    }
    
    # Call function directly
    result = myextension_item_create(context, {})
    
    # Assert return structure
    assert result["success"] is False
    assert "Must be a sysadmin" in result["msg"]
```
