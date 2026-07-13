---
icon: lucide/help-circle
---

# Helpers

Template helpers format data, wrap configuration flags, or resolve URLs for Jinja2 templates. Tests verify that helpers process inputs and return correct formatting or markup structures.

---

## Testing Helpers Directly

The fastest way to test helper functions is to import them directly from their module and test them as pure python functions:

```python title="tests/test_helpers.py"
from __future__ import annotations

from ckanext.myextension.helpers import myextension_format_filesize

class TestTemplateHelpers:

    def test_format_filesize_bytes(self):
        """Verify byte formatting outputs."""
        result = myextension_format_filesize(512)
        assert result == "512 B"

    def test_format_filesize_kilobytes(self):
        """Verify kilobyte formatting outputs."""
        result = myextension_format_filesize(1536)
        assert result == "1.50 KiB"
```

---

## Testing Registered Helpers via Toolkit

To verify that your helpers are correctly registered and available under CKAN's global helper registry (`h`), load the plugins and resolve the helper via the toolkit:

```python
import ckan.plugins.toolkit as tk
import pytest

@pytest.mark.usefixtures("with_plugins")
def test_helper_registration(self):
    """Verify the helper is registered and accessible via toolkit."""
    # Ensure the helper exists in the global h registry
    assert hasattr(tk.h, "myextension_format_filesize")
    
    # Resolve and invoke helper
    result = tk.h.myextension_format_filesize(1024 * 1024)
    assert result == "1.00 MiB"
```
