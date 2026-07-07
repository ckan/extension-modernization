---
icon: lucide/help-circle
---

# Template Helpers

Template helpers are Python functions that are exposed to CKAN's Jinja2
templating system. They allow templates to call custom logic to format data,
fetch config properties, or retrieve dynamic dataset information using the `h`
global object (e.g., `h.myextension_some_helper()`).

---

## Naming and Namespacing

In older CKAN extensions, helpers were often defined with generic names (e.g.,
`get_featured_datasets` or `get_all_groups`). This creates conflicts if CKAN
core or other extensions register helpers with the same name.

/// admonition | Prefix Your Helpers
    type: important

Always prefix your helper functions with your extension's name (e.g.,
`myextension_recently_updated_info` instead of `recently_updated_info`). This
guarantees namespace safety.

///

---

## Best Practices for Modern Helpers

### A. Centralize Configuration Access

Instead of reading raw configurations inside helpers using
`tk.config.get(...)`, wrap config parameters in a dedicated `config.py` module
inside your extension and call the config helper function.

=== "Legacy (Direct config access)"

    ```python
    def matomo_url():
        # Directly querying config dictionary - harder to test and maintain
        return toolkit.config.get(
            'ckanext.myextensions.matomo.tracker_url',
            'https://analytics.example.com',
        )
    ```

=== "Modern (Config wrapper)"

    ```python
    from . import config  # Import your extension's centralized config module

    def myextension_matomo_url() -> str:
        # Calls wrapper function from config.py which handles fallbacks and types
        return config.matomo_tracker_url()
    ```

---

### B. Use Action APIs Instead of Direct DB Queries
Older extensions often query database tables (e.g., `model.Session.query(model.PackageExtra)`) directly inside helpers as a fallback when search indexes (Solr) are slow. This bypasses search caches and couples your extension to the internal database schema, which can change between CKAN versions.

!!! tip "Query via search API"
    Always use action API calls (such as `package_search` or `package_show`) to query datasets instead of writing database-level SQLAlchemy queries.

=== "Legacy (Direct DB fallback)"

    ```python
    import ckan.model as model

    def get_featured_datasets():
        # DB fallback is slow and Couples model to DB schema
        extras_query = model.Session.query(model.PackageExtra).filter(
            model.PackageExtra.key == 'is_featured', # (1)!
            model.PackageExtra.value == 'True'
        ).all()
        # ... logic to fetch packages ...
    ```

    1. This code may work in CKAN v2.11, but it breaks in v2.12, because `PackageExtra` model was removed.

=== "Modern (Action query)"

    ```python
    import ckan.plugins.toolkit as tk

    def yukon_get_featured_datasets() -> list[dict[str, Any]]:
        # Resolves via Solr search index - fast, cached, and API-compliant
        return tk.get_action("package_search")(
            {},
            {
                "fq": "is_featured:true AND type:data",
                "sort": "metadata_created desc",
            },
        )["results"]
    ```

---

### C. Write Typed and Annotated Helpers

Always supply PEP 484 type annotations for parameters and return types. Even
though helpers are usually called from templates, where type-checker has no
power, typing information can be used to detect internal anomalies inside
helper implementation.

```python
def my_count_uploaded_resources(pkg: dict[str, Any]) -> int:
    """Counts the number of uploaded resources in a package."""
    count = 0
    for res in pkg.get("resources", []):
        if res.get("url_type") == "upload":
            count += 1
    return count
```

---

## Auto-Registering Helpers

CKAN extensions register all helper functions automatically by applying the
`@tk.blanket.helpers` decorator to the plugin class in `plugin.py`.

```python title="plugin.py"
import ckan.plugins as p
import ckan.plugins.toolkit as tk

@tk.blanket.helpers  # (1)
class MyPlugin(p.SingletonPlugin):
    pass
```

1. Discovery scans your `helpers.py` file and exposes every defined function to
   the Jinja2 template context under the `h` namespace (e.g.,
   `h.my_count_uploaded_resources(package)`).
