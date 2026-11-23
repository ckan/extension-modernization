---
name: ckan-review
description: Review CKAN extension changes, including staged, unstaged, and relevant untracked work. Use when the developer requests or approves a review, including the one offered by the development workflow; report defects separately from modernization suggestions.
---

# CKAN review

Review only. Never edit, commit, push, publish, run a development lifecycle,
or spawn another reviewer. Technical rules live in the bundled docs.
Resolve their links from the installed skill location, not the target project.

## Establish scope

Read the task requirements, target project path, supported versions, comparison
base, scoped patch/file inventory, and check results supplied by the delegator.
If the user explicitly requests staged-only or another base, honor that scope.
Otherwise review the relevant staged and unstaged changes plus untracked source.
With read-only shell access, use `git status --short`, `git diff --cached`,
`git diff`, and `git ls-files --others --exclude-standard` scoped to the task;
read relevant untracked files separately. These commands do not alter Git state.
Without shell access, require the parent to provide those inputs. Identify
pre-existing unrelated changes separately. Missing inputs limit coverage;
report the gap rather than inventing a baseline or declaring a clean review.

## Examine the changed behavior

Use only the reference-routing portion of
[ckan-development](../ckan-development/SKILL.md#route-the-task) and applicable
topic skills. In reviewer context they supply docs only, without implementation
or review dispatch. Read the needed sections and nearby source, callers, and
tests to establish an actual behavior change.

Check correctness, authorization boundaries, compatibility with the declared
version range, migrations/data integrity where relevant, and meaningful test
coverage. Apply the [CKAN review checklist](references/checklist.md) to the
changed code. Check documentation or packaging changes for correct claims and
resolvable installed references. Verify disputed API behavior against the
applicable version's source. A recommendation in a guide is not by itself proof
of a defect: preserve valid project-specific implementations and focused unit
tests. Formatting belongs to the project's existing tools.

Evaluate check results provided by the parent; report unavailable checks.
Do not run tests that mutate the target's files or services from this reviewer.
Check task acceptance criteria before concluding that the scoped work is complete.

## Report

Return a compact report containing:

- **Scope:** comparison base, included changes, and relevant exclusions.
- **Defects:** severity (high/medium/low), file and line, concrete triggering
  condition, evidence and impact, and a concise suggested resolution. Cite the
  applicable guide/version when a standards or compatibility claim depends on it.
- **Questions:** requirements or assumptions only the developer can settle,
  such as unclear scope or units; not defects. Anything wrong regardless of
  the answer is still a defect.
- **Optional suggestions:** non-blocking modernization choices, only if useful.
- **Checks and limitations:** supplied verification, missing inputs, unsupported
  environments, and any uncertainty that prevents a conclusion.

Say “No defects found in the reviewed scope” when appropriate; do not manufacture
findings. A same-agent pass is self-review, not independent review. Return control
to the delegator/developer without applying fixes or authorizing a commit.
