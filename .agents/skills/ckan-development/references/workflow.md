# Shared development lifecycle

This lifecycle is shared by the development and five topic skills. Apply it
once per implementation task; loading another topic adds references, not a
second lifecycle. In review context, read technical guidance only. Questions,
planning, and other read-only work stop after answering: they do not offer a review.

## 1. Establish constraints

Read the target project's instructions and relevant configuration. Record the
requested behavior and an initial inventory of staged, unstaged, and untracked
changes so unrelated work is distinguishable. Use declared dependencies,
package metadata, CI matrices, and project docs to establish the supported
CKAN/Python/dependency range and actual test/build commands. A local installed
version is evidence about this environment, not the project's support policy.
Before editing, state the range and its source in one line, for example
"Supported: CKAN 2.11 and 2.12 (CI matrix)", or say that support is missing
or contradictory.

Preserve compatibility across the declared range: use APIs present in the
oldest supported version and not removed in the newest. Verify
version-sensitive guidance against the applicable source or official docs.
If support is missing or contradictory and affects the implementation, ask
before introducing a version-dependent API; continue independent work meanwhile.
Existing project requirements take precedence over optional guide conventions.

## 2. Select and implement

Follow the explicitly selected topic, or use the
[development routing table](../SKILL.md#route-the-task). Before editing, read
the relevant sections of the linked guides, including the testing guidance for
changed behavior. Resolve links relative to each installed Markdown file.

Implement the requested scope, preserving pre-existing work. Use the detected
project tools and environment. Treat named Docker/build recipes as conditional
on the actual workspace. Keep detailed technical rules in the guides rather
than copying them into project instructions or skills.

## 3. Check the result

Run the existing checks appropriate to the change and meaningful affected tests
in this project's own environment, such as its Docker setup, virtualenv, or
documented commands. If it is unclear which environment to use, ask before
running checks: list the candidates you found and the option of leaving checks
to the developer, and reuse the answer for the session. Never borrow another
project's environment without asking. Record commands, outcomes, and anything
unavailable. Do not claim a skipped check passed. Prepare the final scoped
staged and unstaged patches and relevant untracked contents; identify
unrelated pre-existing work separately.

## 4. Hand off and offer a review

Close with this summary, followed by the review step below:

- **Changes:** what changed, and where.
- **Guides:** the guide sections used, and any departure from them to follow
  an existing project pattern.
- **Checks:** the commands run and their results, or why checks could not run.

If the request or the project's instructions already settle the review, follow
them: run it right away when they ask for one ("and review it"), and do not
offer it when they decline ("no review").

Otherwise, end by offering one independent review: list the areas the change
touched and ask whether to run [ckan-review](../../ckan-review/SKILL.md). Mark
the offer recommended when the change touched authorization, data writes,
models or migrations, or security-sensitive input, for example: "Changes
touch: actions, auth. Run ckan-review on these changes? (recommended)". If
this host cannot start a separate reviewer, say so in the offer. Then wait for
the answer.

Offer it once per implementation batch, never after each file write or for
every loaded topic. Leave commits, pushes, and publishing to the developer.

## 5. Run the review on approval

Delegate the review to a separate read-only agent: Claude's installed
`ckan-reviewer` adapter when available, or Codex/the host's native subagent
mechanism. The delegator supplies:

- The task requirements, target project path, and declared supported versions.
- The scoped patch and changed-file inventory, including relevant untracked
  source; identify the comparison base and pre-existing unrelated changes.
- Relevant guide paths, and, unless using Claude's adapter (which locates
  its skill itself), the absolute path to the installed review skill.
- Check commands/results and known limitations.

Pass these inputs, not the full conversation. Claude's adapter has no shell;
provide the patch and check results explicitly. The reviewer remains read-only
and returns findings; it never runs this lifecycle or delegates another reviewer.

Report defects, questions, and optional suggestions separately for the
developer's decision; do not start an automatic fix loop. If delegation is
unavailable, say so and offer explicit `ckan-review` invocation in a separate
session; label any same-agent pass self-review. If substantive fixes follow,
check them and offer a focused review of the updated diff.
