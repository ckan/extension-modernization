---
icon: lucide/file-code
---

# Templates

CKAN frontend pages are rendered using the **Jinja2** templating
engine. Extensions override, extend, and modularize HTML structures using clean
template layouts and inheritance structures.

---

## Template Directory Layout

Place templates inside a `templates/` directory under your package root:

```
ckanext-myextension/
├── ckanext/
│   └── myextension/
│       ├── plugin.py
│       └── templates/
│           ├── page.html
│           ├── myextension/
│           │   └── index.html
│           └── snippets/              # Reusable template fragments
│               └── item_card.html
```

Ensure this directory is registered in your `plugin.py` using `IConfigurer`:
```python
def update_config(self, config: tk.CKANConfig):
    tk.add_template_directory(config, "templates")
```

---

## Template Inheritance

To override or modify an existing CKAN template (like `package/read.html`), you can define a template with the exact same path and name in your extension.

To inherit from the core version of that template (rather than completely overwriting it), use the `{% ckan_extends %}` tag. This functions similarly to Flask's `{% extends %}` but avoids infinite recursion.

```django title="templates/package/read.html"
{# 1. Inherit from the core read.html template #}
{% ckan_extends %}

{# 2. Override specific blocks #}
{% block secondary_content %}
    {# 3. Call super() to keep the core content of this block #}
    {{ super() }}

    {# 4. Add custom markup #}
    <div class="custom-sidebar-widget">
        <h3>My Custom Extension Widget</h3>
        <p>This content is added to the sidebar.</p>
    </div>
{% endblock %}
```

---

## Template Variables & Helpers

Templates have access to several global objects:

* `h`: The helpers registry. Call helper functions to format data or access config properties (e.g., `#!django {{ h.lang() }}`).
* `g`: Global template rendering context.
* `request`: current request object
* `current_user`: currently authenticated `User` object, or `AnonymousUser`.

```html
{# Example of formatting a date helper #}
<span class="date">{{ h.render_datetime(package.metadata_modified) }}</span>
```

---

## Snippets

Snippets are reusable HTML fragments that can be included in other templates. They should be placed under a `snippets/` folder. Use the `{% snippet %}` tag to render them, passing variables as keyword arguments.

### The Snippet file
```django title="templates/snippets/item_card.html"
<div class="item-card">
    <h4>{{ title }}</h4>
    <p>{{ description | default('No description provided') }}</p>
</div>
```

### Rendering the Snippet
```django title="templates/myextension/index.html"
{% extends "page.html" %}

{% block content %}
    <h1>Items</h1>
    {% for item in items %}
        {# Render the snippet passing local variables #}
        {% snippet 'snippets/item_card.html', title=item.name, description=item.description %}
    {% endfor %}
{% endblock %}
```
