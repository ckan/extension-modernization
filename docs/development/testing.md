---
icon: lucide/test-tube-2
---

# Writing Tests

CKAN extensions run their test suites using **Pytest**. Tests are categorized
into unit/logic tests (running actions and verifying DB entries) and end-to-end
(E2E) tests (automating browser interactions).

---

## Unit & Logic Testing

Unit tests verify that actions, models, helpers, and schemas behave
correctly. Extensions use the `pytest-ckan` package for test execution and
database isolation.

### Directory Layout

```
ckanext-myextension/
├── ckanext/
│   └── myextension/
│       └── tests/
│           ├── conftest.py     # Shared fixtures
│           ├── test_utils.py   # Unit tests
│           └── logic/
│               └── test_action.py # Logic API tests
```

### Setup Fixtures (`conftest.py`)

A clean database state is required for database-bound tests. Use the `clean_db` fixture to reset and run migrations:

```python title="tests/conftest.py"
from __future__ import annotations

from typing import Any
import pytest

@pytest.fixture
def clean_db(reset_db: Any, migrate_db_for: Any):
    """Reset the DB state and run this extension's migrations."""
    reset_db()
    migrate_db_for("myextension")  # (1)
```

1. Runs Alembic migrations specific to `myextension` to prepare database schemas.

---

### Writing Logic Tests

Use `call_action` to execute extension business logic and verify outcomes.

```python title="tests/logic/test_action.py"
from __future__ import annotations

import pytest
from ckan.tests import factories
from ckan.tests.helpers import call_action

@pytest.mark.usefixtures("with_plugins", "clean_db") # (1)!
class TestMyExtensionActions:

    def test_item_create_success(self):
        """Test that item is successfully created and returned."""
        data = {"name": "My test item", "description": "Some description"}

        result = call_action("myextension_item_create", **data)

        assert result["name"] == "My test item"
        assert "id" in result

    def test_item_create_validation_error(self):
        """Test that validation schema catches missing name parameter."""
        data = {"description": "Some description"}  # Missing 'name'

        with pytest.raises(Exception) as excinfo:
            call_action("myextension_item_create", **data)

        assert "name" in str(excinfo.value)
```

1. Always apply `with_plugins` fixture before `clean_db`, to load plugins that
   contain corresponding DB migrations.

---

## End-to-End (E2E) Testing

E2E tests automate browser workflows using **Selenium**, **Cypress**,
**Playwright** or similar tool. They ensure pages render correctly and UI flows
succeed.

Here we'll be using playwright, because it requires minimal amount of efforts
to write the simple tests and run it using pytest.

/// note

Usually e2e tests require running CKAN app. Before executing any of the tests
below, do not forget to start test CKAN instance inside a separate terminal session.

```sh
ckan -c test.ini run
```

///

### Writing E2E Tests

E2E tests require loading the extension's plugins. Use
`@pytest.mark.usefixtures("with_plugins")` and inject the `page` fixture:

```python title="tests/views/test_views.py"
from __future__ import annotations

from typing import Any
import pytest
from playwright.sync_api import Page, expect
import ckan.plugins.toolkit as tk

@pytest.mark.usefixtures("with_plugins")  # (1)
class TestItemViews:

    def test_index_page_title(self, page: Page):
        """Verify the index page title loads correctly."""
        # 1. Navigate to view route. Avoid using `url_for` in e2e tests
        page.goto("/my-extension/items")

        # 2. Check title or headings using expect
        expect(page).to_have_title("My Items - CKAN")

        # 3. Locate element
        btn = page.get_by_role("button", name="Create item")
        expect(btn).to_be_visible()
```

1. Tells pytest-ckan to activate the extension's plugin inside the test Flask context.

---

### Authenticating in E2E Tests

Use fixtures to automate E2E authentication. You can mock cookie authentication using Flask remember cookies or inject API tokens into headers.

```python title="tests/conftest.py"
from __future__ import annotations

from typing import Any
import pytest
from flask_login import encode_cookie
from playwright.sync_api import BrowserContext, Page

@pytest.fixture
def login(api_token_factory: Any, page: Page):
    """Provides a function for authentication."""

    def authenticator(user: str | dict[str, Any], _page: Page | None = None):
        if _page is None:
            _page = page

        if isinstance(user, dict):
            user = user["name"]

        token: str = api_token_factory(user=user)["token"] if user else ""
        _page.set_extra_http_headers({"Authorization": token})

    return authenticator

```

Use the login helper directly in your test function:

```python
def test_dashboard_access_authorized(page: Page, login: Any):
    # Log in as testuser
    login("testuser")
    page.goto("/dashboard")

    expect(page.locator(".dashboard-header")).to_be_visible()
```
