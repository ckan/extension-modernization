---
icon: lucide/hammer
---

# Package configuration

Migrating your CKAN extension's package configuration from legacy setups
(`setup.py` or `setup.cfg`) to the modern `pyproject.toml` format (conforming
to [PEP 518][pep-518] and [PEP 621][pep-621]) is a key step in modernization. This transition
simplifies dependencies, standardizes packaging metadata, and prepares your
extension for modern Python packaging tools.

[pep-518]: https://peps.python.org/pep-0518/
[pep-621]: https://peps.python.org/pep-0621/

---


## Metadata and Dependencies

Below is a comparison showing how legacy packaging files translate into a modern `pyproject.toml`.

=== "setup.py"

    ```python title="setup.py"
    from setuptools import setup, find_packages

    setup(
        name='ckanext-myextension',
        version='0.1.0',
        description='A CKAN extension',
        long_description='A longer description',
        author='John Doe',
        author_email='john@example.com',
        url='https://github.com/my/ckanext-myextension',
        license='AGPL',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        namespace_packages=['ckanext'],
        zip_safe=False,
        install_requires=[
            'requests',
            'pandas',
        ],
    )
    ```


=== "setup.cfg"

    ```ini title="setup.cfg"
    [metadata]
    name = ckanext-myextension
    version = 0.1.0
    description = A CKAN extension
    long_description = file: README.md
    long_description_content_type = text/markdown
    author = John Doe
    author_email = john@example.com
    url = https://github.com/my/ckanext-myextension
    license = AGPL

    [options]
    packages = find_namespace: # (1)!
    install_requires =
        requests
        pandas

    [options.packages.find]
    exclude =
        tests
        tests.*
    ```

    1.  Uses `find_namespace:` to automatically discover package directories (including `ckanext` namespaces).

=== "pyproject.toml"

    ```toml title="pyproject.toml"
    [build-system]
    requires = ["setuptools>=61.0.0", "wheel"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "ckanext-myextension"
    version = "0.1.0"
    description = "A CKAN extension"
    readme = "README.md"
    authors = [
        { name = "John Doe", email = "john@example.com" }
    ]
    license = { text = "AGPL" }
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ]
    keywords = [ "CKAN", "extension"]
    dependencies = [
        "requests",
        "pandas",
    ]
    requires-python = ">=3.10"

    [project.urls]
    Homepage = "https://github.com/my/ckanext-myextension"

    [tool.setuptools.packages]
    find = {}
    ```

---

## Entry Points

CKAN extensions register their plugins, command line interfaces, and translation extractors via Python entry points.

=== "setup.py"

    ```python title="setup.py"
    setup(
        # ...
        entry_points='''
            [ckan.plugins]
            myextension=ckanext.myextension.plugin:MyPlugin

            [babel.extractors]
            ckan = ckan.lib.extract:extract_ckan
        ''',
    )
    ```

=== "setup.cfg"

    ```ini title="setup.cfg"
    [options.entry_points]
    ckan.plugins =
        myextension = ckanext.myextension.plugin:MyPlugin
    babel.extractors =
        ckan = ckan.lib.extract:extract_ckan
    ```

=== "pyproject.toml"

    ```toml title="pyproject.toml"
    [project.entry-points."ckan.plugins"]
    myextension = "ckanext.myextension.plugin:MyPlugin"

    [project.entry-points."babel.extractors"]
    ckan = "ckan.lib.extract:extract_ckan"
    ```

---

## Babel Internationalization (i18n)

