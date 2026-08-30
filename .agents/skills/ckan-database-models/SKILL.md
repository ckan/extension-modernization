---
name: ckan-database-models
description: Guide for declaring SQLAlchemy v2 database models, dictize serialization, and isolated Alembic migrations.
---

# CKAN Database Models and Migrations

This skill provides comprehensive instructions on designing database tables, writing type-safe queries, serializing objects, and generating database migrations.

---

## Declaring SQLAlchemy v2 Models

CKAN extensions define database structures using modern, type-safe SQLAlchemy v2 syntax.

### Base Declaration
Inherit from your extension's base class and declare mappings:

```python title="model/item.py"
import sqlalchemy as sa
from sqlalchemy.orm import Mapped
from ckan.lib.dictization import table_dictize
from .base import Base

class MyExtensionItem(Base):
    """SQLAlchemy model for MyExtensionItem."""
    __table__ = sa.Table(
        "myextension_item",
        Base.metadata,
        sa.Column("id", sa.UnicodeText, primary_key=True),
        sa.Column("title", sa.UnicodeText, nullable=False),
        sa.Column("description", sa.UnicodeText),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    id: Mapped[str]
    title: Mapped[str]
    description: Mapped[str | None]
    created_at: Mapped[sa.DateTime]
```

* **Type Safety**: Use PEP 484 annotations with `Mapped[T]` to ensure type check compatibility (Pyright).

---

## Model Serialization (Dictize Method)

To expose model data through CKAN Actions, implement a `dictize` method to serialize database objects to JSON-compatible dictionaries.

* **Avoid Context Pollution**: Do not pass context variables containing DB sessions and user data into the dictization pipeline.
* **Keyword-Only Configuration Parameters**: Declare customization arguments as keyword-only arguments to keep interface boundaries clear:

```python
    def dictize(self, *, include_description: bool = True) -> dict[str, Any]:
        """Serialize database model to dictionary."""
        # Use table_dictize for default database-column mappings
        result = table_dictize(self, {})

        if not include_description:
            result.pop("description", None)

        return result
```

---

## Querying the Database (SQLAlchemy v2 Syntax)

Do not use the legacy `Session.query()` syntax inside modern extensions. Always build queries using `select` and execute them via the database session.

### Querying a Single Object
```python
import sqlalchemy as sa
import ckan.plugins.toolkit as tk

session = context["session"]

# Select item by ID
stmt = sa.select(MyExtensionItem).where(MyExtensionItem.id == item_id)
item = session.scalar(stmt)
```

### Querying Multiple Objects
```python
# Select all active items
stmt = sa.select(MyExtensionItem).order_by(MyExtensionItem.created_at.desc())
items = session.scalars(stmt).all()
```

---

## Database Migrations (Alembic)

Extensions manage database schemas using Alembic. Follow these commands and configuration rules.

### Generating a New Migration File
Run the CLI generator inside the CKAN folder or active development container:

```bash
ckan generate migration -p my_plugin_name -m "Add myextension_item table"
```

This generates a version script inside your extension's `migration/` directory.

### Isolation of Alembic Version Tracking
To prevent conflicts with core CKAN database migrations or other extensions, ensure your extension's `migration/env.py` file isolates its version tracker table:

```python title="migration/env.py"
# Configure Alembic context inside env.py
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    # Isolate version tracking table name
    version_table="myextension_alembic_version",
)
```
