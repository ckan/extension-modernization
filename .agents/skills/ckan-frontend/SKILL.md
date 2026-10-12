---
name: ckan-frontend
description: Implement or review CKAN templates, WebAssets bundles, CSS/SASS, JavaScript modules, or existing Gulp/Vite builds; select browser tests only for interactive behavior.
---

# CKAN frontend

For implementation, follow the [shared lifecycle](../ckan-development/references/workflow.md)
once per task, including checks and the review offer at handoff.
This explicit topic request already selects the topic; do not restart routing.
For questions, planning, or reviewer work, read technical references only; do
not implement or dispatch a reviewer. Reviewer context never starts a lifecycle.

Resolve references from this installed skill's directory. Select only applicable
sections for the target project's supported versions and existing tooling.

| When relevant | Reference |
| --- | --- |
| Frontend architecture | [index](../../../docs/frontend/index.md) |
| Template overrides and inheritance | [templates](../../../docs/frontend/templates.md) |
| Registration and asset bundles | [assets](../../../docs/frontend/assets.md) |
| Stylesheets and RTL | [css](../../../docs/frontend/css.md) |
| JavaScript modules and events | [javascript](../../../docs/frontend/javascript.md) |
| Gulp, only when the project uses it | [gulpfile](../../../docs/environment/gulpfile.md) |
| Vite/TypeScript, only when the project uses it | [vite typescript](../../../docs/environment/vite-typescript.md) |
| Interactive browser coverage | [e2e playwright](../../../docs/testing/e2e-playwright.md) |
