---
name: ckan-actions-auth
description: Implement or change CKAN action functions, authorization rules, validation schemas, custom validators, or chained actions/auth; also use when reviewing changes in those areas.
---

# CKAN actions and authorization

For implementation, follow the [shared lifecycle](../ckan-development/references/workflow.md)
once per task, including checks and the review offer at handoff.
This explicit topic request already selects the topic; do not restart routing.
For questions, planning, or reviewer work, read technical references only; do
not implement or dispatch a reviewer. Reviewer context never starts a lifecycle.

Resolve references from this installed skill's directory. Select only applicable
sections for the target project's supported versions and existing tooling.

| When relevant | Reference |
| --- | --- |
| Action design, registration, context propagation, chaining | [adding actions](../../../docs/development/adding-actions.md) |
| Schema and custom validator behavior | [validators](../../../docs/development/validators.md) |
| Action tests | [actions](../../../docs/testing/actions.md) |
| Permission tests | [auth functions](../../../docs/testing/auth-functions.md) |
