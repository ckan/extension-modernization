---
icon: lucide/terminal
---

# CLI Commands

CKAN extensions implement CLI commands using **Click**. These commands are
exposed via the `ckan` command-line utility, enabling administrative workflows,
migrations, and stats queries.

---

## Directory Structure

Place CLI implementations under a `cli.py` module or a `cli/` package:

```
ckanext-myextension/
├── ckanext/
│   └── myextension/
│       ├── plugin.py
│       └── cli/
│           ├── __init__.py      # Root CLI group
│           ├── dev.py           # Developer scripts
│           └── sync.py          # Data sync commands
```

---

## Defining Click Commands

Define a parent Click group inside `cli/__init__.py` and bind sub-commands or sub-groups:

```python title="cli/__init__.py"
from __future__ import annotations

import click
from . import dev, sync

# declare exported members for `cli` blanket. Without `__all__`
# it will register every public function in a module as a CLI command.
__all__ = ["myextension_group"]

# 1. Define the parent CLI entrypoint command group
@click.group("myextension", short_help="ckanext-myextension CLI commands")
def myextension_group():
    """Group of administrative commands for ckanext-myextension."""
    pass

# 2. Add sub-groups/commands
myextension_group.add_command(dev.group, "dev")
myextension_group.add_command(sync.group, "sync")

# 3. Add single commands directly
@myextension_group.command()
@click.option("-n", "--name", help="Name to greet")
def greet(name: str | None):
    """Simple test command."""
    click.echo(f"Hello {name or 'World'}!")
```

---

## Creating Sub-Commands

Create individual sub-commands/groups in their respective submodules:

```python title="cli/sync.py"
from __future__ import annotations

import click
import ckan.plugins.toolkit as tk

@click.group("sync", short_help="Synchronize datasets")
def group():
    pass

@group.command("run")
@click.option("--force", is_flag=True, help="Force sync")
def run_sync(force: bool):
    """Run data synchronization pipeline."""
    # Run CKAN actions using standard context
    context = {"ignore_auth": True}
    tk.get_action("myextension_item_sync")(context, {"force": force})
    click.secho("Sync completed successfully!", fg="green")
```

---

## Auto-Registration

In modern CKAN, extensions register CLI commands by applying the `@tk.blanket.cli` decorator to the plugin class in `plugin.py`.

```python title="plugin.py"
import ckan.plugins as p
import ckan.plugins.toolkit as tk

@tk.blanket.cli   # (1)
class MyExtensionPlugin(p.SingletonPlugin):
    pass
```

1. The blanket decorator automatically discovers and registers all click groups
   exported in the extension's `cli` submodule under the `ckan` namespace
   (making them executable as `ckan myextension ...`).
