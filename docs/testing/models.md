---
icon: lucide/database-zap
---

# Models

Database model tests verify that database tables, constraints, column mappings,
and relationships are set up correctly.

---

## Testing Table Schema Constraints

Verify that model structures raise errors if database constraints (like nullability or uniqueness) are violated:

```python title="tests/test_models.py"
from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from ckanext.myextension.model import MyModel
from ckan import model
import ckan.plugins.toolkit as tk

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestDatabaseModels:

    def test_model_creation_success(self):
        """Verify successful model insertion and query."""

        # 1. Create model instance
        record = MyModel(name="test-record", description="Test description")
        model.Session.add(record)
        model.Session.commit()

        # 2. Query record back
        stmt = sa.select(MyModel).where(MyModel.name=="test-record")
        saved = model.Session.scalar(stmt)
        assert saved is not None
        assert saved.description == "Test description"

    def test_model_name_unique_constraint(self):

        # Insert first record
        record1 = MyModel(name="duplicate-name")
        model.Session.add(record1)
        model.Session.commit()

        # Insert second record with same name
        record2 = MyModel(name="duplicate-name")
        model.Session.add(record2)

        # Commit should raise IntegrityError
        with pytest.raises(IntegrityError):
            model.Session.commit()
```

---

## Testing Relationships and Cascades

If your custom models link to core tables (like `User` or `Package`) via
foreign keys, verify that deletion cascades behave as expected:

```python
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_user_deletion_cascade(self):
    """Verify that deleting a CKAN user cascades to custom model records."""

    # 1. Link custom model to user
    record = MyModel(name="cascaded-record", user_id=user["id"])
    model.Session.add(record)
    model.Session.commit()

    # 2. Delete user
    user_obj = model.Session.get(model.User, user["id"])
    model.Session.delete(user_obj)
    model.Session.commit()

    # 3. Verify record was cascaded and deleted
    stmt = sa.select(MyModel).where(MyModel.name=="cascaded-record")
    saved = model.Session.scalar(stmt)
    assert saved is None
```
