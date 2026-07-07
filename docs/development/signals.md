---
icon: lucide/radio-receiver
---

# Signals & Event Handling

CKAN signals provide a publish-subscribe (event notification) mechanism powered
by the **Blinker** library. This allows extensions to observe and react to core
application events (like user registration, logins, or datastore updates)
without modifying core code or interrupting execution flows.

This guide covers how to subscribe to signals, emit custom events, and
understand when to use signals instead of CKAN plugin interfaces.

---

## Signals vs. Interfaces

While both interfaces and signals allow extensions to hook into CKAN, they have different design patterns:

| Feature                  | Signals (Blinker)                                          | Interfaces (Plugins)                                                    |
|:-------------------------|:-----------------------------------------------------------|:------------------------------------------------------------------------|
| **Primary Intent**       | Observation & Side-effects                                 | Extension, Modification & Flow Control                                  |
| **Data Alteration**      | Should **never** modify arguments or payloads [^1]         | Often designed to mutate datasets/configs                               |
| **Execution Flow**       | Cannot abort requests or alter responses                   | Can return responses or raise abort errors                              |
| **Execution Order**      | Undefined and parallel                                     | Often determined by plugin loading order                                |
| **Dependency on plugin** | If plugin that emits signal is not loaded, nothing happens | `ImportError` if you are trying to import interface from missing plugin |


When you are creating an extension and want to introduce a hook:

* **Use Signals** when you want to observe an action to perform a secondary,
  independent task (e.g. sending a welcome email after `user_created` fires, or
  logging actions).
* **Use Interfaces** when you need to change how CKAN behaves (e.g. changing
  authorization logic using `IAuthFunctions`, or modifying schemas with
  `IDatasetForm`).

---

## Subscribing to Signals

To listen to signals, your extension's plugin should implement the `ISignal`
interface and declare its subscriptions in `get_signal_subscriptions()`.

### Code Example

```python title="plugin.py"
from typing_extensions import override

import ckan.plugins as p
import ckan.plugins.toolkit as tk


class NotificationPlugin(p.ISignal, p.SingletonPlugin):

    @override
    def get_signal_subscriptions(self) -> dict[p.Signal, list[p.SignalHandler]]:
        # Map signal instances to list of listener callback methods
        return {
            tk.signals.user_created: [self.on_user_created],
            tk.signals.failed_login: [self.on_failed_login],
        }

    def on_user_created(self, sender: str, **kwargs: Any) -> None:
        """Fires when a new user account is successfully registered."""
        # Always read kwargs defensively; signatures might evolve across CKAN versions
        user_dict = kwargs.get("user")
        if user_dict:
            username = user_dict.get("name")
            print(f"User created: {username} (Sender: {sender})")
            # Logic to enqueue welcome email goes here

    def on_failed_login(self, sender: str, **kwargs: Any) -> None:
        """Fires after a login attempt fails."""
        username = kwargs.get("username")
        print(f"Failed login attempt for username: {username}")
```

---

## Common Core Signals

Core signals can be referenced directly using `ckan.plugins.toolkit.signals`:

* **`request_started` / `request_finished`**: Triggered at the beginning and end of Flask HTTP requests.
* **`user_created`**: Sent after a new user record is successfully written to the database.
* **`user_logged_in` / `user_logged_out`**: Triggered on session change events.
* **`failed_login`**: Triggered when validation fails on a login attempt.
* **`action_succeeded`**: Sent after any logic action (e.g. `package_create`) completes successfully.
* **`datastore_upsert` / `datastore_delete`**: Sent after writing or deleting records in the datastore database.

---

## Declaring & Emitting Custom Signals

Extensions can define custom signals under the `ckanext` namespace to allow other plugins to hook into their internal processes.

### A. Define the Signal
Define your signals in a central file (e.g. `signals.py`) using `tk.signals.ckanext.signal()`:

```python title="signals.py"
import ckan.plugins.toolkit as tk

_doc = "Fires when an extension file upload completes successfully."
file_uploaded = tk.signals.ckanext.signal("files:uploaded", _doc)
```

### B. Emit the Signal
Trigger your event using the `.send()` method, specifying the sender name and key/value metadata:

```python title="logic/action.py"
from myextension.signals import file_uploaded

def myextension_file_create(context, data_dict):
    # ... file upload logic ...

    # Emit event notification
    file_uploaded.send(
        "myextension_uploader",
        file_id=file_id,
        size=file_size,
        owner=context.get("user")
    )
```

---

## Interchangeability Example

Sometimes you can achieve similar outcomes using either a Signal or an Interface.

For instance, if you want to execute code after a dataset is created:

### Option A: Using the `action_succeeded` Signal (Defensive, Observer Pattern)

Use this if your post-save action (like indexing details in an external
service) fails but should **not** interrupt the main CKAN transaction.

```python
def get_signal_subscriptions(self):
    return {
        tk.signals.action_succeeded: [self.after_action]
    }

def after_action(self, sender, **kwargs):
    action_name = kwargs.get("action_name")
    if action_name == "package_create":
        # Observe creation event safely
        pass
```

### Option B: Overriding Actions via `IActions` Interface (Active Middleware)

Use this if your post-save action is a mandatory requirement.

```python
class MyPlugin(p.SingletonPlugin):
    p.implements(p.IActions)

    def get_actions(self):
        return {"package_create": self.custom_package_create}

    def custom_package_create(self, context, data_dict):
        # 1. Run core logic
        result = tk.get_action("package_create")(context, data_dict)

        try:
            # 2. Run critical custom logic.
            self.perform_critical_task(result)
        except ...:
            # 3. Revert changes if task is failed
            ...
        return result
```

[^1]: Actually, you can modify payload of signal, but responsibility for any
    issue is yours.
