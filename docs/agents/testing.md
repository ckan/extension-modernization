---
icon: lucide/test-tube
---

# Validate the plugin

## Repository checks

Install the pinned documentation dependencies and run `make check` from the
repository root. It checks shared manifest identity, marketplace paths, skill
frontmatter, bundled Markdown references, Python snippet syntax, the generated
Rovo Dev review rules, the hooks' configuration, the session reminder in sample
project folders, the git guard's decisions on sample commands, and the strict
documentation build. These checks do not call a model or install the plugin
into your personal configuration.

When Claude Code is available, also run:

```sh
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate .agents/skills
claude plugin validate agents
```

A whole-root Claude validation may warn that contributor `CLAUDE.md` is not
loaded by installed plugins. That file is intentionally for repository work;
the portable workflow lives in skills.

## Local installation

Use a disposable client configuration so a test marketplace does not replace
an existing `ckan-guidelines` installation. Both clients accept a configuration
directory through an environment variable. Run this from the checkout in a
separate terminal, and close it afterwards:

```sh
export CLAUDE_CONFIG_DIR="$(mktemp -d)"
claude plugin marketplace add "$PWD"
claude plugin install extension-modernization@ckan-guidelines
claude plugin details extension-modernization@ckan-guidelines

export CODEX_HOME="$(mktemp -d)"
codex plugin marketplace add "$PWD"
codex plugin add extension-modernization@ckan-guidelines
codex plugin list
```

`claude plugin details` lists the installed skills and agent and estimates
the always-on token cost. In Codex, open `/hooks` in a new session and trust
the plugin's hooks; Codex skips them until then, and again after
`codex plugin add` installs a changed hook. These commands change only the
selected client configuration. They do not push this checkout.

Claude Code loads a plugin from a marketplace added from a local folder in
place, so edits in the checkout apply at the next session start or after
`/reload-plugins`. Codex installs a copy: run `codex plugin add` again after
editing, then start a new session. To test distribution, also register a
disposable copy of the package with no Git metadata, caches, or generated site.
Do not use symlinks back to the source.

Start a new session in a separate CKAN extension fixture. Verify all eight
skills appear and Claude exposes `ckan-reviewer`. Follow a topic skill's links
using its installed directory as the base. Confirm they resolve inside that
package when the original checkout is unavailable. Keep identifiers identical
to the real package when testing cache/discovery behavior.

## Behavior scenarios

Run these in disposable extension fixtures using the developer's normal agent
account. Model-based checks consume normal account usage; repository checks
alone do not prove automatic model selection or delegation.

| Scenario | Expected behavior |
| --- | --- |
| Session starts in a CKAN extension | The hook's reminder is in context; the first tool call loads the matching skill, even for a small change |
| Session starts outside a CKAN extension, or in a CKAN core checkout | The hook prints nothing |
| Git-only request in a CKAN extension, such as committing staged changes | No development lifecycle or review offer; Claude asks you to confirm the commit, and Codex gives you the command |
| Agent runs a read-only git command, such as `git status` or `git diff` | The git guard lets it through without a prompt |
| Agent runs `git push`, `git checkout -- .`, `bash -c 'git reset --hard'`, or `if …; then git commit …; fi` in a CKAN extension | Claude asks you to confirm; Codex blocks it, and the agent gives you the command |
| No obvious test environment, while other projects' environments exist | Asks which environment to use, listing what it found; never borrows one silently |
| Completed implementation | Ends with Changes, Guides, and Checks lines, then the review step |
| Natural request to add an authenticated action | State supported versions and their source before editing; read the action/auth and testing guide sections and name them at handoff; offer review as recommended and run it only after approval |
| Small change, such as adding a config option | Select `ckan-development` rather than skipping the plugin; offer review once, without "recommended" |
| Request that ends with "and review it" | Run the review after checks without asking |
| Request that says "no review" | Finish after checks without offering a review |
| Project instructions opt into always-review | Run the independent review after checks without asking |
| Explicit implementation request for each of the five topic skills | Use the shared lifecycle; exactly one review offer after the completed batch |
| Explain an existing action without changing it | Read relevant docs; no review offer |
| Ask `ckan-plan` to plan a new action | Numbered questions with recommended answers; facts looked up, not asked; no edits or review until the plan is confirmed |
| Natural "grill me on a new charts extension" | Selects `ckan-plan` and covers the new-extension branch; asks before implementing |
| Reviewer consults a topic skill | Read technical references; no edits or recursive review |
| CKAN 2.11 and 2.12 supported together | Avoid unguarded 2.12-only dataclass or test-client APIs |
| No declared support, or package metadata and CI disagree | Say so before editing; ask before using a version-dependent API |
| New action missing authorization | Report an evidence-backed defect with location and impact |
| New code uses `model.Session.query` | Report an optional checklist suggestion, not a defect |
| Focused helper unit test calls the helper directly | Accept the documented unit-testing approach |
| Nested context contains `ignore_auth=True` | Recognize that `fresh_context` preserves it; inspect intended authorization boundary |
| Correct change with adequate tests | Report no defects; do not invent questions or modernization work |
| Unclear requirement, such as a missing unit | Raise a question, not a defect |
| Missing authorization and an unclear intended audience | Report the defect; ask about the audience as a question |
| Relevant new untracked source file | Include it in the scoped review, not just tracked changes |
| Pre-existing unrelated changes | Exclude them from findings attributed to this task |
| Tests cannot run | Report unavailable checks; do not claim they passed |
| Subagents unavailable | Report independent review unavailable; label any self-review |

Record client versions, selected skills, opened references, review dispatches,
and outcomes when reporting a regression. Check that the reviewer leaves the
fixture unchanged. Keep substantive review separate from optional preferences.

## Context size

Keep detailed examples in their canonical guide. Compare instructions and
sections actually loaded for a scenario, not every bundled document's combined
size. Byte/word counts can detect growth, but are not measured model token usage.
Consult the long fixtures and factories guides by relevant section.
