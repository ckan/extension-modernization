---
icon: lucide/eye
---

# Views

Views handle HTTP routing, request parsing, and HTML rendering. In CKAN, views
are defined using Flask Blueprints. Tests should verify that URLs return
correct status codes, redirect when necessary, and render template content.

---

## Simulating GET Requests

Use the `app` fixture (which wraps the Flask test client) to send GET requests
to your routes.

```python title="tests/views/test_views.py"
from __future__ import annotations

import pytest
from ckan import types

@pytest.mark.usefixtures("with_plugins")
class TestMyViews:

    def test_item_index_page_status(self, app: types.FixtureApp):
        """Verify the item index page loads successfully."""
        # 1. Dispatch GET request
        response = app.get("/my-extension/items")

        # 2. Check HTTP status code
        assert response.status_code == 200

        # 3. Check for specific content in the rendered HTML
        assert "Items List" in response.body
```

---

## Simulating POST Requests (Form Submissions)

To test form submissions, send POST requests containing form data.


```python
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_item_create_submission(self, app: types.FixtureApp, user: dict[str, Any]):
    """Verify that posting form data creates a record."""
    form_data = {
        "name": "new-posted-item",
        "title": "My Posted Item"
    }

    # Authenticate the session
    app.set_session_user(user)

    # Dispatch POST request simulating form submit
    response = app.post(
        "/my-extension/items/new",
        data=form_data,
    )

    assert response.status_code == 200
    assert "new-posted-item" in response.body
```

---

## Authenticating in View Tests

When testing views that require authentication (like dataset creation forms or
user dashboard pages), you must authenticate the Flask test client. There are
two primary methods to accomplish this:

### Session Authentication (`set_session_user`)

The easiest way to simulate a logged-in user session is to call the
`set_session_user()` method on the `app` client:

```python
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_dashboard_authenticated(self, app, user):
    app.set_session_user(user["name"])

    response = app.get("/dashboard")
    assert response.status_code == 200
    assert f"Welcome, {user['name']}" in response.body

    app.set_session_user()

    response = app.get("/dashboard", follow_redirects=False) # (1)!
    assert response.status_code == 302
```

1. Client follows redirects by default. If you need to make sure that dashboard
   is not rendered, it's easier to disable redirects and check status code.

/// admonition | Session Cookie Domain Configuration
    type: warning

Due to Flask implementation details, your configuration's
`SESSION_COOKIE_DOMAIN` must match the domain specified by `ckan.site_url` (or
be left completely empty to automatically fallback to the correct domain). If
there is a mismatch (for example, if `ckan.site_url` is `http://localhost:5000`
but `SESSION_COOKIE_DOMAIN` is set to `http://127.0.0.1`), session cookies will
be rejected, and mock login data will not persist between requests.

///

### Token Authentication (`Authorization` Header)

If you are testing API actions, AJAX endpoints, or views configured to validate
authorization headers, use `api_token` fixture to generate an API token and
pass it inside the request's `headers` dictionary:

```python
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_api_view_with_token(self, app: types.FixtureApp, api_token: dict[str, Any]):
    headers = {"Authorization": token["token"]}

    response = app.get(
        "/api/action/myextension_item_list",
        headers=headers
    )

    assert response.status_code == 200
```

---

## Testing Redirects and Permissions

Disable `follow_redirects` to verify that unauthorized users are redirected to
login pages when accessing protected view routes.

```python
def test_protected_route_redirect(self, app):
    """Verify that accessing protected page redirects to login."""
    response = app.get("/my-extension/admin-panel", follow_redirects=False)

    # Assert redirect code
    assert response.status_code == 302
    assert "/user/login" in response.headers["Location"]
```

---

## Parsing HTML with BeautifulSoup

When testing views, the response body contains raw HTML. To perform robust
assertions on structural elements, classes, attributes, or text nodes, parse
the response using **BeautifulSoup** (`bs4`):

```python
from bs4 import BeautifulSoup

def test_items_view_content(app):
    response = app.get("/my-extension/items")
    assert response.status_code == 200

    # 1. Parse HTML using BeautifulSoup
    soup = BeautifulSoup(response.body, "html.parser")

    # 2. Find elements by tag name and text
    header = soup.find("h1")
    assert header is not None
    assert header.text.strip() == "Items List"

    # 3. Find list of elements using CSS class
    items = soup.find_all("div", class_="item-card")
    assert len(items) == 5

    # 4. Locate elements using CSS selectors (select_one or select)
    create_button = soup.select_one("a.btn-primary[href*='new']")
    assert create_button is not None
    assert "Create item" in create_button.text.strip()
```

!!! tip ""

/// admonition | BeautifulSoup Best Practices
    type: tip


* Prefer using `soup.select_one()` and `soup.select()` with CSS selectors for
  targeting specific nodes, as they match browser-level selector patterns.
* Defensively assert that nodes are not `None` before calling `.text` to
  prevent unhelpful `AttributeError` exceptions in your test logs.

///
