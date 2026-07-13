---
icon: lucide/factory
---

# Test Factories

CKAN provides a set of factory utilities under `ckan.tests.factories` to generate mock database records quickly. These factories bypass HTTP API layers and directly write models to the database, ensuring clean and fast test setups.

---

## Creating Test Users

Generate test users with customizable attributes (e.g. usernames, emails, sysadmin flags):

```python
from ckan.tests import factories

# Create a regular user
user = factories.User(name="john_doe", email="john@example.com")

# Create a sysadmin user
admin = factories.Sysadmin(name="admin_user")
```

---

## Creating Organizations

Generate organizations to establish dataset owner contexts:

```python
org = factories.Organization(
    name="test-org",
    title="Test Organization",
    description="This is a test organization"
)
```

---

## Creating Datasets (Packages)

Create datasets and optionally associate them with an owner organization:

```python
dataset = factories.Dataset(
    name="test-dataset",
    title="My Test Dataset",
    owner_org=org["id"]
)
```

---

## Creating Resources

Add file resources directly inside a dataset:

```python
resource = factories.Resource(
    package_id=dataset["id"],
    url="https://example.com/data.csv",
    format="CSV"
)
```

---

## Why Use Factories?

* **Speed**: They communicate directly with the database layer via SQLAlchemy, bypassing validation middleware and HTTP request handling overhead.
* **Defaults**: They automatically generate valid mock data for required fields you don't specify (like generating random email addresses or unique IDs).
* **Return Format**: Factories return standard python dictionaries matching the serialized outputs of corresponding action APIs, making assertions easy.
