---
icon: lucide/terminal
---

# Unit Tests

Unit tests verify that individual components—like action functions, auth functions, database models, and helper methods—behave correctly in isolation. 

CKAN extensions use **Pytest** as their test runner.

---

## Directory Layout

All tests are placed in a `tests/` directory under your extension's package root:

```
ckanext-myextension/
├── pyproject.toml
└── ckanext/
    └── myextension/
        └── tests/
            ├── conftest.py          # Shared fixtures
            ├── test_helpers.py      # Template helper tests
            ├── test_models.py       # DB Model tests
            ├── logic/
            │   ├── test_action.py   # Action tests
            │   └── test_auth.py     # Auth tests
            └── views/
                └── test_views.py    # Flask routing tests
```

---

## Running Unit Tests

Run your test suite using the `pytest` command line. Specify the path to your testing configuration file (typically `test.ini`):

```bash
# Run all tests
pytest --ckan-ini=test.ini

# Run tests in a specific folder
pytest --ckan-ini=test.ini ckanext/myextension/tests/logic/

# Run a specific test file
pytest --ckan-ini=test.ini ckanext/myextension/tests/logic/test_action.py
```

---

## Test Filtering & Marks

Use Pytest marks to categorize tests and speed up runs:

```python
import pytest

@pytest.mark.unit
def test_some_pure_logic():
    assert 1 + 1 == 2
```

Configure filters to run or exclude specific marks:

```bash
# Run only unit-marked tests
pytest -m unit --ckan-ini=test.ini

# Exclude integration-marked tests
pytest -m "not integration" --ckan-ini=test.ini
```

---

## Code Coverage

Measure coverage statistics to identify untested code paths:

```bash
pytest --ckan-ini=test.ini --cov=ckanext.myextension --cov-report=term-missing
```
