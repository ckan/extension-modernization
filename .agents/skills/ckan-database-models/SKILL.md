---
name: ckan-database-models
description: Add or change CKAN extension database models, SQLAlchemy queries, dictization, or Alembic migrations; also use when reviewing persistence changes.
---

# CKAN models and migrations

For implementation, follow the [shared lifecycle](../ckan-development/references/workflow.md)
once per task, including checks and the review offer at handoff.
This explicit topic request already selects the topic; do not restart routing.
For questions, planning, or reviewer work, read technical references only; do
not implement or dispatch a reviewer. Reviewer context never starts a lifecycle.

Resolve references from this installed skill's directory. Select only applicable
sections for the target project's supported versions and existing tooling.

| When relevant | Reference |
| --- | --- |
| Models, queries, and serialization; choose the supported-version example | [database models](../../../docs/development/database-models.md) |
| Schema changes and migration isolation | [database migrations](../../../docs/development/database-migrations.md) |
| Model tests | [models](../../../docs/testing/models.md) |
