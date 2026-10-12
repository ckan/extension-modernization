---
name: ckan-docker-dev
description: Set up, diagnose, or change a CKAN Docker/Compose development environment, extension mounts, plugin variables, or container test commands; use only for a detected Docker workspace.
---

# CKAN Docker development

For implementation, follow the [shared lifecycle](../ckan-development/references/workflow.md)
once per task, including checks and the review offer at handoff.
This explicit topic request already selects the topic; do not restart routing.
For questions, planning, or reviewer work, read technical references only; do
not implement or dispatch a reviewer. Reviewer context never starts a lifecycle.

Resolve references from this installed skill's directory. Select only applicable
sections for the target project's supported versions and existing tooling.

| When relevant | Reference |
| --- | --- |
| Identify the distribution and commands before following a recipe | [docker development](../../../docs/environment/docker-development.md) |
| CI containers, when changing CI rather than local Compose | [github workflows](../../../docs/environment/github-workflows.md) |
