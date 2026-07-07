---
icon: lucide/history
---

# Writing Changelogs

Changelogs inform developers, users, and administrators about what has changed
between releases. CKAN extensions automate this process using conventional git
history, though alternative strategies can be used depending on team workflow.

---

## Conventional Commits

The foundation of automated changelogs is **Conventional Commits**. This standardizes commit messages by adding structural prefixes that describe the intent of the changes:

```
<type>(<optional-scope>): <description>

[optional body]
[optional footer(s)]
```

### Common Commit Types
* `feat`: A new feature (translates to **Features** in the changelog).
* `fix`: A bug fix (translates to **Bug Fixes** in the changelog).
* `docs`: Documentation-only changes.
* `refactor`: A code change that neither fixes a bug nor adds a feature.
* `test`: Adding missing tests or correcting existing tests.
* `chore`: Maintainance tasks, dependency updates, or internal tooling changes.

---

## Automated Changelogs with Git Cliff

[Git Cliff](https://git-cliff.org/) parses your Git repository history, filters
out noise, and renders a structured markdown file (`CHANGELOG.md`) using a Tera
template.

### How Git Cliff is Configured (`cliff.toml`)
The `cliff.toml` file at your extension's root controls how commit messages are parsed and grouped.

#### Commit Parsing Rules
The `commit_parsers` section uses regex patterns to categorize commits or skip them entirely:
```toml
commit_parsers = [
    { message = "^feat", group = "<!-- 0 -->🚀 Features" },
    { message = "^fix", group = "<!-- 10 -->🐛 Bug Fixes" },
    { message = "^refactor", group = "<!-- 20 -->🚜 Refactor" },
    { message = "^doc", group = "<!-- 40 -->📚 Documentation" },
    { message = "^test", group = "<!-- 70 -->🧪 Testing" },
    # Skip minor chore/dependency commits
    { message = "^chore\\(deps.*\\)", skip = true },
    { message = ".*", group = "<!-- 90 -->💼 Other" },
]
```

#### The Tera Template
The `[changelog].body` setting defines the Markdown layout of the generated release. It loops over the grouped commits and renders links to GitHub commits:
```jinja
{% if version %}\
    ## [{{ version }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | striptags | trim | upper_first }}
    {% for commit in commits %}
        - {% if commit.scope %}*({{ commit.scope }})* {% endif %}{{ commit.message }} ([{{ commit.id | truncate(length=7, end='') }}](https://github.com/{{ remote.github.owner }}/{{ remote.github.repo }}/commit/{{ commit.id }}))
    {% endfor %}
{% endfor %}
```

### Running Git Cliff
Compile the changelog using the command line:
```bash
git cliff --output CHANGELOG.md
```
Or use a unified `Makefile` target:
```makefile
changelog:  ## Compile release changelog
	git cliff --output CHANGELOG.md $(if $(bump),--tag $(bump))
```

---

## Alternative Changelog Strategies

Automating changelogs via conventional commits requires strict discipline from all contributors. If your team has a noisy commit history or wants to avoid merge conflicts on a single `CHANGELOG.md` file, consider these alternatives:

### Towncrier (News Fragment Files)
[Towncrier](https://github.com/twisted/towncrier) is a popular Python tool that generates changelogs by gathering small text files (news fragments) from a `newsfragments/` directory.

* **How it works**: For every pull request, the developer adds a single-sentence file named after the issue or PR (e.g. `123.feature`, `456.bugfix`). At release time, Towncrier aggregates these fragments into `CHANGELOG.md` and deletes the files.
* **Benefit**: Since developers write separate files, there are **no git merge conflicts** on the main `CHANGELOG.md` file during parallel pull request reviews.

### Release Drafter / GitHub Release Notes
If your development is hosted entirely on GitHub, you can delegate changelog drafting to GitHub Releases.

* **How it works**: Tools like [Release Drafter](https://github.com/release-drafter/release-drafter) automatically categorize pull requests into release notes based on GitHub **labels** (e.g., PRs labeled `enhancement` are added under "Features").
* **Benefit**: No configuration or special commit syntax is required in the repository itself.

### Manual Changelog (Keep a Changelog)
Writing a manual changelog is the most basic strategy, but it is often the cleanest for end-users because it focuses on user-impact rather than code-level commit histories.

* **Format**: Follow the [Keep a Changelog](https://keepachangelog.com/) standard. Categorize changes using six clear subheadings:
  - `Added` (new features).
  - `Changed` (changes in existing functionality).
  - `Deprecated` (soon-to-be-removed features).
  - `Removed` (removed features).
  - `Fixed` (any bug fixes).
  - `Security` (in case of vulnerabilities).

---

## Advanced Scenarios

### Transitioning an Existing Repository to Conventional Commits

If your repository has a long history of non-conventional commit messages, you can transition without rewriting your git history or generating a messy changelog.

#### Option 1: Generate from a Specific Starting Point
You can restrict `git-cliff` to only parse commits from a specific tag or commit onwards by specifying a range:

```bash
# Generate changelog only for commits after version 1.2.0
git-cliff v1.2.0..HEAD --output CHANGELOG.md
```

#### Option 2: Prepend to a Manual Legacy History
1. Create a `CHANGELOG.md` file and manually write the release history for your old versions.
2. When a new release is ready, use the `--prepend` option to add only the new conventional-commit-based release notes at the top:
   ```bash
   git-cliff --latest --prepend CHANGELOG.md
   ```

---

### Preserving Manual Edits to Past Releases

In some cases, you may need to manually edit, correct, or add extra context to past release sections in your `CHANGELOG.md` (for instance, to call out security details or major breaking warnings that were not fully captured in the original commit messages).

If you run a full rebuild (`git-cliff --output CHANGELOG.md`), your manual adjustments will be overwritten.

#### The Solution: Partial Prepends
Instead of rebuilding the entire file, configure your build system to only generate and prepend the new release block.

* **Prepend Latest Release**: When a new tag is released, run:
  ```bash
  git-cliff --latest --prepend CHANGELOG.md
  ```
  This command parses only the commits belonging to the latest tag, removes the old file header, prepends the new release block, and retains the entire rest of the `CHANGELOG.md` exactly as it was.
* **Prepend Unreleased Changes**: In development mode, to preview unreleased notes at the top without affecting the historical log:
  ```bash
  git-cliff --unreleased --prepend CHANGELOG.md
  ```
