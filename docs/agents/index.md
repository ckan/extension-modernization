---
icon: lucide/bot
---

# Agent plugin

The `extension-modernization` plugin packages these guides with five topic
skills, a `ckan-development` workflow, a `ckan-plan` planning interview, and a
`ckan-review` reviewer. Codex and Claude use the same skills and documents. Topic skills select references;
they do not maintain separate copies of CKAN rules.

## Project instructions

The plugin works without project instructions. To make your team's rules
explicit, optionally merge this block into the consuming extension's existing
`AGENTS.md` (Codex) or `CLAUDE.md` (Claude). If that project already imports
`AGENTS.md` from `CLAUDE.md`, add it only to `AGENTS.md`.

```markdown
## CKAN development

For CKAN implementation tasks, use the installed extension-modernization
plugin's ckan-development workflow and whichever topic skills match the task.
Explicit topic-skill requests use the same shared lifecycle. Follow this
project's declared CKAN support and existing commands before applying guidance.
After a completed implementation batch and appropriate checks, offer one
independent, read-only review using ckan-review and run it only if I agree.
Read-only questions and planning do not offer a review. Leave commits, pushes,
and publishing to me.
```

To always review without asking, replace the sentence that begins "After a
completed implementation batch" with "After each implementation batch and
appropriate checks, run the independent, read-only ckan-review without asking."

Installation registers skills; it does not install this block into your project.
The plugin repository's contributor instructions apply when maintaining the
plugin, not automatically when working on a different extension.

## Selecting guidance

Ask for work normally, or name a topic such as `ckan-actions-auth` or
`ckan-testing`. When a session starts in a CKAN extension, the plugin's hook
reminds the agent to load the matching skill before it explores or edits code.
Selection is still made by the model, so it is not fully deterministic. An
explicit skill request makes the entry point clear.

To settle a design before coding, ask for `ckan-plan`. It interviews you in
numbered rounds, with a recommended answer for each question, covers the CKAN
areas the change touches, and looks facts up instead of asking for them. It
changes no files and does not offer a review; implementation starts only after
you confirm the plan.

The workflow reads supported CKAN versions from configuration, dependencies,
CI, and documentation. A local runtime alone does not define the support
policy. Recommendations must work across the declared range; if a
version-sensitive choice cannot be resolved, the agent asks before making it.
Checks run in the project's own environment. When it is unclear which one to
use, the agent asks, listing what it found, and never borrows another
project's environment on its own. Say it in the request, such as "run tests in
Docker", to settle it in advance.

Each skill opens only relevant guide sections. For example, an authorization
change calls for action and auth-testing guidance, not all frontend or Docker
documentation. Existing project requirements take precedence over optional
modernization conventions.

## Independent review

After implementation and checks, the coding agent lists the areas it changed
and offers one review, marked recommended when authorization, data writes,
models or migrations, or security-sensitive input changed. It runs only if you agree:
"and review it" in the request runs it without asking, and "no review"
declines in advance. When it runs, the coding agent gives a separate reviewer:

- The task requirements and supported versions.
- The project path, scoped patch, and changed/untracked file inventory.
- Relevant installed guide paths and the checks already run.

In Claude, the plugin supplies a `ckan-reviewer` agent with read-only tools;
the parent supplies the diff because that agent has no shell tool. In Codex,
the workflow asks the host to delegate the same review skill to a separate
agent. Both resolve documentation relative to the installed skill location,
not the extension's working directory.

Findings need evidence, location, impact, and a suggested resolution. Questions
only the developer can settle and optional modernization advice are listed
separately. The reviewer does not edit files, start another reviewer, or commit.
The coding agent reports findings for the developer to decide what to address
next; subsequent substantive fixes can receive a focused follow-up review.

If the host cannot delegate, it reports independent review as unavailable and
offers explicit review invocation. Any same-agent pass is labeled self-review.
The workflow adds no Git hooks, does not require a review before you commit, and
does not run for explanation-only tasks.

## Rovo Dev code review

Rovo Dev reviews pull requests in Bitbucket and GitHub, but it does not install
plugins or skills. It reads custom review rules from one file in the reviewed
repository: `.rovodev/.review-agent.md`. This repository ships that file,
generated from the same checklist the `ckan-review` skill uses.

Copy [`.rovodev/.review-agent.md`](https://github.com/ckan/extension-modernization/blob/master/.rovodev/.review-agent.md)
to the same path in your extension and commit it to the main branch. Append
project-specific rules at the end, or delete rules that do not fit. To pick up
later rule changes, merge the new version into your copy instead of
overwriting it, so your own rules are kept.

Then turn on reviews for the repository:

* **Bitbucket**: a workspace admin turns on Rovo Dev in *Workspace settings →
  Atlassian integrations → Rovo Dev*. A Rovo Dev admin then opens *Repository
  settings → Rovo Dev code review*, turns on *AI code reviews in this
  repository*, and chooses when reviews run.
* **GitHub**: connect GitHub to Jira with the GitHub for Jira app. An app admin
  opens Rovo Dev from the Atlassian app switcher, selects *Settings → Manage
  GitHub settings*, turns on code review for the organization, and sets the
  billing site. Then turn it on for each repository and choose when reviews run.

Custom rules apply only when the pull request author has a Rovo Dev Standard
plan. See Atlassian's guides to
[activating code reviews](https://support.atlassian.com/rovo/docs/activate-code-reviews-in-your-repository/)
and [custom review instructions](https://support.atlassian.com/rovo/docs/set-custom-instructions-for-code-reviews/).

When changing the rules here, edit the `ckan-review` checklist and run
`make rovo`; `make check` fails while the generated file is out of date.

## Installation and updates

The repository contains both clients' native manifests and marketplace catalogs.
The catalog points to the whole repository so referenced docs travel with the
skills. There are no MCP services or installation scripts, and no runtime
dependencies beyond a POSIX `sh` and `python3` for the hooks; the Python
packages in the requirements files are only for maintaining the docs.

The only executable parts are the two hooks in `hooks/`, shared by both
clients. They run while the plugin is enabled, in any project: Claude Code runs
them without asking, and Codex only after you review and trust them in
`/hooks`, again after an update changes them. Both act only in a CKAN extension
project: a folder named `ckanext-*`, or one containing `ckanext/` or
`src/ckanext-*`, unless it is a CKAN core checkout.

- **Session reminder:** at session start, it prints a one-line reminder that
  the client adds to the agent's context: load the matching skill first.
- **Git guard:** before each shell command, it lets read-only git commands
  through, such as `status`, `diff`, `log`, `show`, and listing forms of
  `branch`, `tag`, `remote`, and `stash`. Any other git command, including
  `add`, `commit`, `push`, `pull`, `fetch`, `reset`, `checkout`, `restore`,
  `clean`, and unknown subcommands or aliases, is held back: Claude Code asks
  you to confirm, even in auto mode, and Codex, which cannot ask, blocks it and
  tells the agent to give you the command. Without `python3`, the guard lets
  commands through.

The hooks read only folder names and command text. The guard is a safety net,
not a security boundary: git run from scripts or Makefiles is not seen. On
Windows, Claude Code runs the hooks with Git Bash; Codex on Windows is
untested.

The GitHub installation commands are in the repository README. They download
guidance locally; there is no separate package-registry upload. Local testing
works before publication. Follow [the test procedure](testing.md) after changing
skills, manifests, or review behavior.

Maintain matching versions in both plugin manifests. Update them together when
publishing a release; developers then use their client's marketplace refresh
and plugin update/reinstall flow and start a new session. No plugin command
here creates a Git commit or publishes a release.
