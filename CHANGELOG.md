# Changelog

All notable changes to this repository are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/), and plugin versions
follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - Unreleased

### Added

- Codex and Claude Code plugin `extension-modernization`, installable from the
  `ckan-guidelines` marketplace in this repository.
- Five topic skills (`ckan-actions-auth`, `ckan-database-models`,
  `ckan-docker-dev`, `ckan-frontend`, `ckan-testing`), the `ckan-development`
  workflow, and the `ckan-review` reviewer with a CKAN review checklist. After
  each implementation batch the workflow offers one review, marked recommended
  for authorization, data, model or migration, or security changes, and runs it
  only on approval.
- `ckan-plan` skill: a planning interview that settles the design of a CKAN
  change in numbered rounds before any code is written.
- The workflow states the supported CKAN versions before editing, reads the
  matching guides first, asks which environment to run checks in when that is
  unclear, and closes with a Changes, Guides, and Checks summary.
- Two hooks for Claude Code and Codex, active only in CKAN extension projects:
  a session-start reminder to load the matching skill, even for small changes,
  and a git guard that lets read-only git commands through and holds back the
  rest (Claude Code asks first; Codex blocks them).
- A `ckan-reviewer` agent for Claude Code that runs the review in a separate,
  read-only context (Codex uses its built-in subagents).
- Agent plugin guide and validation scenarios in the documentation.
- `make check`, which validates plugin files, skills, links, Python example
  syntax, and the documentation build, with pinned documentation dependencies.

### Changed

- The Rovo review rules in `.rovodev/.review-agent.md` are now generated from
  the shared review checklist with `make rovo`, corrected for CKAN versions.
- Read the Docs runs `make check` before publishing the site.

### Removed

- `agent.md`: its rules and examples now live in the documentation and the
  plugin skills. Install the plugin, or read `AGENTS.md` to work on this
  repository.

### Fixed

- Documentation claims and examples verified against CKAN 2.10, 2.11, and 2.12
  sources, including:
  - `fresh_context` keeps `ignore_auth`, so it is not an authorization reset.
  - Signal senders and payloads for `user_created`, `failed_login`, and
    `action_succeeded`.
  - The `navl_validate` argument order.
  - `call_action` skips authorization checks by default.
  - CKAN 2.12-only test helpers are marked.
  - Docker images read `CKAN__PLUGINS`.
- Broken code examples, imports, links, and typos across the guides.
