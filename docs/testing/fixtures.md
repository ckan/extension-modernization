---
icon: lucide/test-tube
---

# Setup Fixtures

Fixtures are reusable components that set up state, prepare mocks, or expose
APIs to your tests. CKAN extensions utilize Pytest fixtures for plugin loading
and database lifecycle management.

CKAN adds a number of useful fixtures to the test suite, and extensions can
additionally register new fixtures or modify existing ones.

---

## Fixture definition

Fixtures must be defined in `conftest.py` inside any test folder. Fixtures
defined inside `conftest.py` will be available for all tests in the same
directory or its subdirectories.

```python title="conftest.py"
import pytest

@pytest.fixture
def my_fixture():
    return 1
```


`conftest.py` inside nested folder can be used to define additional fixtures
that have sense only to group of tests. Additionally you can override parent
fixtures here.

Fixtures can be also defined inside test files and as methods of test
classes. Fixture defined globally in the file, will be available only inside
this module. Fixture defined as class method will be available only inside this
class.

/// admonition
    type: example

```python title="test_something.py"
import pytest

@pytest.fixture
def module_data(): ...

class TestSomething:
    @pytest.fixture
    def class_data(self): ...

```

///

---

## Add fixture to test

To enable fixture, simply add it as an argument to your test. The fixture
function will be called and its returned value will be provided during test
execution.

```python title="test_something.py"
import pytest

@pytest.fixture
def data():
    return 42

def test_fixture(data):
    assert data == 42
```

---

## Reusable fixtures

By default, fixture is created once per test function and cached for this
test. If the same fixture is required multiple times during the same test, the
same instance will be used everywhere.

```python

@pytest.fixture
def data():
    return {}

@pytest.fixture
def augmented_data(data): # (1)!
    data["extra"] = 42
    return data

def test(data, augmented_data): # (2)!
    assert data is augmented_data # (3)!

```

1. Instance of `data` initialized here. The fixture mutates and returns the
   same `data` it took as input, not the new object of clone of `data`.

2. `data` has been already initialized and here we'll get the cached version,
   the same that was used for `augmented_data` initialization.

3. Both `data` and `augmented_data` contain `extra: 42`, because they are the same object.

It can be used to move initialization step of the test to fixtures. Imagine
that you need a user, an organization to which user belongs and a dataset
created by the user in the same test.

You can create these 3 objects in the beginning of the test. But this adds
noise to the test and hides actual thing that is tested. In addition, if you
want to do it inside multiple tests, you'll have to copy-paste the boilerplate
code.

First attempt to improve the situation may result in defining a function
`create_data` that returns a tuple with all three items, or a dictionary of
form `#!python {"user": ..., "org": ..., "dataset": ...}`. This is much better,
but still feels a bit off, because of the complex structure of returned object.

Here come fixtures. You define separate fixtures for all 3 items and make sure
that dataset and organization fixtures require user-fixture. Because of the
cache, they will use exactly the same user.

The test itself will require all three of these items, receiving the same user
that was used during initialization of organization and dataset. On top of
this, you can include only organization into your test and omit dataset - it
won't be created at all in this case.

```python


@pytest.fixture
def dataset(user, package_factory, organization): # (1)!
    return package_factory(user=user, owner_org=organization["id"])

@pytest.fixture
def organization(user, organization_factory):
    org = organization_factory(users=[{"name": user["name"], "capacity": "admin"}])
    return org

def test_something(user, dataset, organization):
    assert dataset["creator_user_id"] == user["id"]
    assert dataset["owner_org"] == organization["id"]
```

1. In this example we went further and added organization fixture to the
   dataset. It will be the same organization passed to test itself, so we
   produce dataset _created by the shared user_ and _owned by the shared
   organization_. Note, even though dataset fixture is defined before the
   organization fixture, pytest will build dependency graph of fixtures and
   order them accordingly, initializing organization before the dataset.

/// admonition | Isn't it a lot of arguments for test?
    type: question

Using fixtures you can quickly get to tests that are requiring 5-10-15
fixtures. It may seem a lot, but with pytest it's a normal situation. Fixture
means that certain number of lines with initialization logic is moved
from the test to the fixture. It's a change for a greater good.

Still, if you need more than 5 fixtures, your test may be
overcomplicated. Consider splitting it into few smaller tests that verify only
one or two aspects of the application.

