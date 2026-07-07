---
icon: lucide/terminal
---

# JavaScript & Module System

CKAN uses a client-side module system to initialize, manage, and isolate page
scripts. Extensions compile modular TypeScript into self-executing IIFE
bundles, integrating with CKAN's module registry.

---

## CKAN Module System Basics

In CKAN, scripts are declared as modules using `ckan.module()`. These modules are bound to specific HTML elements in your template using the `data-module` attribute:

### The Template element
```html
<div data-module="myextension-counter" data-module-initial-count="5">
    <button class="btn-increment">Increment</button>
    <span class="count-display">5</span>
</div>
```

### The Module script
```javascript
ckan.module("myextension-counter", function ($, _) {
  return {
    options: {
      initialCount: 0,
    },
    count: 0,

    initialize() {
      this.count = this.options.initialCount;
      this.el.on("click", ".btn-increment", this._onIncrement.bind(this));
    },

    teardown() {
      this.el.off("click");
    },

    _onIncrement(event) {
      event.preventDefault();
      this.count++;
      this.el.find(".count-display").text(this.count);
    }
  };
});
```

---

## Using the Sandbox

Every CKAN module is instantiated with a `sandbox` object, which provides isolated utility methods and communication interfaces.

### A. AJAX Actions (`sandbox.client`)
Use `sandbox.client` to call CKAN's API actions from JavaScript:
```javascript
this.sandbox.client.call(
  "POST",
  "myextension_item_show",
  { id: "123" },
  function(result) { console.log("Success:", result.result); },
  function(error) { console.error("Error:", error); }
);
```

### B. Pub/Sub Events (`sandbox.publish` / `sandbox.subscribe`)
Modules should not communicate directly. Instead, they publish events to a shared topic or subscribe to topics:
```javascript
// Module A (Publishing)
this.sandbox.publish("dataset:update", { id: "dataset-id" });

// Module B (Subscribing)
this.sandbox.subscribe("dataset:update", function(data) {
  console.log("Dataset updated:", data.id);
});
```

---

## Writing TypeScript Modules

Writing modules in TypeScript prevents reference bugs and ensures type checking. By defining custom global typings, you can utilize `ThisType<T & IModule>` to provide auto-completions for variables inside your module definitions.

### Typical Module Code

```typescript title="assets/ts/module-uploader.ts"
// Fully typed CKAN module
window.ckan.module("myextension-uploader", function ($) {
  return {
    options: {
      targetInput: "input[type=file]",
    },
    queue: new Set<File>(),

    initialize() {
      // 'this.el' (JQuery) and 'this.options' are fully type-safe
      this.el.on("change", this.options.targetInput, this._onFileSelected);
    },

    _onFileSelected(event: Event) {
      const input = event.target as HTMLInputElement;
      if (input.files) {
        Array.from(input.files).forEach(file => this.queue.add(file));
      }
      // 'this.sandbox' is typed
      this.sandbox.publish("upload:queue_updated", { size: this.queue.size });
    }
  };
});
```

Refer to the [Vite & TypeScript Guide](../environment/vite-typescript.md) for compiling these modules and setting up global TypeScript declaration files.
