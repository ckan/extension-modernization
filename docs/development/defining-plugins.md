---
icon: lucide/plug
---

# Defining Plugins

CKAN extensions register their entry points and central logic by defining
subclasses of `ckan.plugins.SingletonPlugin`. As extensions grow, `plugin.py`
can become bloated with boilerplate registration methods. CKAN extensions solve
this using **blanket decorators** and modular **implementations**.

---

## Plugin Structure

To keep your code clean, maintainable, and type-safe:

1. **Keep `plugin.py` light**: Define only the main plugin class and its
   interface registrations.
2. **Use blanket decorators**: Automatically register helpers, validators,
   actions, auth functions, CLI commands, and blueprints from their submodules.
3. **Use an `implementations/` submodule**: Extract the concrete methods
   required by CKAN interfaces (e.g. `IConfigurer`, `IPackageController`) into
   separate files under an `implementations/` package, rather than writing long
   helper methods inside `plugin.py`.

---

## Implementation Example

Here is how to set up a plugin using blanket decorators and the `implementations` module layout.


=== "plugin.py"

    Plugin is a main entry-point of the extension. When plugin does not do a lot,
    it makes sense to keep all the logic inside `plugin.py`. But when you feel that
    it becomes hard to manage, don't hesistate refactoring it and extracting logic
    into separate modules.

    ```python title="ckanext/myextension/plugin.py"
    from __future__ import annotations

    from typing_extensions import override

    import ckan.plugins as p
    import ckan.plugins.toolkit as tk

    # Import interface implementation module
    # with classes implementing specific interfaces
    from . import implementations

    @tk.blanket.helpers # (1)!
    @tk.blanket.actions
    @tk.blanket.cli
    @tk.blanket.blueprints
    class MyExtensionPlugin(
        implementations.PackageController, # (2)!
        p.IConfigurer, # (3)!
        p.SingletonPlugin,
    ):
        # p.implements(p.IConfigurer, inherit=True) # (4)

        # IConfigurer

        @override # (5)!
        def update_config(self, config: tk.CKANConfig):
            ...
    ```

    1. Blanket decorators automatically scan submodules (like `helpers.py`,
       `logic/action.py`, `cli.py`, `views.py`) and register _everything_ without
       manual boilerplate methods (like `get_helpers`, `get_actions`,
       etc.).
    2. Always add parent classes in this order: implementations, literal interfaces, `SingletonPlugin`. This guarantees expected method resolution order.
    3. As long as implementation is simple, it can be added directly into plugin.
    4. Avoid using `p.implements` and prefer extending interface classes for better typing support.
    5. Always add `@override` decorator to override method to guarantee warnings from type-checker if interface implemented in unexpected way.

=== "logic/action.py"

    All public members defined in the module will be registered by the blanket. Any
    imported function or function prefixed by `_` is considered an utility function
    and ignored by blanket implementation.

    ```py title="ckanext/myextension/logic/action.py"
    from __future__ import annotations

    from ckan import types

    def _ignored_by_blanket(): ...

    def myext_action(context: types.Context, data_dict: dict[str, Any]):
        ...
    ```

=== "cli.py"

    It's possible to specify the mebmers
    manually, by setting global `__all__` variable with names of all members that
    must be used by interface. Most commonly it's used inside `cli.py` as `#!py
    __all__ = ["my_main_command"]`, to avoid registering all the CLI groups
    globally.

    ```py title="ckanext/myextension/cli.py"
    import click

    __all__ = ["my_ext"]  # (1)!

    @click.group()
    def my_ext(): ...

    @my_ext.command()
    def my_command(): ...
    ```

    1. Without `__all__`, both functions, `my_ext` and `my_command` will be registered as separate top-level CLI commands.

=== "views.py"

    Blueprints blanket additionally filters public members by type and registers
    only `flask.Blueprint` descendants.

    Keep in mind, that only member defined inside `views` module will be
    registered. If you are importing blueprints from other submodules, you must
    manually add them to `__all__` or else they will be ignored by the blanket.

    ```py title="ckanext/myextension/views.py"

    from flask import Bluepint

    bp = Blueprint("my_ext", __name__)

    @bp.route("/my-ext")
    def index(): ... # (1)!
    ```

    1. `blueprints` blanked registers only `Blueprint` instances and it's safe to define any additional function inside this module.


=== "implementations/"

    This submodule contains complex implementations of interfaces. What exactly is
    considered a "complex implementation" is up to you to decide.

    ```py title="ckanext/myextension/implementations/__init__.py"

    # one module per interface; module name matches normalized
    # name of the interface without `I` prefix.
    from .package_controller import PackageController

    __all__ = [
        "PackageControler",
    ]
    ```

    Submodule with implementation contains only interface-specific code and
    helpers, nothing else.

    Functions that are used elsewhere, should be defined elsewhere. Keep
    implementation atomic and black-boxed: assume that only implementation class is
    defined here; any shared functionality must be defined inside a different
    module and imported into implementation, when required.

    ```py title="ckanext/myextension/implementations/package_controller.py"
    from __future__ import annotations

    from typing import Any
    from typing_extensions import override

    import ckan.plugins as p
    from ckan import types

    log = logging.getLogger(__name__)

    # Name implementation class as interface, without `I` prefix.
    class PackageController(p.IPackageController): # (1)!

        @override # (2)!
        def after_dataset_show(self, context: types.Context, pkg_dict: dict[str, Any]):
            ...

        @override
        def before_dataset_index(self, pkg_dict: dict[str, Any]):
            ...

        @override
        def create(self, entity: model.Package):
            ...

        @override
        def edit(self, entity: model.Package):
            ...

        @override
        def after_dataset_search(self, search_results: dict[str, Any], search_params: dict[str, Any]):
            ...

        @override
        def before_dataset_search(self, search_params: dict[str, Any]):
            ...

    ```

    1. Implementation extends only one interfaces and does not extends
       `SingletonPlugin`. The latter will be added to the main plugin and
       duplicating it inside implementations will only make MRO more entangled.
    2. Make a rule to add `@override` decorator whenever you override method defined in the parent class. It really pays off in long-term.
