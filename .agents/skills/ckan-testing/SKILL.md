---
name: ckan-testing
description: Pytest testing guidelines for actions, permissions, blueprints/views, and CLI commands.
---

# CKAN Pytest Testing Guide

This skill provides comprehensive instructions on writing isolated, robust, and clean tests for actions, authorization functions, views, and CLI commands.

---

## Action and Auth Testing (Black-Box Approach)

Do not use monkeypatching or mock wrappers to verify that an action invokes other actions. Treat actions as black boxes: set up data, invoke the action, and verify the resulting state in the database or search index.

### Action Testing Structure
* **Context**: Avoid passing a context dictionary to `call_action` unless you are explicitly testing authentication or permission checks.
* **DB Verification**: Assert database state changes directly.

```python title="tests/test_actions.py"
import pytest
from ckan.tests import factories
from ckan.tests.helpers import call_action

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestItemActions:

    def test_item_delete(self, item_factory):
        # 1. Setup DB state using factories
        item = item_factory()
        
        # 2. Invoke action without redundant context parameters
        call_action("myextension_item_delete", id=item["id"])
        
        # 3. Assert side-effects/state directly (Black-Box verification)
        with pytest.raises(ObjectNotFound):
            call_action("myextension_item_show", id=item["id"])
```

### Parametrized Permission Testing
Use `@pytest.mark.parametrize` to verify access permissions for multiple roles without writing duplicate test functions:

```python title="tests/test_auth.py"
import pytest
from ckan.tests.helpers import call_action
from ckan.exceptions import NotAuthorized

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestItemAuth:

    @pytest.mark.parametrize(
        "user_role, should_allow",
        [
            ("sysadmin", True),
            ("member", False),
            ("anonymous", False),
        ],
    )
    def test_create_permissions(self, user_role, should_allow, user_factory):
        # Resolve user object based on roles
        if user_role == "anonymous":
            context = {"user": None}
        elif user_role == "sysadmin":
            sysadmin = user_factory(sysadmin=True)
            context = {"user": sysadmin["name"]}
        else:
            user = user_factory()
            context = {"user": user["name"]}

        if should_allow:
            # Action should succeed without throwing error
            result = call_action("myextension_item_create", context, name="test")
            assert result["name"] == "test"
        else:
            # Action must raise NotAuthorized exception
            with pytest.raises(NotAuthorized):
                call_action("myextension_item_create", context, name="test")
```

---

## View and Blueprint Testing

Test views by sending HTTP requests to blueprints using the Flask test client.

* **Authentication**: Use `app.set_session_user` to log users in.
* **HTML Parsing**: Use `BeautifulSoup` to find page elements. Do not perform regex checks on raw HTML strings.

```python title="tests/test_views.py"
import pytest
from bs4 import BeautifulSoup
from ckan.tests.helpers import url_for

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestViews:

    def test_settings_page(self, app, user_factory):
        user = user_factory()
        
        # Authenticate client
        app.set_session_user(user)
        
        # Retrieve blueprint URL and request page
        url = url_for("myextension_admin.settings")
        response = app.get(url)
        
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.body, "html.parser")
        settings_title = soup.select_one(".page-heading").text.strip()
        
        assert "My Extension Settings" in settings_title
```

---

## CLI Command Testing

Test click-based command line interfaces using the `cli` fixture.

* **Dynamic Command Load**: Use the `with_extended_cli` fixture to register commands registered dynamically by plugin classes.

```python title="tests/test_cli.py"
import pytest

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestCliCommands:

    def test_sync_command(self, cli, with_extended_cli):
        # Invoke CLI command
        result = cli.invoke(["myextension", "sync-items"])
        
        # Assert CLI output
        assert result.exit_code == 0
        assert "Sync completed successfully" in result.output
```

---

## E2E Playwright Browser Testing

For a subset of tests that verify complex frontend user interactions (such as interactive map bounding boxes, charting widgets, dynamic form state changes, or multi-step wizard processes), use **Playwright**.

* **Scope**: Do not use Playwright to test backend API logic, action parameter validation, or standard page redirects. These must be tested using standard backend tests (`call_action` or `app`).
* **Fixture Configuration**: Add base URL parameters to `browser_context_args` in `conftest.py` mapping to `ckan.site_url`.
* **Shared Authentication**: Authenticate using the `login` helper which appends an API Authorization header to the page context instead of performing slow web logins.

```python title="tests/e2e/test_ui.py"
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestInteractiveUI:

    def test_bounding_box_selection(self, page: Page, login):
        # 1. Log in via API header
        login("sysadmin")
        
        # 2. Open spatial search form
        page.goto("/dataset/new")
        
        # 3. Draw bounding box on leaflet map
        map_canvas = page.locator(".leaflet-container")
        expect(map_canvas).to_be_visible()
        # Simulate browser interactions ...
```
