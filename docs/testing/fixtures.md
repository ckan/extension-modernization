---
icon: lucide/test-tube
---

# Setup Fixtures

Fixtures are reusable components that set up state, prepare mocks, or expose
APIs to your tests. CKAN extensions utilize Pytest fixtures for plugin loading
and database lifecycle management.

---

## The `clean_db` Fixture

Since CKAN tests share a single database, you must reset the database state and apply your migrations before running database-bound tests.

Define `clean_db` in your `conftest.py` file using core helper fixtures `reset_db` and `migrate_db_for`:

```python title="tests/conftest.py"
from __future__ import annotations

from typing import Any
import pytest

@pytest.fixture
def clean_db(reset_db: Any, migrate_db_for: Any):
    """Reset the database state and run this extension's migrations."""
    reset_db()
    migrate_db_for("myextension") # (1)
```

1. Runs the Alembic migrations defined in the `myextension` migration folder.

---

## The `with_plugins` Fixture

This fixture loads your extension plugins inside the Flask app context. Always combine `with_plugins` with the `clean_db` fixture when testing models or logic actions:

```python
import pytest

@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_something():
    # Test executes with extension plugins active and a migrated database
    pass
```

---

## The `app` Fixture

Exposes the Flask test client, letting you simulate HTTP requests directly against your views without starting a real web server:

```python
def test_about_page_status(app):
    response = app.get("/about")
    assert response.status_code == 200
```

---

## The `api_token_factory` Fixture

Generates API tokens for test users. This is useful when testing authenticated action calls or routes:

```python
def test_authenticated_action(api_token_factory):
    # Generates a valid API token for a test user
    token = api_token_factory(user="admin")["token"]
```
