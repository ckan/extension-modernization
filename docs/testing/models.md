---
icon: lucide/database-zap
---

# Models

Database model tests verify that database tables, constraints, column mappings, and relationships are set up correctly.

---

## Testing Table Schema Constraints

Verify that model structures raise errors if database constraints (like nullability or uniqueness) are violated:

```python title="tests/test_models.py"
from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from ckanext.myextension.model import MyModel
import ckan.plugins.toolkit as tk

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestDatabaseModels:

    def test_model_creation_success(self):
        """Verify successful model insertion and query."""
        session = tk.get_action("model")["session"]

        # 1. Create model instance
        record = MyModel(name="test-record", description="Test description")
        session.add(record)
        session.commit()

        # 2. Query record back
        saved = session.query(MyModel).filter_by(name="test-record").first()
        assert saved is not None
        assert saved.description == "Test description"

    def test_model_name_unique_constraint(self):
        """Verify that duplicate names trigger an IntegrityError."""
        session = tk.get_action("model")["session"]

        # Insert first record
        record1 = MyModel(name="duplicate-name")
        session.add(record1)
        session.commit()

        # Insert second record with same name
        record2 = MyModel(name="duplicate-name")
        session.add(record2)

        # Commit should raise IntegrityError
        with pytest.raises(IntegrityError):
            session.commit()
```

---

## Testing Relationships and Cascades

If your custom models link to core tables (like `User` or `Package`) via foreign keys, verify that deletion cascades behave as expected:

```python
def test_user_deletion_cascade(self, clean_db):
    """Verify that deleting a CKAN user cascades to custom model records."""
    session = tk.get_action("model")["session"]
    
    # 1. Create a user and link custom model
    user = factories.User()
    record = MyModel(name="cascaded-record", user_id=user["id"])
    session.add(record)
    session.commit()

    # 2. Delete user
    user_obj = session.query(User).filter_by(id=user["id"]).first()
    session.delete(user_obj)
    session.commit()

    # 3. Verify record was cascaded and deleted
    saved = session.query(MyModel).filter_by(name="cascaded-record").first()
    assert saved is None
```
