---
icon: lucide/brush
---

# CSS & Styling

CKAN extensions structure their styling rules using **SASS (SCSS)**, which is compiled into standard CSS stylesheets. This ensures code modularity, theme customization support, and clean stylesheet structure.

---

## Stylesheet Layout

Organize SASS stylesheets inside your extension's assets directory:

```
ckanext-myextension/
└── ckanext/
    └── myextension/
        └── assets/
            └── scss/
                ├── main.scss           # Primary stylesheet entrypoint
                ├── main-rtl.scss       # Right-to-Left stylesheet entrypoint (1)
                └── components/         # Modular SASS files
                    ├── _buttons.scss
                    ├── _cards.scss
                    └── _header.scss
```

1. Standard stylesheet for RTL locales (like Arabic or Hebrew).

---

## Right-to-Left (RTL) Support

CKAN is translated into many languages and supports Right-to-Left layouts. If your extension changes structural positioning (like floating panels or custom layout alignments), you must provide RTL overrides in `main-rtl.scss`.

### `main.scss`
```scss
.my-card {
  margin-left: 20px;
  float: left;
}
```

### `main-rtl.scss`
```scss
@import "main"; // Import primary stylesheet

.my-card {
  margin-left: 0;
  margin-right: 20px;
  float: right;
}
```

/// note

Instead of using "left" and "right" keywords, you can use better CSS properties
that natively support different writing modes. For example, if you use
`margin-inline-start` and `float: inline-end` in the previous example, there
will be no need in custom overrides inside `main-rtl.scss`.


```scss
.my-card {
  margin-inline-start: 20px;
  float: inline-end;
}
```

///

---

## Best Practices for Styling

* **Avoid Hardcoded Colors**: Use CSS variables or SASS variables corresponding to CKAN theme variables (e.g. `var(--primary)`, `var(--body-bg)`) to ensure your extension matches the active theme color palette automatically.
* **Namespace Class Names**: Prefix CSS classes with your extension name (e.g. `.ckanext-myext-card` instead of `.card`) to prevent rule overriding and global style leaks.
* **Optimize Selectors**: Keep CSS selectors flat. Highly nested selectors (e.g. `.content .sidebar .nav ul li a`) slow down rendering performance and make it difficult to write overrides.

---

## Post-Processing & Optimization

Stylesheets should be optimized during the Gulp compilation step before being served:

* **Group Media Queries**: Use PostCSS plugins (like `postcss-sort-media-queries`) to combine media queries mobile-first, reducing duplication in compiled outputs.
* **Minification**: Production builds should minify files using `cleanCSS` to eliminate comments, whitespace, and optimize syntax rules.
* **Source Maps**: Enable source maps in development environments (`DEBUG=1`) to easily trace selectors back to their original SASS files in browser inspection tools.

Refer to the [Gulp Asset Compilation Guide](../environment/gulpfile.md) for configuring these post-processors.
