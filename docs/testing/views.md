---
icon: lucide/eye
---

# Views

Views handle HTTP routing, request parsing, and HTML rendering. In CKAN, views are defined using Flask Blueprints. Tests should verify that URLs return correct status codes, redirect when necessary, and render template content.

---

## Simulating GET Requests

Use the `app` fixture (which wraps the Flask test client) to send GET requests to your routes:

```python title="tests/views/test_views.py"
from __future__ import annotations

import pytest

@pytest.mark.usefixtures("with_plugins")
class TestMyViews:

    def test_item_index_page_status(self, app):
        """Verify the item index page loads successfully."""
        # 1. Dispatch GET request
        response = app.get("/my-extension/items")

        # 2. Check HTTP status code
        assert response.status_code == 200

        # 3. Check for specific content in the rendered HTML
        assert "Items List" in response.data.decode("utf-8")
```

---

## Simulating POST Requests (Form Submissions)

To test form submissions, send POST requests containing form data. Ensure CSRF validation rules are satisfied:

```python
def test_item_create_submission(self, app, clean_db):
    """Verify that posting form data creates a record."""
    form_data = {
        "name": "new-posted-item",
        "title": "My Posted Item"
    }

    # Dispatch POST request simulating form submit
    response = app.post(
        "/my-extension/items/new",
        data=form_data,
        follow_redirects=True # Follow any redirect actions (e.g. redirecting to item index)
    )

    assert response.status_code == 200
    assert "new-posted-item" in response.data.decode("utf-8")
```

---

## Testing Redirects and Permissions

Verify that unauthorized users are redirected to login pages when accessing protected view routes:

```python
def test_protected_route_redirect(self, app):
    """Verify that accessing protected page redirects to login."""
    response = app.get("/my-extension/admin-panel")
    
    # Assert redirect code
    assert response.status_code == 302
    assert "/user/login" in response.headers["Location"]
```
