---
name: ckan-testing
description: Write, change, or review CKAN tests for actions, auth, models, views, CLI, helpers, fixtures, factories, or browser interactions. Also use when diagnosing failures or missing behavior coverage.
---

# CKAN testing

For implementation, follow the [shared lifecycle](../ckan-development/references/workflow.md)
once per task, including checks and the review offer at handoff.
This explicit topic request already selects the topic; do not restart routing.
For questions, planning, or reviewer work, read technical references only; do
not implement or dispatch a reviewer. Reviewer context never starts a lifecycle.

Resolve references from this installed skill's directory. Select only applicable
sections for the target project's supported versions and existing tooling.

| When relevant | Reference |
| --- | --- |
| Select the test layer and project conventions | [index](../../../docs/testing/index.md) |
| Pure logic and focused unit tests | [unit tests](../../../docs/testing/unit-tests.md) |
| Action behavior | [actions](../../../docs/testing/actions.md) |
| Authorization boundaries | [auth functions](../../../docs/testing/auth-functions.md) |
| Models | [models](../../../docs/testing/models.md) |
| Views and client authentication | [views](../../../docs/testing/views.md) |
| CLI | [cli](../../../docs/testing/cli.md) |
| Helpers | [helpers](../../../docs/testing/helpers.md) |
| Fixture lifecycle; read only the needed fixture sections | [fixtures](../../../docs/testing/fixtures.md) |
| Factories; read only the relevant creation/stub sections | [test factories](../../../docs/testing/test-factories.md) |
| Interactive Playwright coverage | [e2e playwright](../../../docs/testing/e2e-playwright.md) |
| Existing Cypress suites | [e2e cypress](../../../docs/testing/e2e-cypress.md) |