There are situations when fixtures themselves are not used and included into
tests only for side-effect. I.e. you are including `dataset` fixture, because
you need to verify that `There are no datasets found` message is hidden when
you have at least one dataset, but you never check whether this actual dataset
is show on the page. In this case you can move fixtures from test signature to
`usefixtures` mark.

```python
@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index", "dataset")
def test_search(app):
    page = app.get("/dataset")
    assert "There are no datasets" not in page.body
```

///

---

## Fixture scope

By default fixtures are initialized and cached for every individual tests. But
this "lifetime" can be extended by fixture's _scope_:

* `function`: the default scope, the fixture is destroyed at the end of the test.
* `class`: the fixture is destroyed during teardown of the last test in the class.
* `module`: the fixture is destroyed during teardown of the last test in the module.
* `package`: the fixture is destroyed during teardown of the last test in the package.
* `session`: the fixture is destroyed at the end of the test session.

To apply a different scope, specify `scope` argument when fixture is defined.

```python
@pytest.fixture(scope="class")
def small_fixture(): ...

@pytest.fixture(scope="module")
def big_fixture(): ...

@pytest.fixture(scope="session")
def big_fixture(): ...

```

/// admonition | Inter-scope relationship
    type: note

Fixture can require other fixtures only if they have only the same or wider
scope. I.e, fixture with the `function` scope can require any other fixture;
fixture with `session` scope can require only fixtures with `session` scope.

///


/// admonition | @smotornyuk: Scope of fixtures
    type: quote

Usually, default `function` scope is the best, because it helps to avoid
accidental relationship between tests, especially if they mutate fixture's
value. Additionally, when tests are randomized or grouped, `class` and `module`
level fixtures may behave in unexpected manner.

The only scope other from `function` that I'd recommend to use is
`session`. This scope initialize a single global fixture for the whole test
run - it will be initialized when first test requires it and will remain the
same till the end of the last test.

///

### Session scope

Session-scoped fixtures can be used to initialize shared global data or to
perform once a time-consuming task, like starting dev server for e2e
tests.

```python
@pytest.fixture(scope="session")
def global_fixture()
    data = []
    yield data # (1)!

    assert len(data) == 2, "Not all tests were executed" #(2)!

def test_one(data):
    data.append(1)

def test_two(data):
    data.append(2)
```

1. You can `yield` result from fixture. In this case, the rest of fixture's
   code will run during fixture's teardown. For `session` scope it happens
   after the last test.
2. The second element of `assert` is a message shown in case of fail.

/// admonition
    type: note

Session-scoped fixtures are initialized once and do not react on changes in the
configuration: if you created a dev server and then, in the following tests,
modified the config, the dev server will use the original configuration that
existed during its initialization (unless you somehow managed to dynamically
swap config inside running process).

///


---

## Parametrization

/// admonition | Parametrization recap
    type: note

Tests can be _parametrized_: they will run multiple times with different values
for specific argument.

To parametrize the test, attach `parametrize` mark to it. First aprgument of the
mark specifies names of parameters and second argument contains iterable with
possible values of these parameters.

```python
@pytest.mark.parametrize("value", [1, 2, 3])
def test_conversion(value: int):
    assert int(str(value)) == value

```

The test in example will be executed three times: with `1`, `2` and `3`. This
is the great way to test function that processes value: you can check normal
values, edge cases and extend list of parameters with time when new problems
discovered and fixed.

To add more than one parameters, specify all names of parameters in the first
argument and include collections of parameter values into iterable provided in
the second argument.

```python
@pytest.mark.parametrize("value, expected", [ # (1)!
    (1, 10),
    (2, 20),
    (3, 30)
])
def test_conversion(value: int, expected: int):
    assert value * 10 == expected
```

1. Names can be specified as list of strings (`#!python ["value", "expected"]`)
   instead of single comma-separated string, but historically version from
   example is more popular.

///


Fixtures can also be parametrized in multiple ways, even though it's a bit
advanced topic.

There are two main cases for fixture parametrization. First, the fixture itself
parametrized and whenever it's requested by the test, test will be executed
multiple times with every fixture version.

To parametrize the fixture, add `param=VALUES` to the `fixture`
decorator. Unlike tests, parameters do not come into fixture by name. Instead
you have to use separate fixture `request` and access its attribute `param`:
the current value of parameter will be stored there.

