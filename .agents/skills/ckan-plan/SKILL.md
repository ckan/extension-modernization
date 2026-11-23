---
name: ckan-plan
description: Interview the developer to agree on goals and design before code is written for a CKAN extension feature, change, or new extension. Use when asked to plan, scope, or stress-test ("grill me") such work; not for requests to implement directly.
---

# CKAN plan

Until the developer approves the plan, do not edit files, run the development
lifecycle, or request a review. Resolve references from this installed skill's directory.

## Run the interview

Look facts up before asking: the extension's code and configuration, and the
guides routed by [ckan-development](../ckan-development/SKILL.md#route-the-task).
Bring only decisions to the developer, never questions the project can answer.
Base each recommendation on the matching guide section, reading the section
itself rather than only its heading, and say when it departs from the guide,
for example to follow an existing project pattern.

A plan is a set of decisions, and some depend on others. Proceed in rounds:

1. Ask every decision that no longer depends on an open one. Number them and
   frame each as a proposal the developer can approve in one word.
2. After the answers, ask the decisions that have become possible.
3. Stop when nothing is left open or silently assumed.

## CKAN branches to cover

Skip branches the work does not touch:

- Goal: the problem, the users, and what done looks like.
- Supported CKAN and Python versions: the plan must work across the whole
  range, using APIs present in the oldest version and not removed in the newest.
- Actions: names, inputs, outputs, and existing actions they call or chain.
- Authorization: who may call each action, anonymous access, sysadmin-only parts.
- Validation: schema fields, defaults, and custom validators.
- Data: new tables or columns, migrations, and existing data.
- Interface: API only, or also views, templates, assets, and JavaScript modules.
  Views and CLI stay thin and call actions
  ([thin-wrapper rule](../../../docs/development/index.md#the-feature-development-process)).
- Configuration options and their defaults.
- Side effects: signals, background jobs, emails, and external services.
- Tests per layer: actions, auth, models, views, and CLI; browser tests only
  for complex interactive UI.
- Docker, CI, and packaging changes.
- New extension only: the `ckanext-<name>` package, the plugin interfaces it
  implements, scaffolding with `ckan generate extension`, and packaging, CI,
  and README set up from the start.

## Finish

Summarize the agreed plan: goal, decisions, affected files, and tests. Ask
whether to implement it now; only on a yes, follow the
[shared lifecycle](../ckan-development/references/workflow.md).
