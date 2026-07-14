---
icon: lucide/terminal-square
---

# CLI Commands

CKAN extensions define command-line interfaces using the **Click** framework. Testing CLI commands ensures they process arguments, execute operations, and print the expected output to the stdout stream.

CKAN recommends using the pre-configured `cli` fixture to execute commands in the test context.

---

## Using the CKAN `cli` Fixture

Use CKAN's `cli` fixture (an instance of `ckan.tests.helpers.CKANCliRunner`) to
invoke CLI commands. This runner is pre-configured to automatically load
environment settings (like the test configuration file `CKAN_INI`).

```python title="tests/test_cli.py"
from __future__ import annotations

import pytest
from ckanext.myextension.cli import myextension_command

@pytest.mark.usefixtures("with_plugins")
class TestCliCommands:

    def test_command_execution_success(self, cli: CKANCliRunner):
        """Verify the command runs successfully and prints output."""
        # 1. Invoke the imported Click command directly via the 'cli' fixture
        result = cli.invoke(myextension_command, ["--name", "test-item"])

        # 2. Assert exit code is 0 (success)
        assert result.exit_code == 0

        # 3. Check console stdout print contents
        assert "Successfully created item test-item" in result.output

    def test_command_missing_arguments(self, cli: CKANCliRunner):
        """Verify the command exits with error code when arguments are missing."""
        # Invoke without mandatory name argument
        result = cli.invoke(myextension_command, [])

        # Click returns exit code 2 on syntax or usage validation errors
        assert result.exit_code == 2
        assert "Error: Missing option" in result.output
```

---

## Testing Command Registration via `with_extended_cli`

If your extension registers its CLI commands dynamically using the `IClick`
plugin interface, the core CKAN CLI needs to discover them.

To test execution via the global `ckan` entry point (verifying that your
command is correctly registered and named on the CLI group), you must apply the
`with_extended_cli` fixture alongside `with_plugins`:

```python title="tests/test_cli_registration.py"
from __future__ import annotations

import pytest
from ckan.cli.cli import ckan

# 1. Apply fixtures to load plugin commands and enable configuration patches
@pytest.mark.ckan_config("ckan.plugins", "myextension_plugin")
@pytest.mark.usefixtures("with_extended_cli", "with_plugins")
class TestCliRegistration:

    def test_run_command_by_name(self, cli):
        """Verify the command is registered and executes under the 'ckan' CLI."""
        # 2. Invoke the command via the main CKAN CLI group by name
        result = cli.invoke(ckan, ["myextension", "run-task", "--id", "123"])

        assert result.exit_code == 0
        assert "Task 123 completed successfully" in result.output
```


/// admonition | The Role of `with_extended_cli`
    type: note

By default, the global `ckan` Click command group is initialized only once from
your static test configuration files. The `with_extended_cli` fixture patches
the CLI configuration loader, allowing dynamically loaded test plugins (via
`@pytest.mark.ckan_config`) to register their commands on the CLI group for the
scope of the test.


///
