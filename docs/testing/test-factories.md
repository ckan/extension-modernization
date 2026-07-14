---
icon: lucide/factory
---

# Test Factories

Test factories generate mock database records. CKAN extensions can use
factories in two ways:

* **Pytest Fixtures**: Powered by `pytest-factoryboy`, these
  integrate with Pytest's dependency injection for declarative setup.
* **Direct Factory Classes**: Imported directly from `ckan.tests.factories` and
  called manually within test functions.

---

## Pytest Fixture-Style Factories

Using `pytest-factoryboy` allows you to register factories as reusable
fixtures, making tests more "pytest'ish" and keeping test setups declarative.

### Registering a Custom Extension Factory

To register a factory for a custom extension model, inherit from
`ckan.tests.factories.CKANFactory` and register it using the `@register`
decorator in `tests/conftest.py`.

The factory class must contain nested `Meta` class with reference to the
created model and name of API action responsible for creation.

```python title="tests/conftest.py"
import factory
from pytest_factoryboy import register
from ckan import model
from ckan.tests import factories


@register # (1)!
class FileFactory(factories.CKANFactory):
    class Meta:
        model = model.File  # (2)!
        action = "file_create"  # (3)!

    # 4. Define default attribute generators
    name = factory.LazyFunction(factories.fake.unique.file_name)
    upload = factory.Faker("binary", length=100)
```

1. This decorator registers two fixtures: one is a function with camelized name
   of the factory class (`file_factory`) that produces objects; another uses
   camelized name of the `model` (`file`) and contains the instance produced by
   this factory.
2. The SQLAlchemy model representing the custom database table.
3. The logic action API responsible for inserting/validating the record.
4. Generates unique file names and random binary payloads by default.

---

## Defining Factory Attributes

To generate realistic mock data, you can configure factory fields using static
values, sequential values, or random generators.

### Static Attributes
For properties that should default to the same constant value across all entities:

```python
class DocumentFactory(factories.CKANFactory):
    # ...
    format = "PDF" # Every document will have format="PDF" by default
```

### Sequences

If a field must be unique (such as a username or code ID), use
`factory.Sequence()`. It passes a unique incrementing integer `n` (starting at
0) to your generator function:

```python
class UserFactory(factories.CKANFactory):
    # ...
    # Generates: user-0, user-1, user-2, etc.
    name = factory.Sequence(lambda n: f"user-{n}")
```

### Lazy Functions

Use `factory.LazyFunction()` when you want to call a function (without
arguments) every time the factory generates an object. This is ideal for
timestamping or generating values dynamically:

```python
from datetime import datetime

class ResourceFactory(factories.CKANFactory):
    # ...
    # Evaluated at the time of creation (not class load)
    created = factory.LazyFunction(datetime.now)
```

### Using Faker for Random Attributes

