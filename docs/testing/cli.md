---
icon: lucide/terminal-square
---

# CLI Commands

CKAN extensions define command-line interfaces using the **Click** framework. Testing CLI commands ensures they process arguments, execute operations, and print the expected output to the stdout stream.

---

## Testing via Click's CliRunner

Use Click's `CliRunner` to execute and capture the results of your commands:

```python title="tests/test_cli.py"
from __future__ import annotations

import pytest
from click.testing import CliRunner
from ckanext.myextension.cli import myextension_command

@pytest.mark.usefixtures("with_plugins")
class TestCliCommands:

    def test_command_execution_success(self):
        """Verify the command runs successfully and prints output."""
        runner = CliRunner()
        
        # Invoke the command with arguments
        result = runner.invoke(myextension_command, ["--name", "test-item"])
        
        # Assert exit code is 0 (success)
        assert result.exit_code == 0
        
        # Check stdout prints
        assert "Successfully created item test-item" in result.output

    def test_command_missing_arguments(self):
        """Verify the command exits with error code when arguments are missing."""
        runner = CliRunner()
        
        # Invoke without mandatory name argument
        result = runner.invoke(myextension_command, [])
        
        # Click returns exit code 2 on syntax/usage errors
        assert result.exit_code == 2
        assert "Error: Missing option" in result.output
```

---

## Accessing CKAN Context in CLI Tests

If your command relies on reading configuration values or accessing database records, you must run it within the application context. `CliRunner.invoke` handles this if the CKAN environment is loaded via the `with_plugins` fixture:

```python
def test_command_db_lookup(self, clean_db):
    """Verify CLI command can query database models."""
    runner = CliRunner()
    
    # Run the command that queries items from the DB
    result = runner.invoke(myextension_command, ["list-items"])
    
    assert result.exit_code == 0
```