```python
@pytest.fixture(params=[1,2,3])
def data(request):
    return request.param * 10


def test_data(data: int):
    print(data)
```

In this example, `test_data` is executed 3 times: with values of `data` set to
`10`, `20` and `30`.

This option is convenient when fixture provides some kind of client for tests
and this client can use multiple different drivers or backends. Parametrizing
such fixture allows running tests against every available backend.

Another option is to provide parameters for fixture from tests. This option
even more intricated. It mainly used to allow configuring fixture from test.

In this version, fixture itself does not have parameters, but instead they are
provided by parametrize mark from test. This time `parametrize` mark
includes `indirect=True` flag, so that values of the parameter passed not to
test, but to fixture instead.

```python
@pytest.fixture(params=[]) # (1)!
def data(request):
    return request.param * 10

@pytest.mark.parametrize("data", [1,2,3], indirect=True) # (2)!
def test_data(data: int):
    print(data)
```

1. You can specify default parameters here, or even empty list, to skip test
   that does not parametrize the fixture.

2. Name of the parameter must match the name of the fixture required by
   test. Without `indirect=True`, parameter will be passed directly into
   test. But when this flag is enabled, parameter instead passed into fixture
   (as `request.param`) and the result of fixture is then used in the test.

Usecases for this fixture type is pretty specific. Sometimes it's used with
default parameters to test multiple items, while parametrization from test
narrows down this list. For example, fixture that creates storage for every
available backend and test that restricts list of backends to cloud-backends,
because it's checking validity of signed cloud-urls, which arno not implemented
at all for filesystem or memory backend.

---

## Common Fixtures

### `tmp_path: pathlib.Path`

A built-in Pytest fixture that provides a unique temporary directory path for
each test function. The directory is automatically cleaned up and deleted after
the test finishes.

/// admonition
    type: example

Writing file uploads or export caches to disk during test runs.

```python
def test_export_data(tmp_path: Path):
    file_path = tmp_path / "dataset.csv"
    file_path.write_text("id,name\n1,Test")
    assert file_path.read_text() == "id,name\n1,Test"
```

Use `tmp_path` instead of creating files in the project's root or `/tmp/`
directory to prevent parallel test runs from colliding or leaving behind dirty
file states.

///

---

### `monkeypatch: pytest.MonkeyPatch`

A built-in Pytest fixture that allows safe modification of system environment
variables, object attributes, dictionaries, or `sys.path` during a test
execution context. Everything is automatically restored to its original state
after the test.

/// admonition
    type: example

Mocking third-party API client behavior or patching environment flags.

```python
def test_external_sync(monkeypatch: MonkeyPatch):
    # Override the external API URL
    monkeypatch.setenv("SYNC_SERVICE_URL", "https://mock.service/api")

    # Mock the return value of an external API call function
    from ckanext.myextension import utils
    monkeypatch.setattr(utils, "call_external_api", lambda *args: {"status": "ok"})
```

///


---

### `faker: faker.Faker`

Exposed by `pytest-faker` (registered as the `faker` fixture). It generates random, realistic test data such as names, emails, URLs, dates, and descriptions.

/// admonition
    type: example

Seeding database models or generating payloads.

```python
def test_user_creation(faker: Faker):
    email = faker.email()
    name = faker.user_name()
    # Pass these generated fields to your factories
```

Combine `faker` with CKAN factories to ensure your test objects use unique and
valid emails/names, preventing database unique constraint violations.

///

---

### `ckan_config: ckan.types.FixtureCkanConfig`

A core CKAN fixture that provides a clean copy of the configuration dictionary
(`ckan.plugins.toolkit.config`) and allows temporary overrides via
`ckan_config` mark. The configurations are automatically reverted at the end of
the test.

/// admonition
    type: example

Modifying custom extension settings or site-wide options.

```python
@pytest.mark.ckan_config("ckan.site_title", "Custom Test Portal")
def test_portal_title(ckan_config: types.FixtureCkanConfig):
    assert ckan_config["ckan.site_title"] == "Custom Test Portal"
```

Never modify `ckan.plugins.toolkit.config` directly inside a test body, as it
leaks configuration pollution across tests. Always use the
`@pytest.mark.ckan_config` mark or modify the injected `ckan_config`
dictionary.

///

---

### `app: ckan.types.FixtureApp`