Historically, CKAN extensions specified extraction mappings using the
`message_extractors` configuration inside `setup.py`. Integration with
setuptools is still required, but we aim for eventual switch to
`pyproject.toml`, when babel [fully supports
it](https://github.com/python-babel/babel/issues/777).


/// admonition | Babel Configuration Migration
    type: info

Create a `babel.cfg` file in the root of your extension to specify what files and templates to parse. Move `message_extractors` configuration from `setup.py` to `babel.cfg`. Typically you'll see following lines in the `setup.py`:

```py
setup(
    message_extractors={
        "ckanext": [
            ("**.py", "python", None),
            ("**.js", "javascript", None),
            ("**/templates/**.html", "ckan", None),
        ],
    }
)
```


This translates to the following `babel.cfg`:

```ini title="babel.cfg"
[python: **.py]
[javascript: **.js]
[ckan: **/templates/**.html] # (1)!
```

1. `ckan` extractor is basically a `jinja2` extractor that loads all Jinja2 extensions used by CKAN.

Register the custom `ckan` extractor under `[project.entry-points."babel.extractors"]` in your `pyproject.toml` (as shown above).

Update `setup.cfg`. It already should contain following lines:

```cfg title="setup.cfg"
[extract_messages]
keywords = translate isPlural
add_comments = TRANSLATORS:
output_file = ckanext/myext/i18n/ckanext-myext.pot
width = 80

[init_catalog]
domain = ckanext-myext
input_file = ckanext/myext/i18n/ckanext-myext.pot
output_dir = ckanext/myext/i18n

[update_catalog]
domain = ckanext-myext
input_file = ckanext/myext/i18n/ckanext-myext.pot
output_dir = ckanext/myext/i18n
previous = true

[compile_catalog]
domain = ckanext-myext
directory = ckanext/myext/i18n
statistics = true
```

You need to add `mapping_file` reference to the new `babel.cfg` under `extract_messages` section:

```cfg title="Updated setup.cfg"
[extract_messages]
mapping_file = babel.cfg
keywords = translate isPlural
...
```

Now you can perform extraction using setuptools integration:
```sh
python setup.py extract_messages
```

You can also use standard `pybabel` commands, but in this way configuration
from `setup.cfg` will not be taken into account:

```bash
pybabel extract -F babel.cfg -o ckanext/myextension/i18n/myextension.pot .
```

///


---

## Python namespaces

CKAN extensions are relying on legacy namespace definitions. To make package
discoverable and avoid conflicts with other packages, make sure you have
following lines in `setup.cfg` and `pyproject.toml`:

```cfg title="setup.cfg"
[options]
namespace_packages = ckanext  # (1)!
```

1. This option has no analogues for `pyproject.toml` and must be kept inside `setup.cfg`

```toml title="pyproject.toml"
[tool.setuptools.packages]
find = {}  # (1)!
```

1. This option is responsible for automatic package discovery.

/// note

To keep related options in same file, you can move `tool.setuptools.packages`
from `pyproject.toml` to `setup.cfg`

```cfg title="setup.cfg"
[options]
packages = find:
namespace_packages = ckanext
```

///

---

## Final version

When migration completed, you should have following content in specified files

=== "setup.py"

    Content from here is distributed between other files. Still, `setup.py` with the minimal content is required by setuptools.

    ```py title="setup.py"
    from setuptools import setup

    setup()
    ```

=== "babel.cfg"

    This was specified inside `setup.py` in past. You can keep these options inside `setup.py`, but moving them to a separate file will may reduce friction if future and reduce depenency on setuptools.

    ```cfg title="babel.cfg"
    [python: **.py]
    [javascript: **.js]
    [ckan: **/templates/**.html]
    ```

=== "setup.cfg"

    This file contains the `options` section with legacy namespace-specific configuration that cannot be moved to `pyproject.toml`. In future, if CKAN extensions move to [PEP 420](https://peps.python.org/pep-0420/) or stop using namespaces at all, this section can be dropped.

    Additionally it contains babel configuration under `extract_messages`, `init_catalog`, `update_catalog`, `compile_catalog` sections. These sections may move to `pyproject.toml` when babel will improve its support.

    ```cfg title="setup.cfg"
    [options]
    namespace_packages = ckanext

    [extract_messages]
    mapping_file = babel.cfg
    keywords = translate isPlural
    add_comments = TRANSLATORS:
    output_file = ckanext/myextension/i18n/ckanext-myextension.pot
    width = 80

    [init_catalog]
    domain = ckanext-myextension
    input_file = ckanext/myextension/i18n/ckanext-myextension.pot
    output_dir = ckanext/myextension/i18n

    [update_catalog]
    domain = ckanext-myextension
    input_file = ckanext/myextension/i18n/ckanext-myextension.pot
    output_dir = ckanext/myextension/i18n
    previous = true

    [compile_catalog]
    domain = ckanext-myextension
    directory = ckanext/myextension/i18n
    statistics = true

    ```

=== "pyproject.toml"

    This is the main source for package's metadata. Prioritize it over other formats when adding new package's metadata or configuring additional tool.

    ```toml title="pyproject.toml"
    [project]
    name = "ckanext-myextension"
    version = "0.1.0"
    description = "Description of the project"
    readme = "README.md"
    license = {text = "AGPL"}
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
    ]

    keywords = [ "CKAN", ]
    dependencies = ["typing_extensions"]

    authors = [
        {name = "John Doe", email = "john@example.com"},
    ]
    maintainers = [
        {name = "John Doe", email = "john@example.com"},
    ]

    [project.urls]
    Homepage = "https://github.com/my/ckanext-myextension"
    Documentation = "https://my.github.io/ckanext-myextension/"

    [project.entry-points."ckan.plugins"]
    myextension = "ckanext.myextension.plugin:MyPlugin"

    [project.entry-points."babel.extractors"]
    ckan = "ckan.lib.extract:extract_ckan"

    [project.optional-dependencies]
    test = ["pytest-ckan", "pytest-pretty", "pytest-playwright"]
    docs = ["zensical"]
    dev = ["pytest-ckan", "pytest-pretty", "zensical", "pre-commit", "pytest-playwright"]

    [build-system]
    requires = ["setuptools"]
    build-backend = "setuptools.build_meta"

    [tool.setuptools.packages]
    find = {}

    ```

## Automated Migration with `ini2toml`

If you already have a `setup.cfg` file, you can automate a large part of the migration using the `ini2toml` tool. It parses the INI/CFG syntax and translates metadata and options to the equivalent `pyproject.toml` specifications.

### Step 1: Install `ini2toml`

It is recommended to install the tool with the `[full]` extra options to ensure comments are preserved and formatting is optimized:

```bash
pipx install "ini2toml[full]"
# OR
pip install "ini2toml[full]"
```

### Step 2: Convert `setup.cfg`

Run `ini2toml` targeting your `setup.cfg` and outputting the result to `pyproject.toml`:

```bash
ini2toml setup.cfg -o pyproject.toml
```

/// admonition | Converting `setup.py` directly
    type: warning

`ini2toml` only supports converting `.cfg` or `.ini` files. It **cannot** parse
or translate python code from `setup.py`. If your extension only has a
`setup.py`, you should:

1. convert your `setup.py` to `setup.cfg` using a tool like
   [setup-py-upgrade](https://github.com/asottile/setup-py-upgrade) or
   [setutools-py2cfg](https://pypi.org/project/setuptools-py2cfg/).

2. translate the parameters manually into a new `pyproject.toml` following the examples above.

///

### Step 3: Verify and Clean Up

After generating the `pyproject.toml` file:

1. **Review the contents**: Ensure that the tool has correctly moved standard
   metadata into the `[project]` table and `setuptools`-specific rules into
   `[tool.setuptools]`.

2. **Test build execution**: Run standard packaging validations to verify your new configuration:
   ```bash
   pip install -e .
   ```
3. **Delete legacy configurations**: Once verification succeeds, remove
   unnecessary section from `setup.cfg` and `setup.py` files to finalize the
   modernization.
