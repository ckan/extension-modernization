---
icon: lucide/layout-template
---

# Blueprints and Views

CKAN extensions expose HTTP interfaces, endpoints, and web pages using Flask
**Blueprints**. View functions are placed inside a `views.py` file (or `views/`
submodule) and registered automatically via `blueprints` blanket.

---

## Defining Blueprints

Define a Blueprint instance and map your views. To ensure consistency in error
states, you can register custom error handlers to render clean error templates:

```python title="views.py"
from __future__ import annotations

import logging
from flask import Blueprint, jsonify
import ckan.plugins.toolkit as tk

log = logging.getLogger(__name__)

# 1. Define the blueprint
bp = Blueprint("myextension", __name__)

# Optional: export the blueprint explicitly
__all__ = ["bp"]


# 2. Register global error handlers for this blueprint
def not_found_handler(error: tk.ObjectNotFound) -> tuple[str, int]:
    """Render custom 404 page for ObjectNotFound exceptions."""
    return (
        tk.render(
            "error_document_template.html",
            {
                "code": 404,
                "content": f"Object not found: {error.message}",
                "name": "Not Found",
            },
        ),
        404,
    )

bp.register_error_handler(tk.ObjectNotFound, not_found_handler)
```

---

## Implementing View Routes

Implement standard Flask routes. Use CKAN's toolkit functions to check
permissions, render Jinja2 templates, and read request params.

```python title="views.py"
@bp.route("/items", methods=["GET"])
def index() -> str:
    """Render items list page."""
    try:
        items = tk.get_action("myextension_item_list")({}, {}) # (1)!
    except tk.NotAuthorized:
        return tk.abort(403, "Not authorized to view items.")

    # Render templates placed inside the 'templates/' folder
    return tk.render("myextension/index.html", {"items": items})


@bp.route("/api/items/<id>", methods=["GET"])
def api_show(id: str):
    """API endpoint returning item details."""
    try:
        # If you did not add global 404 error handler,
        # add explicit ObjectNotFound handler
        item = tk.get_action("myextension_item_show")({}, {"id": id})
    except tk.NotAuthorized:
        return tk.abort(403, "Not authorized to view the item.")

    return jsonify(item)
```

1. You can pass empty context into auth functions and actions, when they are
   called from views. CKAN will add missing `user` and `session` properties
   automatically.

---

## Auto-Registration

Apply the `@tk.blanket.blueprints` decorator to your plugin class in
`plugin.py`. This scans the `views.py` file for Flask blueprints and
automatically hooks them into the CKAN routing framework.

```python title="plugin.py"
import ckan.plugins as p
import ckan.plugins.toolkit as tk

@tk.blanket.blueprints  # (1)
class MyExtensionPlugin(p.SingletonPlugin):
    pass
```

1. Automatic blueprint discovery removes the need to manually implement the
   `IBlueprint` interface or write route-registration boilerplate methods.