Exposes the Flask test client instance, allowing you to simulate and assert
GET, POST, and other HTTP requests against your view blueprints without running
a real web server.

/// admonition
    type: example

Checking view route status codes.

```python
def test_items_view(app):
    response = app.get("/my-extension/items")
    assert response.status_code == 200
```

///

/// admonition | Authentication
    type: tip

Users can be authenticated via `app.set_session_user` method. After the call,
all requests will be made on behalf of specified user.

```python
def test_items_view(app: types.FixtureApp, user: dict[str, Any]):
    app.set_session_user(user["name"])
    response = app.get("/dashboard")
    assert response.status_code == 200
```

///


/// admonition | CKAN v2.11 authentication
    type: note

`set_session_user` was added in v2.12. In v2.11 you need to set `Authorization`
header on every request instead.

```python
def test_items_view(app: types.FixtureApp, api_token: dict[str, Any]):
    response = app.get("/dashboard", headers={"Authorization": api_token["token"]})
    assert response.status_code == 200
```

///


---

### `cli: ckan.tests.helpers.CKANCliRunner` and `with_extended_cli: None`

**`cli`**: A custom wrapper around Click's `CliRunner` pre-configured to
  execute command-line actions within the correct CKAN application context.

**`with_extended_cli`**: An initialization helper that ensures commands
  registered by newly loaded plugins are correctly bound and discoverable by
  the CLI runner. Without this fixture, CLI commands registered by dynamically
  loaded plugin (not enabled via `test.ini`) are not available during tests.

/// admonition
    type: example

Running a custom CLI command.

```python
from ckanext.myextension.cli import my_cli_command

@pytest.mark.usefixtures("with_extended_cli")
def test_my_command(cli: CKANCliRunner):
    result = cli.invoke(my_cli_command, ["--name", "test"])
    assert result.exit_code == 0
    assert "Success" in result.output
```

///

---

### `clean_db: None` and `reset_db: ckan.types.FixtureResetDb`

**`reset_db`**: A session-scoped callable that empties database tables and
prepares the DB to a clean state.

**`clean_db`**: A function-scoped fixture that resets the DB state before every
test. In extension repositories, you should override this in your `conftest.py`
to also apply your extension migrations.

/// admonition
    type: example

Always add `with_plugins` before the `clean_db` fixture. If you are applying
plugin migrations, this guarantees all configured plugins are loaded before DB
initialization.

```python
def test_db(with_plugins, clean_db):
    # database is initialized and empty here
    ...
```
///


/// admonition
    type: tip

Define your own version of `clean_db` that applies migrations for enabled plugins.

```python title="tests/conftest.py"
@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("myextension")  # Runs migrations for this plugin
```


///

---

### `clean_index: None` and `reset_index: ckan.types.FixtureResetIndex`

**`reset_index`**: A session-scoped callable that empties the Solr search index database.

**`clean_index`**: Clears the Solr index before the test, ensuring that queries
or search pages only return datasets created within the current test.

/// admonition
    type: example

`clean_index` often used with `clean_db`. `clean_index` does not requires `with_plugins`
fixture, but `clean_db` does, so you'll often see three of them together.

```python
@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
def test_dataset_search():
    # Index is empty; create a test dataset and assert search behavior
    factories.Dataset(title="Special Data")
    # ... assert dataset is found in search ...
```

///

---

### `clean_redis: None` and `reset_redis: ckan.types.FixtureResetRedis`

**`reset_redis`**: A session-scoped callable that cleans the Redis cache
keys. It accepts a key-matching pattern parameter (defaults to `*`).

**`clean_redis`**: A function-scoped fixture that automatically empties the Redis cache before the test.

```python
@pytest.mark.usefixtures("clean_redis")
def test_cache_layer():
    # Redis starts empty
    pass
```

---

### `provide_plugin: ckan.types.FixtureProvidePlugin`

A helper fixture that programmatically registers and instantiates a plugin
class for the duration of the test, without needing to declare it inside
entrypoints of the python package.

/// admonition
    type: example


```python
def test_temporary_plugin(provide_plugin: types.FixtureProvidePlugin):
    provide_plugin("my_mock_plugin", MyMockPluginClass)
    # Plugin is loaded and active for this test
```

///

/// admonition | Using marks
    type: tip

