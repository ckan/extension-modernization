---
name: ckan-frontend
description: Frontend customization guidelines covering templates, SASS/CSS WebAssets, and Javascript modules.
---

# CKAN Frontend and UI Customization

This skill provides comprehensive instructions on writing templates, managing stylesheets, compiling SASS/CSS, and creating interactive Javascript scripts.

---

## Template Overrides and Inheritance

CKAN uses the Jinja2 templating system. To modify pages, register your template directories and override files matching the original CKAN core structure.

### Registering Directories
Register your asset and template directories inside your plugin class:

```python title="plugin.py"
import ckan.plugins as p
import ckan.plugins.toolkit as tk

from typing_extensions import override

class MyThemePlugin(p.IConfigurer, p.SingletonPlugin):

    @override
    def update_config(self, config):
        # Register templates (relative to plugin.py)
        tk.add_template_directory(config, 'templates')
        # Register public assets
        tk.add_public_directory(config, 'public')
```

### Template Inheritance (`{% ckan_extends %}`)
Use `{% ckan_extends %}` to inherit from core layouts. Override only specific blocks to ensure future compatibility:

```html title="templates/header.html"
{% ckan_extends %}

{% block header_logo %}
  <div class="logo">
    <a href="{{ h.url_for('home.index') }}">
      <img src="{{ h.url_for_static('/images/custom-logo.png') }}" alt="Logo" />
    </a>
  </div>
{% endblock %}
```

---

## Stylesheets and SASS (WebAssets)

CKAN bundles frontend resources using WebAssets. You must define your stylesheets as resource bundles.

### Register WebAsset Resource and Bundles
1. **Define Bundles in `webassets.yml`**: Create a configuration file at `assets/webassets.yml` under your extension root:
   ```yaml title="assets/webassets.yml"
   mytheme_styles:
     filter: cssmin
     output: mytheme/%(version)s-theme.css
     contents:
       - css/theme.css
   ```

2. **Register the Resource Folder**: Inside your plugin class:
   ```python title="plugin.py"
       @override
       def update_config(self, config):
           tk.add_template_directory(config, 'templates')
           # Register static assets folder for images/icons
           tk.add_public_directory(config, 'public')
           # Register assets folder to process webassets.yml
           tk.add_resource('assets', 'mytheme')
   ```

### Load Assets in Templates
Import the configured asset bundle inside templates using the `{% asset %}` macro:

```html title="templates/page.html"
{% ckan_extends %}

{% block styles %}
  {{ super() }}
  {# Load WebAssets bundle by resource/bundle name #}
  {% asset 'mytheme/mytheme_styles' %}
{% endblock %}
```

---

## Javascript Modules (WebAssets & CKAN Modules)

CKAN uses a modular Javascript architecture. Scripts are registered as modules that bind to HTML elements. Like CSS, all Javascript files must be compiled, bundled through WebAssets, and loaded into templates.

### 1. Create the JS Module Script
Write your module code inside `assets/js/custom-counter.js`:

```javascript title="assets/js/custom-counter.js"
this.ckan.module('custom-counter', function (jQuery, _) {
  return {
    initialize: function () {
      var element = this.el;
      
      // Access options passed from Jinja2 templates
      var step = this.options.step || 1;
      console.log('Counter initialized with step:', step);
    }
  };
});
```

### 2. Bundle JS in `webassets.yml`
Define the Javascript bundle in `assets/webassets.yml`. You must specify a dependency on `base/main` in the `preload` block so CKAN core's module registry loads first:

```yaml title="assets/webassets.yml"
mytheme_js:
  filter: rjsmin
  output: mytheme/%(version)s-main.js
  extra:
    preload:
      - base/main
  contents:
    - js/custom-counter.js
```

### 3. Inject JS and Bind to HTML
Load the bundle in your template scripts block and add the matching `data-module` attribute to your HTML element:

```html title="templates/page.html"
{% ckan_extends %}

{% block scripts %}
  {{ super() }}
  {# Load the WebAssets JS bundle #}
  {% asset 'mytheme/mytheme_js' %}
{% endblock %}

{% block content %}
  <div data-module="custom-counter" data-module-step="5">
    Loading counter...
  </div>
{% endblock %}

---

## Static Files Mappings

Always resolve path names to static files (such as images, SVGs, or fonts) using the static URL helper to prevent broken link errors in production environments:

```html
<img src="{{ h.url_for_static('/images/banner.jpg') }}" alt="Banner" />
```