There are two ways to integrate [Faker](https://faker.readthedocs.io/) into
your attribute declarations:

#### Using `factory.Faker`

This is a built-in provider that maps to Faker's generators. It is clean,
concise, and supports passing parameters:

```python
class ProfileFactory(factories.CKANFactory):
    # ...
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    avatar = factory.Faker("image_url", width=120, height=120)
```

#### Using `factory.LazyFunction` with `faker` instances

If you need custom Faker configurations (like fetching unique values, or using
localized or nested fake data providers), instantiate a `Faker` object and pass
it inside a `LazyFunction`:

```python
from faker import Faker

fake = Faker()

class DatasetFactory(factories.CKANFactory):
    # ...
    # Guarantees that the name will be unique across all test runs
    name = factory.LazyFunction(fake.unique.company)

    # Generates a localized address using the local Faker instance
    location = factory.LazyFunction(lambda: fake.address())
```

### Dependent Attributes (Lazy Attributes)

If an attribute's value depends on the value of another attribute of the same
object, use `factory.LazyAttribute()`. This accepts a lambda function receiving
the constructed entity instance (`obj`):

```python
class UserFactory(factories.CKANFactory):
    # ...
    name = factory.Sequence(lambda n: f"user-{n}")

    # Generates email based on the name attribute (e.g. user-0@example.com)
    email = factory.LazyAttribute(lambda obj: f"{obj.name}@example.com")
```

---

## Instance vs. Factory Fixture Variants

When you register a factory with `@register`, `pytest-factoryboy` creates two separate fixtures:

### The Instance Fixture (`entity`)

Injecting the name of your entity (e.g. `file` or `user`) automatically
triggers the factory to write the object to the database and returns the
populated dictionary/model before the test body runs.

```python
def test_file_details(file):
    # 'file' is already created in the database
    assert "id" in file
    assert file["name"] is not None
```

This example is absolutely identical to the following:

```python
def test_file_details(file_factory: types.TestFactory): # (1)!
    file = file_factory()
    assert "id" in file
    assert file["name"] is not None
```

1. Add `#!python from ckan import types` to use typehints.


### The Factory Fixture (`entity_factory`)

Injecting the name followed by `_factory` (e.g. `file_factory` or
`user_factory`) returns the callable factory class itself. This is useful when
you want to customize attributes for multiple instances or defer creation
inside the test.

```python
def test_multiple_files(file_factory: types.TestFactory):
    # Explicitly generate records with custom attributes
    pdf = file_factory(name="document.pdf", upload=b"PDF_HEADER")
    csv = file_factory(name="data.csv", upload=b"CSV_HEADER")

    assert pdf["name"] == "document.pdf"
```

---

## Direct Factory Classes

Alternatively, you can import and invoke factory classes directly inside test
functions. This is useful for simple scripts but is less declarative than using
Pytest's dependency injection.

### Standard Core Factories

Core CKAN models have corresponding factory classes under `ckan.tests.factories`:

```python title="tests/test_example.py"
from ckan.tests import factories
import pytest

@pytest.mark.usefixtures("clean_db")
def test_dataset_association():
    # 1. Create organization
    org = factories.Organization(name="my-org")

    # 2. Create user
    user = factories.User(name="john")

    # 3. Create dataset owned by organization
    dataset = factories.Dataset(
        name="my-dataset",
        owner_org=org["id"]
    )

    # 4. Associate resources
    resource = factories.Resource(
        package_id=dataset["id"],
        url="https://example.com/data.csv"
    )
```

---

## Comparison: Pytest Fixtures vs. Direct Classes

| Feature           | Pytest-Factoryboy Fixtures                               | Direct Factory Classes                         |
|:------------------|:---------------------------------------------------------|:-----------------------------------------------|
| **Call Style**    | Declarative parameters (`user`, `user_factory`)          | Procedural function calls (`factories.User()`) |
| **Code Style**    | Clean and idiomatic Pytest, but extends test's signature | Can lead to boilerplate setup blocks in tests  |
| **Customization** | Overrides passed as kwargs to `_factory`                 | Overrides passed as kwargs to constructor      |

---

## Action Execution Context and User Parameters

Under the hood, `CKANFactory` calls CKAN core logic action APIs to persist entities in the database.

### The `user` Parameter for Context

By default, every factory accepts a `user` parameter (which can be a user
dictionary returned by a factory, or a string representing a username). This
parameter is extracted from the arguments and placed inside the action
execution `context` dictionary (`#!python context = {"user": username}`).

This ensures that the creation action runs on behalf of that specific user,
which is critical if the action validates auth rules or sets owner fields:

```python
def test_dataset_creator_context(package_factory, user):
    # The package_create action is called with context['user'] = user['name']
    dataset = package_factory(name="my-dataset", user=user)

    assert dataset["creator_user_id"] == user["id"]
```

### Exception: Named `user` Action Parameters

Some factories represent entities where `user` is a payload property of the
action itself rather than the actor context (for instance, the `APIToken`
factory requires a `user` parameter to designate which user is receiving the
token).

For these factories, passing the `user` argument acts as a parameter of the
action payload (as the API schema expects), rather than modifying the creator
context:

```python
def test_api_token_assignment(api_token_factory, user):
    # Here, 'user' is passed as a payload parameter to 'api_token_create'
    # (indicating the recipient of the token), not the actor context.
    token_dict = api_token_factory(user=user["id"])

    assert token_dict["user_id"] == user["id"]
```

---

## CKAN Core Factories Registry

CKAN core provides pre-registered pytest-factoryboy fixtures for all core
database entities. These are available in your test files automatically without
manual imports when `pytest-ckan` is active:

| Factory Class (`ckan.tests.factories`) | Instance Fixture      | Factory Fixture               | Model Target (`ckan.model`)      | Action Endpoint                |
|:---------------------------------------|:----------------------|:------------------------------|:---------------------------------|:-------------------------------|
| `User`                                 | `user`                | `user_factory`                | `User`                           | `user_create`                  |
| `Sysadmin`                             | `sysadmin`            | `sysadmin_factory`            | `User` *(sysadmin=True)*         | `user_create`                  |
| `UserWithToken`                        | `user_with_token`     | `user_with_token_factory`     | `User` *(with API Token)*        | `user_create` + post token gen |
| `SysadminWithToken`                    | `sysadmin_with_token` | `sysadmin_with_token_factory` | `User` *(with API Token)*        | `user_create` + post token gen |
| `Dataset`                              | `package`             | `package_factory`             | `Package`                        | `package_create`               |
| `Resource`                             | `resource`            | `resource_factory`            | `Resource`                       | `resource_create`              |
| `ResourceView`                         | `resource_view`       | `resource_view_factory`       | `ResourceView`                   | `resource_view_create`         |
| `Group`                                | `group`               | `group_factory`               | `Group`                          | `group_create`                 |
| `Organization`                         | `organization`        | `organization_factory`        | `Group` *(is_organization=True)* | `organization_create`          |
| `Vocabulary`                           | `vocabulary`          | `vocabulary_factory`          | `Vocabulary`                     | `vocabulary_create`            |
| `Tag`                                  | `tag`                 | `tag_factory`                 | `Tag`                            | `tag_create`                   |
| `APIToken`                             | `api_token`           | `api_token_factory`           | `ApiToken`                       | `api_token_create`             |
| `SystemInfo`                           | `system_info`         | `system_info_factory`         | `SystemInfo`                     | Config store (custom method)   |
| `File`                                 | `file`                | `file_factory`                | `File`                           | `file_create`                  |

---

## Advanced Factory Methods

Factory classes and `_factory` fixtures support several advanced generation
strategies to return SQLAlchemy model instances, stub data without database
writes, or generate multiple entities at once.

### The `model` Method

By default, calling a factory or its fixture writes the entity to the database
via API and returns a **plain python dictionary** representing the serialized
API response.

If your test needs to interact with the underlying **SQLAlchemy database
model** object instead of a dictionary (for instance, to assert relationship
mapping properties or run database session operations), call the `.model()`
class method:

```python
from ckan import types
from ckan.tests import factories
from ckan.model import User

def test_user_model_instance(user_factory: types.TestFactory):
    # Returns an instance of ckan.model.User instead of a dictionary
    user_obj = user_factory.model(name="alice")

    assert isinstance(user_obj, User)
    assert user_obj.state == "active"
```

### The `stub` Method

If your test only validates schemas, parameters, or forms, you might want to
generate a set of valid dummy attributes **without** actually writing a record
to the database or running time-consuming action workflows.

Call `.stub()` to return a local mock namespace object containing all the
randomly generated parameters the factory *would* have used:

```python
def test_user_validation_form(user_factory):
    # Generates attributes locally; no DB insert or API calls are run
    stub_data = user_factory.stub(fullname="Alice Smith")

    assert stub_data.fullname == "Alice Smith"
    assert "@" in stub_data.email # Faker generated email

    # Convert stub properties to a dictionary to simulate form POST body payload
    form_payload = vars(stub_data)
```

### The `create_batch` Method

To quickly seed a database with multiple mock records for listings, pagination,
or search index tests, use `create_batch(size, **kwargs)`. This calls the
factory creation pipeline repeatedly to insert multiple records:

```python
def test_dataset_pagination(package_factory):
    # Create 15 datasets in the DB
    datasets = package_factory.create_batch(15, owner_org="my-org-id")

    assert len(datasets) == 15
    assert datasets[0]["owner_org"] == "my-org-id"
```

---

## Command-Line Data Generation

CKAN provides a command-line tool `ckan generate fake-data` to easily bootstrap
a development database with mock records.

### Basic Generation

Generate a number of entities using built-in factories (aliases include `user`,
`dataset`, `resource`, `organization`, `group`):

```bash
# Generate 5 fake datasets in the database (outputs JSON for each)
ckan generate fake-data dataset -n 5
```

---

### Generating Custom Extension Entities

If you have defined a custom factory inside your extension (e.g. `FileFactory`
registered inside `ckanext.myextension.tests.conftest`), you can invoke it by
passing its full Python import path as `-f`/`--factory-class` argument:

```bash
ckan generate fake-data -f ckanext.myextension.tests.conftest:FileFactory -n 3
```

---

### Passing Parameters to Factories

You can customize the generated data by passing factory options directly via
command-line arguments in the format `--NAME=VALUE`. These extra arguments are
collected and passed as keyword parameters to the factory's creation logic:

```bash
# Generate a dataset with a custom title and owner organization
ckan generate fake-data dataset --title="Special Core Data" \
    --owner_org="my-org-id"
```

For custom factories, pass your specific parameters in the same manner:

```bash
ckan generate fake-data -f ckanext.myextension.tests.conftest:FileFactory \
    --name="manual_upload.pdf" --upload="file_content_here"
```