Alternatively, test plugins can be added with `provide_plugin` mark, which
internally relies on the current fixture. This style requires using
`ckan_config` mark and applying fixture `with_plugins`, which makes it
overcomplicated. Check `with_plugins` example to find simple solution.

```python
@pytest.mark.provide_plugin("my_mock_plugin", MyMockPluginClass)
@pytest.mark.ckan_config("ckan.plugins", ["my_mock_plugin"])
@pytest.mark.usefixtures("with_plugins")
def test_fake_plugin():
    plugin = plugins.get_plugin("my_mock_plugin")
    assert isinstance(plugin, MyMockPluginClass)
```

///


---

### `with_plugins: None`

Enforces loading and unloading of all plugins specified in the `ckan.plugins` config option before and after a test.

```python
@pytest.mark.ckan_config("ckan.plugins", "myextension_plugin")
@pytest.mark.usefixtures("with_plugins")
def test_action():
    # The actions registered by myextension_plugin are now active
    result = call_action("myextension_action")
```

/// admonition | Using marks
    type: tip

The fixture can be used as mark. It iterates over all arguments and appends
them to the list of ``ckan.plugins`` before loading. This can be used to
enable few plugins **in addition** to any plugins that are already
specified by the ``ckan.plugins`` option.

To load a real plugin, provide its name as a string. To create instance of the
given class and use it as plugin, provide a dictionary with name-class mapping.

```python
@pytest.mark.with_plugins("XXX", {"my_mock_plugin": MyMockPluginClass})
def test_action_and_helper():
    assert plugins.plugin_loaded("XXX")
    assert plugins.plugin_loaded("my_mock_plugin")
    # any other plugin from `ckan.plugins` is loaded as well
```

///

---

### `with_request_context: None` and `test_request_context: ckan.types.FixtureTestRequestContext`

**`test_request_context`**: Factory to create Flask request contexts.

**`with_request_context`**: A function-scoped helper that automatically pushes
a default Flask request context, allowing you to access globals like
`flask.request` or `flask.g` inside unit tests.

```python
@pytest.mark.usefixtures("with_request_context")
def test_request_headers():
    from flask import request
    assert request.headers is not None
```

---

### `with_test_worker: None`

Spawns a mock background worker thread (an RQ worker) that executes jobs synchronously in the main thread process. This allows you to test asynchronous background task flows (like email delivery or file parsing) inline.

```python
@pytest.mark.usefixtures("clean_queues", "with_test_worker")
def test_async_job():
    # Queue an asynchronous job
    tk.get_action("enqueue_job")(...)
    # Job executes synchronously and results are available instantly
```

---

### `clean_queues: None` and `reset_queues: ckan.types.FixtureResetQueues`

**`reset_queues`**: A session-scoped callable that empties and deletes all RQ background task queues.

**`clean_queues`**: Empties and clears RQ jobs queues before the test.

```python
@pytest.mark.usefixtures("clean_queues")
def test_queue_processing():
    # Queues start empty
    pass
```

---

### `mail_server`

Replaces `smtplib.SMTP` with a mock SMTP mail server, capturing all outgoing emails sent by the CKAN application during a test run.

```python
def test_notification_email(mail_server):
    # Trigger an action that sends an email
    call_action("user_invite", email="user@example.com")

    # Assert the captured mail server data
    assert len(mail_server.mails) == 1
    _, from_addr, to_addr, msg = mail_server.mails[0]
    assert to_addr == "user@example.com"
```


---

### `create_with_upload`

A session-scoped shortcut helper that generates a mock file storage payload (using `werkzeug.datastructures.FileStorage`) and uploads it by calling a creation action (defaults to `resource_create`).

```python
def test_file_resource(create_with_upload, package: dict[str, Any]):
    resource = create_with_upload(
        data="file content line",
        filename="data.txt",
        package_id=package["id"]
    )
    assert resource["url_type"] == "upload"
    assert resource["size"] == 17
```

---

### `reset_storages: ckan.types.FixtureResetStorages`

Reload file storages using updated configuration.

```python
def test_storage_override(ckan_config, monkeypatch, reset_storages):
    monkeypatch.setitem(ckan_config, "ckan.storage_path", "/tmp/custom")
    reset_storages()
```

Always invoke `reset_storages` if your test dynamically changes any
configuration variable starting with `ckan.files.storage.` or
`ckan.storage_path` to ensure the storage system applies the configuration
change.
