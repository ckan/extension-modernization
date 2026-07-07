---
icon: lucide/box
---

# Managing Dependencies

CKAN extensions function as library packages within a larger CKAN
deployment. Extensions separate **library dependency definitions** (flexible
metadata) from **application deployments** (fully reproducible environments).


---

## Defining Dependencies in `pyproject.toml`

The `pyproject.toml` file declares what packages your extension needs to run. These declarations should remain as flexible as possible to prevent package resolution conflicts when your extension is installed alongside others.

### Rules for `pyproject.toml`
* **Omit version bounds**: List dependencies without versions (e.g. `requests`, `pandas`) by default.
* **Specify minimal versions only when necessary**: Define a lower bound (e.g., `requests>=2.31.0`) *only* if your extension depends on features introduced in that version and will break with older versions.
* **Never specify top bounds**: Avoid upper-bound limits (e.g., `<3.0.0` or `!=1.4.*`). Upper bounds lock users out of system-wide upgrades and trigger dependency resolution failures in multi-extension deployments.
* **Use optional dependencies**: Group test, documentation, and development dependencies using `[project.optional-dependencies]`.

### Example Configuration

```toml title="pyproject.toml"
[project]
name = "ckanext-myextension"
dependencies = [
    "requests",              # (1)
    "typing_extensions>=4.0", # (2)
]

[project.optional-dependencies]
# Dependencies required for running tests
test = [
    "pytest-ckan",
    "pytest-cov",
]
# Dependencies required for local development
dev = [
    "pytest-ckan",
    "pytest-cov",
    "zensical",
    "pre-commit",
]
```

1. Flexible, unversioned dependency allowing the installer to resolve any compatible version.
2. Minimal version specified because the extension relies on type annotations introduced in version `4.0`.

---

## Reproducible Builds (`requirements.txt`)

While unversioned dependencies in `pyproject.toml` provide maximum flexibility,
they do not guarantee reproducible environments. To provide a predictable,
guaranteed installation for production, staging, and developers, use pinned
requirements files.

### Pinned Requirements Files

Create `requirements.txt` and `dev-requirements.txt` files at the root of your
extension containing the **exact, fully pinned versions** of all packages:

```txt title="requirements.txt"
# Pinned core extension dependencies
requests==2.31.0
typing-extensions==4.9.0
```

```txt title="dev-requirements.txt"
# Pinned development-only dependencies
-r requirements.txt
pytest-ckan==0.3.1
pytest-cov==4.1.0
zensical==0.2.4
pre-commit==3.6.0
```

### Known Version Issues
If you discover that your extension has a known compatibility issue with a new release of a dependency:

1. **Do not** add an upper bound to `pyproject.toml`.
2. **Do** pin the last working version in `requirements.txt`.

This ensures standard automated deployments remain functional and stable, while
still allowing developers to override the pin in their deployment environments
if they need to test or apply custom fixes.

/// tip

It may be not so convenient to use `requirements.txt` when publishing package
to PyPI. Consider adding an extras group to the package with stable/pinned
dependencies.

```toml title="pyproject.toml"
[project]
name = "ckanext-myextension"
dependencies = [
    "requests",
    "typing_extensions>=4.0",
]
dynamic = ["optional-dependencies"]

[tool.setuptools.dynamic]
optional-dependencies = {
    stable = { file = ["requirements.txt"] },
}
```

///

---

## Installation Workflows

Using this setup, developers and users have two ways to install the extension depending on their needs.

### A. Reproducible/Guaranteed Installation

Use this workflow in CI/CD pipelines, production servers, and local development
environments to ensure everyone runs the identical package set:

```bash
# Install exact pinned versions
pip install -r requirements.txt

# Install the extension in editable mode without resolving new dependency versions
pip install --no-deps -e .
```

### B. Flexible Library Installation
For users integrating your extension into an existing platform with pre-resolved versions, they can let pip resolve dependencies automatically:

```bash
pip install -e .
```
