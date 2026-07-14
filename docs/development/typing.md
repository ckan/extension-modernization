---
icon: lucide/type
---

# Typing & Static Analysis

CKAN extensions use Python static typing annotations (PEP 484) to prevent
runtime bugs, enforce API contracts, and enable autocompletions in IDEs. This
guide explains how to use CKAN's built-in types, define custom types, and
configure static type checkers like `pyright` and `basedpyright`.

---

## Using CKAN's Built-in Types

CKAN core provides pre-defined type definitions for logic context, action APIs,
validators, and HTTP responses. You can import these directly from
`ckan.types`.

### Common Core Types
* **`Context`**: Types the logic context dictionary passed to action and auth
  functions (containing the DB `session`, `user` identifier, etc.).
* **`Action`**: The type definition for CKAN action functions.
* **`Validator`**: Represents schema validation functions.
* **`ValidatorFactory`**: Represents schema validation factories (like `default()`).
* **`Response`**: Types Flask HTTP response objects returned from views.

### Code Example

```python title="logic/action.py"
from __future__ import annotations

from typing import Any
from ckan import types
import ckan.plugins.toolkit as tk

def myextension_item_show(context: types.Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Retrieve details of an item."""
    # Context is typed, providing safety checks in IDEs
    session = context["session"]
    user = context["user"]

    # ... logic ...
    return {"id": "123", "name": "Item"}
```

---

## Defining Custom Types

To keep typing annotations organized, create a centralized `types.py` module inside your extension package:

```
ckanext-myextension/
└── ckanext/
    └── myextension/
        ├── plugin.py
        └── types.py          # Centralized extension types
```

### A. Literal Types
Use `Literal` to define variables that must match an exact set of string values (unions of string constants):

```python title="types.py"
from typing import Literal

FileOperation = Literal["show", "update", "delete"]
"""Operations that can be performed on a file."""
```

### B. Structural Subtyping (Protocols)
Use `Protocol` (PEP 544) to specify structural requirements (duck-typing) for objects. For example, if a function accepts any stream-like object with a `.read()` method, define it as a Protocol:

```python title="types.py"
from typing import Protocol, Iterator, Any

class PUploadStream(Protocol):
    """Protocol for file-like stream objects."""
    def read(self, size: Any = ..., /) -> bytes: ...
    def __iter__(self) -> Iterator[bytes]: ...
```

You can then annotate parameters with `PUploadStream` without needing those objects to inherit from a common base class:

```python
def save_stream(stream: PUploadStream):
    chunk = stream.read(1024)
    # ... saving logic ...
```

---

## Configuring Pyright & Basedpyright

[Pyright](https://github.com/microsoft/pyright) is Microsoft's static type checker. [Basedpyright](https://github.com/DetachHead/basedpyright) is a popular fork that introduces stricter defaults, CLI enhancements, and extra check rules.

### Configuring in `pyproject.toml`
Configure the type checker inside `pyproject.toml` under `[tool.pyright].

!!! tip "Path Resolution (`extraPaths`)"
    To type-check CKAN core code or other extensions you import, use the `extraPaths` directive to point to the local paths of those packages in your development workspace.

```toml title="pyproject.toml"
[tool.pyright]
pythonVersion = "3.10"
typeCheckingMode = "standard" # Can be "strict" for strict checks

include = ["ckanext"]
exclude = [
    "**/tests*",
    "**/migration",
]

# Resolution paths for external local dependencies
extraPaths = [
    "../ckan",
    "../ckanext-scheming",
]

# Diagnostics Rules
reportMissingImports = true
reportUnusedImport = true
reportUnusedVariable = true
reportOptionalMemberAccess = true
reportDuplicateImport = true
useLibraryCodeForTypes = true
reportMissingTypeStubs = false # Disable stubs warnings if library lacks them
```

### Running Checks
You can run type checks directly from your command line:

```bash
# Using Pyright
npx pyright

# Using Basedpyright
npx basedpyright
```
