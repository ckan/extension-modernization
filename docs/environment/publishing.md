---
icon: lucide/upload-cloud
---

# Publishing Versions

To make a CKAN extension available to downstream deployments, it should be published as a Python package. This guide covers the importance of publishing to PyPI, tag naming conventions, and automated vs. manual publishing workflows.

---

## Why Publish to PyPI?

While Python packages can be installed directly from Git URLs (e.g., `pip install git+https://...`), publishing your extension to PyPI (or a private package index) is highly recommended for production environments:

* **Reliable & Fast Installations**: Installing packages from PyPI is significantly faster than checking out full Git histories.
* **Dependency Resolution**: Package managers (like `pip` or `pip-tools`) can only resolve dependency trees properly if they can read static metadata from a package index.
* **Stability**: A published version is immutable. Git branches and tags can be modified, deleted, or force-pushed, which risks breaking deployments.

!!! note "Soft Dependencies Reminder"
    As discussed in the [Requirements Management Guide](requirements.md), always specify unversioned or soft dependencies in `pyproject.toml`. The strict pinned versions are kept in `requirements.txt` for deployments and do not pollute the published PyPI package metadata.

---

## Git Tag Naming Conventions

Select a tag naming convention and stay consistent. Popular conventions include:

* **`X.Y.Z` (e.g. `1.3.2`)**: The raw version number. This is recommended because it matches the version string in `pyproject.toml` exactly, simplifying validation scripts in CI.
* **`vX.Y.Z` (e.g. `v1.3.2`)**: Preceded by a `v`. Very common in Git platforms, though scripts will need to strip the `v` when comparing with `pyproject.toml`.
* **`release-X.Y.Z` (e.g. `release-1.3.2`)**: Explicit prefix, useful if the repository contains multiple packages or tags are shared.

---

## Automated Publishing via GitHub Actions

Extensions automate publishing to PyPI using GitHub Actions triggered by Git tags.

### Trusted Publishers (OIDC)
Instead of storing sensitive PyPI passwords or API tokens in GitHub Repository
Secrets, modern workflows use **Trusted Publishers**. PyPI verifies the
identity of the GitHub Actions runner using OpenID Connect (OIDC). This
requires setting `#!yaml permissions: {id-token: write}` on the publishing job.

### Workflow Example

```yaml title=".github/workflows/publish.yml"
name: Publish to PyPI
on:
  push:
    tags:
      - '*.*.*' # Triggers on semantic version tags (e.g. 1.0.2)

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      # Verify that the git tag version matches the pyproject.toml version
      - name: Validate version match
        run: |
          TAG_VALUE=${GITHUB_REF/refs\/tags\//}
          TOML_VERSION=$(grep -E '\bversion\s?=\s?"[^"]+"' pyproject.toml | awk -F '"' '{print $2}')
          if [ "$TAG_VALUE" != "$TOML_VERSION" ]; then
            echo "Version mismatch: Tag is [$TAG_VALUE], but pyproject.toml is [$TOML_VERSION]"
            exit 1
          fi

  publish:
    needs: validate
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # MANDATORY for Trusted Publishing (OIDC)
    steps:
      - uses: actions/checkout@v7
      - name: Build package
        run: |
          pip install build
          python -m build # Generates dist/ source and wheel files

      - name: Publish distributions to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

---

## Manual Publishing via Twine (Fallback)

If you are not using GitHub Actions (or are publishing to a private repository that does not support OIDC), you can publish packages manually from your terminal using `twine`.

### Manual Build & Upload Steps

```bash
# 1. Install packaging tools
pip install build twine

# 2. Build the source distribution and wheel
python -m build

# 3. Upload built packages in dist/ to PyPI
twine upload dist/*
```

---

## Comparison: GitHub Actions vs. Local Twine

| Feature                | GitHub Actions (OIDC)                          | Local Twine Command                           |
|:-----------------------|:-----------------------------------------------|:----------------------------------------------|
| **Authentication**     | Secure OIDC token (no password stored)         | Requires API token or password                |
| **Clean Workspace**    | Guaranteed (fresh checkout container)          | Risk of uploading untracked/dirty local files |
| **Version Validation** | Automated (fails if tag and metadata mismatch) | Manual check (easy to misalign tag/package)   |
| **Test Enforcement**   | Enforces test suite runs prior to build        | Depends on developer remembering to run tests |
