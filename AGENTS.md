# Contributing to CKAN Extension Guidelines

This repository contains documentation and an agent plugin, not a runnable
CKAN extension. Keep technical rules and examples in [docs](docs/index.md).
Keep skills as short workflows and selective references to those guides.

- For skill/routing changes, read the [development skill](.agents/skills/ckan-development/SKILL.md)
  and [shared lifecycle](.agents/skills/ckan-development/references/workflow.md).
- For reviewer changes, read [ckan-review](.agents/skills/ckan-review/SKILL.md).
  `.rovodev/.review-agent.md` is generated from its checklist: edit the
  checklist, then run `make rovo`.
- For packaging or adoption, read [agent usage](docs/agents/index.md) and
  [validation scenarios](docs/agents/testing.md).
- For hook changes, read [installation and updates](docs/agents/index.md#installation-and-updates):
  hooks act only in CKAN extension projects, stay fast and read-only, and
  `make check` pins their configuration and tests their behavior.
- For CKAN claims, verify the applicable version's source or official docs.
  Distinguish API requirements, recommended conventions, and optional recipes.
- Resolve skill references from the skill's directory; bundle their targets.
  Both clients must consume the same skills and docs. Keep provider adapters thin.

Use `make install` for pinned dependencies and `make check` for package,
reference, snippet, and strict site validation. Preview with `make serve`.
When changing invocation, also exercise the documented behavior scenarios.

Before handing off an implementation batch, request one independent read-only
review of the scoped changes and check results. Follow the review skill; do
not recursively delegate from a reviewer. Report unavailable checks or
delegation honestly. Read-only questions and planning do not need review.
Leave commits, pushes, and publishing to the developer.
