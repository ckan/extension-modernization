---
icon: lucide/database-backup
---

# Database Models

CKAN extensions declare database models using SQLAlchemy v2 style. This
approach combines classical `Table` declarations with modern type annotations
(`Mapped[T]`) for full compatibility with IDE autocompletions and type-checkers
like Pyright.

---

## Setting Up the Base Model

All extension models must inherit from CKAN's database metadata base. Import this base from the toolkit:

```python title="model/base.py"
from __future__ import annotations

import ckan.plugins.toolkit as tk

# Base is CKAN's core declarative BaseModel
Base = tk.BaseModel
```

---

## Defining Typed Models

A model definition should consist of:

1. A physical table definition bound to `Base.metadata`.
2. PEP 484 type annotations using `Mapped` to define Python attribute types.
3. Relationship definitions to other models.

```python title="model/item.py"
from __future__ import annotations

from datetime import datetime
from typing import Any
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship
from ckan.model.types import make_uuid
from ckan.lib.dictization import table_dictize

from .base import Base

class MyExtensionItem(Base):
    """DB Model for extension items."""

    # 1. Physical Table definition
    __table__ = sa.Table(
        "myextension_item",
        Base.metadata,
        sa.Column("id", sa.UnicodeText, primary_key=True, default=make_uuid),
        sa.Column("title", sa.UnicodeText, nullable=False),
        sa.Column("created", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("owner_id", sa.UnicodeText, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=True),
    )

    # 2. PEP 484 Type Annotations for Pyright / IDEs
    id: Mapped[str]
    title: Mapped[str]
    created: Mapped[datetime]
    owner_id: Mapped[str | None]

    # 3. Model Relationships
    owner: Mapped[Any] = relationship(  # (1)!
        "User",
        primaryjoin="MyExtensionItem.owner_id == User.id",
        backref="myextension_items",
        lazy="joined",
    )

    def dictize(self) -> dict[str, Any]: # (2)!
        return table_dictize(self, {})

```

1. Standard SQLAlchemy relationships are declared using `Mapped[Type]` and the `relationship()` constructor.
2. Include `dictize` method that can be used by API to transform object into JSON compatible dictionary.


/// note

The definition above is compatible with SQLAlchemy v1 used by CKAN v2.11.

If you know that you'll be working with CKAN v2.12 and newer, you can use more
modern, SQLAlchemy v2 definition of model, that relies on dataclasses.

```python title="model/item.py"
from datetime import datetime
from typing import Annotated, Any, ClassVar
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship
from ckan import model
from ckan.model.types import make_uuid
from ckan.lib.dictization import table_dictize

text = Annotated[str, mapped_column(sa.TEXT)]


@model.registry.mapped_as_dataclass
class MyExtensionItem:
    __table__: ClassVar[sa.Table]
    __tablename__: ClassVar[str] = "myextension_item"

    __table_args__: ClassVar[tuple[Any, ...]] = (
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
    )

    title: Mapped[text]  # (1)!
    owner_id: Mapped[text | None]

    created: Mapped[datetime] = mapped_column(default=sa.func.now())
    id: Mapped[text] = mapped_column(primary_key=True, default_factory=make_uuid)

    owner: Mapped[model.User] = relationship(
        model.User,
        lazy="joined",
        backref=backref("items"),
        init=False, # (2)!
        compare=False,
    )

    def dictize(self) -> dict[str, Any]:
        return table_dictize(self, {})
```

1. Put columns without default value before columns with default value
2. `init=False` removes this column from constructor. We need it flag, as we
   are defining dataclass model.

///

---

## Model Dictization

API actions in CKAN must return JSON-serializable dictionaries rather than
database-bound SQLAlchemy objects. Because of this, every database model should
define a `dictize` method to convert object records into flat Python
dictionaries.

For simple models, start by importing and calling CKAN's core `table_dictize`
utility. It automatically converts core SQLAlchemy table columns into basic
Python datatypes.

/// admonition | `table_dictize`
    type: example

```python
from ckan.lib.dictization import table_dictize

def dictize(self) -> dict[str, Any]:
    # Pass an empty context dictionary since table_dictize only
    # requires it for compatibility
    return table_dictize(self, {})
```

///



If your model contains related tables (e.g. references to owner user profiles)
or computed attributes that need to be exposed in the dictionary, extend the
return dictionary of `table_dictize` directly:

/// admonition | Extending Dictization Outputs
    type: example

```python
def dictize(self) -> dict[str, Any]:
    # Start with the standard column dictionary
    result = table_dictize(self, {})

    # Extend it with related field attributes
    if self.owner:
        result["owner_name"] = self.owner.name

    return result
```

///


/// admonition | Configuration Options via Keyword-Only Parameters
    type: note

You might want to configure the level of detail returned by your `dictize` method (for example, to include or exclude a list of related items to save performance).

**The Antipattern**: Avoid passing the entire CKAN `context` dictionary (which is polluted with database sessions, authorization details, and caching keys) to control serialization detail.

**The Solution**: Declare **keyword-only parameters** directly in the `dictize` method signature. This defines clear, type-checked parameters:

```python
from typing import Any
from ckan.lib.dictization import table_dictize

class MyExtensionItem(Base):
    # ... columns and attributes ...

    def dictize(self, *, include_owner_details: bool = False) -> dict[str, Any]:
        """Convert the database record to a serialized dictionary."""
        result = table_dictize(self, {})

        # Explicitly check keyword-only parameter configuration
        if include_owner_details and self.owner:
            result["owner"] = {
                "id": self.owner.id,
                "name": self.owner.name,
                "email": self.owner.email,
            }

        return result
```

///


---

## Querying Models

SQLAlchemy v2 uses the `session.execute` or `session.scalar` syntax. Avoid legacy `session.query` calls:

```python
# Querying a single record by title
stmt = sa.select(MyExtensionItem).where(MyExtensionItem.title == "My Item")
item = session.scalar(stmt)

# Querying multiple records
stmt = sa.select(MyExtensionItem).order_by(MyExtensionItem.created.desc())
items = session.scalars(stmt)

# Remove records
stmt = sa.delete(MyExtensionItem).where(MyExtensionItem.title == "My Item")
items = session.execute(stmt)
session.commit()


```
