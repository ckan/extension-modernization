---
icon: lucide/terminal-square
---

# E2E with Playwright

End-to-End (E2E) tests automate browser actions (clicking buttons, filling forms, and navigating pages) to verify that the UI works correctly. Playwright is the recommended tool for Pytest-based E2E tests.

---

## Setup Requirements

E2E tests require a running instance of your CKAN application. Before executing
tests, start the CKAN dev server in a separate terminal:

```bash
ckan -c test.ini run
```

/// admonition | Install playwright
    type: note

Install `pytest-playwright` and then install the browser using `playwright` CLI.

```sh
pip install pytest-playwright
playwright install firefox chromium
```

///

---

## Setup site URL

Add `ckan.site_url` to playwright's browser context. It allows using not
fully-qualified URLs in tests.

```python title="conftest.py"

@pytest.fixture
def browser_context_args(browser_context_args, ckan_config):
    """Modify playwright's standard configuration of browser's context."""
    browser_context_args["base_url"] = ckan_config["ckan.site_url"]
    return browser_context_args

```

---
## Shared Login Fixture

To automate user authentication during tests, define a `login` fixture in `conftest.py` that sets an API Authorization header on the page context:

```python title="conftest.py"
from __future__ import annotations

from typing import Any
import pytest
from playwright.sync_api import Page

@pytest.fixture
def login(api_token_factory: Any, page: Page):
    """Provides a function to log in users in browser sessions."""

    def authenticator(user: str | dict[str, Any], _page: Page | None = None):
        if _page is None:
            _page = page

        if isinstance(user, dict):
            user = user["name"]

        # Generate API token and apply to request headers
        token = api_token_factory(user=user)["token"] if user else ""
        _page.set_extra_http_headers({"Authorization": token})

    return authenticator
```

---

## Writing E2E Tests

Write your tests under `tests/e2e/` injecting the `page` and `login` fixtures:

```python title="tests/views/test_e2e.py"
from __future__ import annotations

from typing import Any
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestUIPages:

    def test_anonymous_user_index(self, page: Page):
        """Verify anonymous users can browse public items."""
        # Navigate to the page
        page.goto("/my-extension/items")

        # Expect title
        expect(page).to_have_title("Public Items - CKAN")

        # Locate page elements
        header = page.locator(".page-header")
        expect(header).to_contain_text("Items List")

    def test_authorized_user_create(self, page: Page, login: Any):
        """Verify logged-in users can create records via form."""
        # 1. Log in
        login("testuser")

        # 2. Go to creation form page
        page.goto("/my-extension/items/new")

        # 3. Fill and submit form
        page.fill("#field-name", "my-new-e2e-item")
        page.fill("#field-title", "E2E Created Item")
        page.click("button[type=submit]")

        # 4. Assert success redirect and details page content
        expect(page).to_have_url(f"/my-extension/items/my-new-e2e-item")
        expect(page.locator("h1")).to_contain_text("E2E Created Item")
```
