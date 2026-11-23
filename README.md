# CKAN Extension Guidelines

Version-aware guidance for developing and reviewing CKAN extensions, available
as a [documentation site](https://extension-modernization.readthedocs.io/) and a
shared Codex / Claude Code plugin. Skills load relevant guidance on demand;
the documentation is the source of truth for technical rules and examples.

---

## Install the plugin

Install from this repository's Git-backed marketplace:

```sh
# Codex
codex plugin marketplace add ckan/extension-modernization
codex plugin add extension-modernization@ckan-guidelines

# Claude Code
claude plugin marketplace add ckan/extension-modernization
claude plugin install extension-modernization@ckan-guidelines
```

Start a new session after installing. These commands download the plugin and
register it locally; they do not upload your extension, commit, or push changes.
This repository supplies its own catalog, not an official-store listing.
Using a skill follows your coding agent's existing model and data settings.

To check the installation, run `codex plugin list` (the plugin is listed as
installed) or `claude plugin details extension-modernization@ckan-guidelines`
(eight skills and the `ckan-reviewer` agent).

To share the plugin with your team in Claude Code, add `--scope project` to both
commands and commit the extension's `.claude/settings.json`, which then records
the catalog and the plugin. Codex installs it per developer.

The plugin has two small [hooks](hooks/), active only in CKAN extension
projects. At session start, one reminds the agent to load the matching skill.
Before each shell command, a git guard lets read-only commands such as
`status`, `diff`, and `log` through and holds back commands that change the
repository, such as `commit`, `push`, `reset`, or `checkout`: Claude Code asks
you first, and Codex blocks them so you run them yourself. The hooks read only
folder names and command text, and the plugin has no background services or
network connections. In Codex, trust the hooks in `/hooks`, and again if an
update changes them; Codex warns at startup until you do. The skills and
reviewer are Markdown instructions. In Claude Code their descriptions add about
500 tokens to each session; the guides load only when a task needs them.

### Update or remove

```sh
# Codex: refresh the catalog, then install again
codex plugin marketplace upgrade
codex plugin add extension-modernization@ckan-guidelines

# Claude Code
claude plugin marketplace update ckan-guidelines
claude plugin update extension-modernization@ckan-guidelines
```

Start a new session after updating. To remove the plugin, run
`codex plugin remove extension-modernization@ckan-guidelines` or
`claude plugin uninstall extension-modernization@ckan-guidelines`.

### Rovo Dev

For Rovo Dev pull-request reviews in Bitbucket or GitHub, copy
[`.rovodev/.review-agent.md`](.rovodev/.review-agent.md) into your extension; see
[Rovo Dev code review](docs/agents/index.md#rovo-dev-code-review).

## Use the guidance

Ask naturally: “Add an authenticated action to this CKAN extension.” The
development workflow discovers supported versions, loads matching guides,
runs appropriate checks in the project's own environment (asking which one when
that is unclear), and offers an independent review when it hands off.
Skill selection is model-driven; explicit invocation is also available.

| Skill | Use for |
| --- | --- |
| [ckan-development](.agents/skills/ckan-development/SKILL.md) | Shared development workflow and documentation routing |
| [ckan-plan](.agents/skills/ckan-plan/SKILL.md) | Planning interview before implementation; changes no files |
| [ckan-actions-auth](.agents/skills/ckan-actions-auth/SKILL.md) | Actions, authorization, schemas, validators |
| [ckan-database-models](.agents/skills/ckan-database-models/SKILL.md) | Models, queries, serialization, migrations |
| [ckan-docker-dev](.agents/skills/ckan-docker-dev/SKILL.md) | Docker environments and configuration |
| [ckan-frontend](.agents/skills/ckan-frontend/SKILL.md) | Templates, assets, CSS, JavaScript |
| [ckan-testing](.agents/skills/ckan-testing/SKILL.md) | Tests, fixtures, factories, browser scenarios |
| [ckan-review](.agents/skills/ckan-review/SKILL.md) | Read-only review of a scoped change set |

For example, ask “Use ckan-plan to plan a new ckanext-charts extension”, “Use
ckan-testing to add authorization coverage”, or “Use ckan-review to review my
uncommitted changes.” `ckan-plan` agrees goals and design with you in numbered
rounds and looks facts up itself; it changes nothing until you approve the plan.
In Claude Code, plugin skills also have slash commands such as
`/extension-modernization:ckan-plan`; in Codex, select the installed skill from
the skill picker. Topic-skill calls follow the same workflow.

After each implementation batch, the agent lists the areas it changed and
offers one review, marked recommended when authorization, data writes, models
or migrations, or security-sensitive input changed. The review runs only if you agree: say “and
review it” in your request to skip the question, or “no review” to decline in
advance. The reviewer reports defects separately from open questions and
optional suggestions, and does not edit, commit, or push. Read-only questions and
planning never offer a review. Independent review requires host subagent
support; unavailability is reported explicitly. There is no Git hook or
automatic fix loop.

The plugin works without project instructions. To add standing rules of your
own, such as always reviewing, merge the
[consumer instructions](docs/agents/index.md#project-instructions) into that
extension's existing guidance. Installing the plugin does not rewrite project
instructions or load this repository's contributor files into another project.

## Read the documentation

The guides are best read on the
[documentation site](https://extension-modernization.readthedocs.io/): GitHub
does not render their info boxes and tabs.

- [Get started](docs/index.md): why these guidelines exist and how they ease CKAN upgrades.
- [Agent plugin](docs/agents/index.md): adoption and review workflow.
- [Environment](docs/environment/package-configuration.md): packaging, tools, CI, and Docker.
- [Development](docs/development/index.md): extension interfaces and implementation.
- [Testing](docs/testing/index.md): test layers and isolation.
- [Frontend](docs/frontend/index.md): templates and asset pipelines.

## Contribute

Use Python 3.11 or newer in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
make install
make check
make serve
```

`make serve` previews the site at <http://localhost:8000>; `make help` lists all
commands. Read [AGENTS.md](AGENTS.md) for contributor instructions.

### Where things live

| Path | Contents |
| --- | --- |
| `docs/` | The guides: the source of truth for technical rules and examples |
| `zensical.toml` | Site settings and the navigation menu |
| `.agents/skills/` | The eight skills; they route to the guides instead of copying them |
| `.agents/skills/ckan-review/references/checklist.md` | The CKAN review rules |
| `.rovodev/.review-agent.md` | Rovo copy of the review rules; generated, do not edit |
| `agents/ckan-reviewer.md` | Claude's read-only reviewer agent |
| `hooks/` | The session reminder and git guard for CKAN extension projects |
| `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/` | Plugin manifests and marketplace catalogs |
| `scripts/check.py` | The checks behind `make check` and `make rovo` |

### Common tasks

- **Edit a guide**: preview with `make serve`, then run `make check`.
- **Add a guide page**: also add it to `nav` in `zensical.toml` (`make check`
  fails otherwise), and to the matching skill's reference table if agents
  should use it.
- **Change review rules**: edit `checklist.md`, then run `make rovo` to
  regenerate the Rovo file.
- **Change skills or plugin files**: run `make check`, then follow
  [local testing and validation](docs/agents/testing.md), including its
  behavior scenarios when routing or review changes.
- **Release**: bump `version` in both `plugin.json` files (they must match) and
  add an entry to [CHANGELOG.md](CHANGELOG.md). Claude keeps users on the
  installed version until it changes, so changes without a new version never
  reach them. Users then [update](#update-or-remove).

`make check` validates plugin metadata, skills, local links, Python example
syntax, the generated Rovo file, the site navigation, and the documentation
build. Read the Docs runs it on every push, so a failing check stops the site
from updating.

To try an unpublished checkout, replace `ckan/extension-modernization` in the
marketplace-add command with the absolute path to this repository. See
[local testing and validation](docs/agents/testing.md) before changing an
existing installation.

These guidelines are community-maintained. If you find missing parameters,
outdated configurations, or spelling errors, please submit a pull request or
contact the maintainers.
