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
from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column
from ckan import model

text = Annotated[str, mapped_column(sa.TEXT)]


@model.registry.mapped_as_dataclass
class MyExtensionItem:
    __table__: ClassVar[sa.Table]
    __tablename__: ClassVar[str] = "myextension_item"

    __table_args__: ClassVar[tuple[Any, ...]] = (
        sa.ForeignKeyConstraint(
            ["id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
    )

    title: Mapped[text]  # (1)!
    owner_id: Mapped[text | None]

    created: Mapped[datetime] = mapped_column(default=sa.func.now())
    id: Mapped[text] = mapped_column(primary_key=True, default=make_uuid)

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

## Querying Models

SQLAlchemy v2 uses the `session.execute` or `session.scalar` syntax. Avoid legacy `session.query` calls:

```python
# Querying a single record by title
stmt = sa.select(MyExtensionItem).where(MyExtensionItem.title == "My Item")
item = session.scalar(stmt)

# Querying multiple records
stmt = sa.select(MyExtensionItem).order_by(MyExtensionItem.created.desc())
items = session.scalars(stmt).all()
```
