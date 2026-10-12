---
name: ckan-development
description: Use for any change to a CKAN extension, from a one-line config option to a new feature or modernization, including config, actions, views, templates, CLI, helpers, signals, tests, packaging, and CI. Checks supported versions, runs the shared check workflow, offers an independent review, and routes to focused topic skills. Also answers CKAN extension questions from the guides, without offering a review.
---

# CKAN development

For implementation, follow the [shared lifecycle](references/workflow.md)
once per task, including when another topic skill brought you here. An explicit
topic request already chooses the topic: do not restart skill selection.
For questions or planning, use relevant references only. In reviewer context,
use only the routing table below; never start implementation or another review.

Resolve every relative reference from this file's directory in the installed
plugin, not from the consuming project's working directory. Read selected
sections, not every guide in a category.

## Route the task

| Task or changed area | Read when relevant |
| --- | --- |
| Actions, permissions, schemas, validators | [ckan-actions-auth](../ckan-actions-auth/SKILL.md) |
| Models, queries, serialization, migrations | [ckan-database-models](../ckan-database-models/SKILL.md) |
| Templates, CSS, JavaScript, asset builds | [ckan-frontend](../ckan-frontend/SKILL.md) |
| Tests, fixtures, factories, browser behavior | [ckan-testing](../ckan-testing/SKILL.md) |
| Docker, Compose, container configuration | [ckan-docker-dev](../ckan-docker-dev/SKILL.md) |
| Extension structure and registrations | [Overview](../../../docs/development/index.md), [plugins](../../../docs/development/defining-plugins.md) |
| Configuration declarations, runtime options, or environment variables | [Configuration](../../../docs/development/config-management.md) |
| Blueprints or administrative commands | [Views](../../../docs/development/adding-views.md), [CLI](../../../docs/development/cli-commands.md), and the [thin-wrapper rule](../../../docs/development/index.md#the-feature-development-process): views and CLI call actions |
| Event subscribers or template helpers | [Signals](../../../docs/development/signals.md), [helpers](../../../docs/development/template-helpers.md) |
| Annotations or type-checker compatibility | [Typing](../../../docs/development/typing.md) |
| Package metadata or dependencies | [Packaging](../../../docs/environment/package-configuration.md), [requirements](../../../docs/environment/requirements.md) |
| Lint/type tools or CI | [Tools](../../../docs/environment/tools.md), [workflows](../../../docs/environment/github-workflows.md) |
| Release preparation | [Publishing](../../../docs/environment/publishing.md), [changelogs](../../../docs/environment/changelogs.md); leave publication to the developer |

Choose both implementation and matching test guidance for behavior changes.
The guides distinguish required contracts from recommendations and optional
recipes; apply their version conditions and the consuming project's policy.
