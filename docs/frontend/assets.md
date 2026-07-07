---
icon: lucide/box
---

# Webassets

CKAN extensions manage JavaScript and CSS using Webassets. Extensions place
these files in an `assets/` directory and configure registration inside
`plugin.py`.

---

## Asset Directory Layout

Create an `assets/` directory at your extension's root:

```
ckanext-myextension/
├── ckanext/
│   └── myextension/
│       ├── plugin.py
│       ├── assets/              # Static files directory
│       │   ├── css/
│       │   │   └── custom.css
│       │   ├── js/
│       │   │   └── custom.js
│       │   └── webassets.yml    # Webassets bundle configurations
```

---

## Asset Pipeline Flow

1. **Source Files**: Write raw SASS (`.scss`) or TypeScript (`.ts`) files in development folders (e.g. `assets/scss/`, `assets/ts/`).
2. **Build Tools**: Run compilers (Gulp or Vite) to output compiled `.css` and `.js` files directly into the `assets/` directory.
3. **Webassets Bundle**: Define asset groups (bundles) inside `assets/webassets.yml`.
4. **Template Injection**: Load the defined bundles into templates using the `{% asset %}` Jinja2 tag.

---

## Registering Assets

Implement `IConfigurer` inside your plugin to register the assets directory:

```python title="plugin.py"
from typing_extensions import override

import ckan.plugins as p
import ckan.plugins.toolkit as tk

class MyExtensionPlugin(p.IConfigurer, p.SingletonPlugin):
    @override
    def update_config(self, config: tk.CKANConfig):
        # Register templates
        tk.add_template_directory(config, "templates")

        # Register the assets folder under a specific namespace prefix
        # This makes bundles defined in 'assets/webassets.yml'
        # accessible as 'myextension/ASSET_NAME'
        tk.add_resource("assets", "myextension")
```

---

## Webassets Configuration

Define Webassets bundles to bundle and minify asset files. This is configured
in a `webassets.yml` file placed at the root of the `assets/` folder.

```yaml title="assets/webassets.yml"
myextension_custom_css:
  filter: cssmin
  output: myextension/%(version)s-custom.css # (1)!
  contents:
    - css/custom.css

myextension_custom_js:
  filter: rjsmin
  output: myextension/%(version)s-custom.js
  extra: # (2)!
    preload:
      - base/main
  contents:
    - js/custom.js
```

1. Always add `%(version)s` part to the asset name. `version` variable will be
   replaced with the bundle's content-hash, providing asset immutability and
   allowing permanent cache for asset files.
2. `#!yaml extra: {preload: [...]}` adds dependency on other assets. They will
   be loaded before the current asset. Mainly this is used with CKAN JS
   modules: dependency on `base/main` loads module toolset, such as sandbox or
   module registration function before the plugin and eliminates posibility of
   `ckan.register(...) is undefined` error.
---

## Injecting Assets in Templates

To inject these assets into a Jinja2 template page, use the `{% asset %}` tag
with the bundle name.

```django title="templates/my_template.html"
{% extends "page.html" %}

{% block styles %}
    {{ super() }}
    {# Inject Webassets CSS bundle #}
    {% asset 'myextension/myextension_custom_css' %}
{% endblock %}

{% block scripts %}
    {{ super() }}
    {# Inject Webassets JS bundle #}
    {% asset 'myextension/myextension_custom_js' %}
{% endblock %}

{% block content %}
    <h1>My Extension Page</h1>
    <p>This page loads custom CSS and JavaScript bundles.</p>
{% endblock %}
```
