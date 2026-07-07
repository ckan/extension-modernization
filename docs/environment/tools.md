---
icon: lucide/boxes
---

# Development tools

CKAN extensions leverage several standard Python tools to enforce code
quality, manage tests, run static analysis, and automate release
notes. Configuring these tools directly in `pyproject.toml` (or tool-specific
config files like `cliff.toml`) centralizes configuration and makes it
reproducible.

---

### Ruff

[Ruff](https://astral.sh/ruff) is an extremely fast Python linter and code
formatter written in Rust. It replaces a suite of legacy tools (e.g., `flake8`,
`isort`, `black`, `pyup`, `autoflake`).


/// admonition | Configuration Example
    type: example

```toml title="pyproject.toml"
[tool.ruff]
target-version = "py310" # minimal required version of python interpreter
line-length = 120        # modern screens usually have enough space for 120 characters

[tool.ruff.lint]
select = [
    "ANN0", # Enforce type annotations for function arguments
    "B",    # Catch design/bug problems (flake8-bugbear)
    "C4",   # Optimize list/set/dict comprehensions
    "C90",  # McCabe complexity check
    "E",    # Pycodestyle error reports
    "W",    # Pycodestyle warning reports
    "F",    # Pyflakes validation
    "I",    # Isort (import sorting)
    "N",    # Naming conventions (PEP 8)
    "PL",   # Pylint rules
    "S",    # Bandit security tests
    "UP",   # Upgrade python syntax rules
]
ignore = [
    "RET503",   # Allow implicit return None
    "E712",     # Allow boolean comparison (SQLAlchemy query requirement)
    "PLC1901",  # Allow empty string comparison (SQLAlchemy query requirement)
]

[tool.ruff.lint.per-file-ignores]
# Ignore strict checking/security linting in test files
"ckanext/myextension/tests/*" = ["S", "PL", "ANN"]

[tool.ruff.lint.flake8-import-conventions.aliases]
# Standard CKAN shorthand aliases
"ckan.plugins" = "p"
"ckan.plugins.toolkit" = "tk"
# this perfectly combines with query builder `sa.select(sa.func.cout(...))...`
sqlalchemy = "sa"

[tool.ruff.lint.isort]
# Organize imports so standard libs, ckan, ckanext, and your extension are grouped separately
section-order = [
    "future",            # from __future__ import annotations
    "standard-library",  # import os
    "third-party",       # import flask
    "ckan",              # import ckan
    "ckanext",           # import ckanext.anything_else
    "self",              # import ckanext.myext
    "local-folder",      # from . import
]

[tool.ruff.lint.isort.sections]
# definitions for custom sections
ckan = ["ckan"]
ckanext = ["ckanext"]
self = ["ckanext.myextension"]
```

///

---

### Pyright

[Pyright](https://github.com/microsoft/pyright) is a high-performance static
type checker for Python. It checks code correctness and types without executing
Python code.

/// admonition | Configuration Example
    type: example

```toml title="pyproject.toml"
[tool.pyright]
pythonVersion = "3.10"
include = ["ckanext"]
exclude = [
    "**/tests*",  # I recommend typed tests, but it may require a lot of work
    "**/migration",
]

# Paths to external dependency repositories for resolution when developing locally
extraPaths = [
    "../ckan",
    "../ckanext-scheming",
]

# Error severity controls. Prefer the strictest settings possible for the project.
reportFunctionMemberAccess = true # non-standard member accesses for functions
reportMissingImports = true
reportMissingModuleSource = true
reportMissingTypeStubs = false
reportImportCycles = true
reportUnusedImport = true
reportUnusedClass = true
reportUnusedFunction = true
reportUnusedVariable = true
reportDuplicateImport = true
reportOptionalSubscript = true
reportOptionalMemberAccess = true
reportOptionalCall = true
reportOptionalIterable = true
reportOptionalContextManager = true
reportOptionalOperand = true
reportTypedDictNotRequiredAccess = false # Context won't work with this rule
reportConstantRedefinition = true
reportIncompatibleMethodOverride = true
reportIncompatibleVariableOverride = true
reportOverlappingOverload = true
reportUntypedFunctionDecorator = false
reportUnknownParameterType = true
reportUnknownArgumentType = false
reportUnknownLambdaType = false
reportUnknownMemberType = false
reportMissingTypeArgument = true
reportInvalidTypeVarUse = true
reportCallInDefaultInitializer = true
reportUnknownVariableType = true
reportUntypedBaseClass = true
reportUnnecessaryIsInstance = true
reportUnnecessaryCast = true
reportUnnecessaryComparison = true
reportAssertAlwaysTrue = true
reportSelfClsParameterName = true
reportUnusedCallResult = false # allow function calls for side-effect only
useLibraryCodeForTypes = true
reportGeneralTypeIssues = true
reportPropertyTypeMismatch = true
reportWildcardImportFromLibrary = true
reportUntypedClassDecorator = false
reportUntypedNamedTuple = true
reportPrivateUsage = true
reportPrivateImportUsage = true
reportInconsistentConstructor = true
reportMissingSuperCall = false
reportUninitializedInstanceVariable = true
reportInvalidStringEscapeSequence = true
reportMissingParameterType = true
reportImplicitStringConcatenation = false
reportUndefinedVariable = true
reportUnboundVariable = true
reportInvalidStubStatement = true
reportIncompleteStub = true
reportUnsupportedDunderAll = true
reportUnusedCoroutine = true
reportUnnecessaryTypeIgnoreComment = true
reportMatchNotExhaustive = true
reportAny = false
reportExplicitAny = false
```

///

---

### Pytest

[Pytest](https://docs.pytest.org/) is the standard testing framework for Python
projects. CKAN extensions run tests via Pytest using the `pytest-ckan` plugin.

/// admonition | Configuration Example
    type: example

```toml title="pyproject.toml"
[tool.pytest.ini_options]
# Automatically supply --ckan-ini flag to pytest to initialize CKAN context
# disable e2e tests by default as they may require dedicated application instance running
addopts = "--ckan-ini test.ini -m 'not e2e'"
testpaths = ["ckanext/myextension/tests"]
```

///

---

### Coverage

The `coverage` tool measures what percentage of your code is executed during test runs.

/// admonition | Configuration Example
    type: example

```toml title="pyproject.toml"
[tool.coverage.run]
branch = true                          # Track branch execution (e.g. if-else coverage)
omit = ["ckanext/myextension/tests/*"] # Exclude test files from coverage statistics
source = ["ckanext/myextension"]       # With this option you can simply add `--cov` to pytest

```

///

---

### Git Cliff

[Git Cliff](https://git-cliff.org/) is a tool that parses conventional Git commit history to generate a structured and beautiful changelog file automatically.

/// admonition | Configuration Example
    type: example

Git Cliff is usually configured via a `cliff.toml` file in the root of the project.

```toml title="cliff.toml"
[changelog]
# Tera template to format release notes
body = """
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
"""
trim = true

[git]
# Enforce Conventional Commit standards when sorting changelog entries
conventional_commits = true
filter_unconventional = true

commit_parsers = [
    { message = "^feat", group = "<!-- 0 -->🚀 Features" },
    { message = "^fix", group = "<!-- 10 -->🐛 Bug Fixes" },
    { message = "^refactor", group = "<!-- 20 -->🚜 Refactor" },
    { message = "^doc", group = "<!-- 40 -->📚 Documentation" },
    { message = "^perf", group = "<!-- 50 -->⚡ Performance" },
    { message = "^test", group = "<!-- 70 -->🧪 Testing" },
    { message = ".*", group = "<!-- 90 -->💼 Other" },
]

[remote.github]
owner = "MyGithubOrg"
repo = "ckanext-myextension"
```

///

---

### Makefile

A `Makefile` is used to define shorthand commands for complex, multi-step
terminal operations. This ensures that all developers and CI/CD pipelines run
tasks—such as launching test servers, compiling assets, and generating
changelogs—with the exact same parameters.

/// admonition | Configuration Example
    type: example

```makefile title="Makefile"
.DEFAULT_GOAL := help
.PHONY: help

help:  ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

changelog:  ## Compile release changelog, `... bump=v0.2.0` to specify version
	git cliff --output CHANGELOG.md $(if $(bump),--tag $(bump))

test-config = test.ini

test-server:  ## Reset DB, run migrations, create admin user, and start flask server
	yes | ckan -c $(test-config) db clean
	ckan -c $(test-config) db upgrade
	yes | ckan -c$(test-config) sysadmin add admin password=password123 email=admin@test.net
	ckan -c $(test-config) run -t
```
///
