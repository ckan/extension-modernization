---
icon: lucide/file-type-2
---

# Vite & TypeScript

If you wonder how you can improve quality of JavaScript code inside your
extension, try using **Vite** and **TypeScript**.

Writing scripts in TypeScript ensures type safety, IDE autocompletions, and
robust compile-time error checking, while Vite bundles the code into optimized,
browser-compatible modules.

## Installation

To configure Vite and TypeScript, you need the bundler, the compiler, and
jquery types(because CKAN includes jQuery). All of them can be installed via
NPM:

```sh
npm i -d vite \
         typescript \
         @types/jquery
```

This command will initialize or update your `package.json` file, and install
local development dependencies inside `node_modules/`.

---

## Configuration

Vite is used to collect and combide scripts and other things into a
fully-functional web application. We are not going to use its full potential
and focus only on compiling typescript into javascript. Create the
`vite.config.ts` and `tsconfig.json` configurations next to the `package.json`:

```
ckanext-myextension/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── ckanext/
    └── myextension/
        └── assets/
            ├── script.js             # Compiled webassets output
            └── ts/                   # TypeScript source files
                ├── main.ts
                ├── types.ts          # Global CKAN typings
                └── my-module.ts
```

### Vite Configuration (`vite.config.ts`)

CKAN uses WebAssets to concatenate multiple scripts. To prevent concatenation
errors, Vite must be configured to bundle code as a single Immediately Invoked
Function Expression (IIFE) and prepend a semicolon using a custom plugin. In
this way, even when CKAN combine all scripts into a single line of code, they
will be interpreted correctly.

/// admonition | `vite.config.ts` configuration used to compile and bundle TypeScript scripts.
    type: example

```typescript title="vite.config.ts"
import { defineConfig } from "vite";
import { resolve } from "path";

// compute absolute path to the assets directory
const assets = resolve(__dirname, "ckanext/myextension/assets");

export default defineConfig({
  publicDir: false, // (1)
  plugins: [
    {
      name: "prepend-semicolon",
      generateBundle(options, bundle) {
        // (2)
        for (const chunk of Object.values(bundle)) {
          if (chunk.type === "chunk") {
            chunk.code = ";" + chunk.code + "\n";
          }
        }
      },
    },
  ],

  build: {
    lib: {
      entry: resolve(assets, "ts/main.ts"), // (3)
      formats: ["iife"], // (4)
      fileName: (format) => `script.js`,
      name: "MyExtensionUI",
    },
    outDir: resolve(assets), // (5)
    emptyOutDir: false,
  },
});
```

1. Disable erasing the public directory to prevent Vite from rewriting or
   clearing static assets (like images) placed in `assets/public/`.
2. Prepend a semicolon `;` before the IIFE chunk.
3. Define the main entry point file. This file must import all other TypeScript modules.
4. Output the build format as an IIFE (Immediately Invoked Function Expression) so it can run directly in browsers without module loaders.
5. Write the compiled JavaScript directly into the `assets/` folder.

///

---

### TypeScript Configuration (`tsconfig.json`)

`tsconfig.json` defines how the TypeScript compiler processes your code and resolves type dependencies (like jQuery).

/// admonition | `tsconfig.json` template used to configure compilation options.
    type: example

```json title="tsconfig.json"
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "target": "es2020",
    "module": "preserve",
    "outDir": "ckanext/myextension/assets/",
    "types": ["jquery"], // (1)
    "strict": true, // (2)
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "inlineSources": true,
    "inlineSourceMap": true
  },
  "include": ["ckanext/myextension/assets/ts/*.ts"]
}
```

1. Load typing declarations for jQuery globally so that `$` behaves as a typed jQuery instance.
2. Enable strict type checking for safer and cleaner JavaScript.

///

---

### Entrypoint File (`ts/main.ts`)

Vite bundles all JavaScript assets by starting at a single entrypoint file and recursively resolving its imports. In your extension, this entrypoint imports all individual script files and CKAN modules to ensure they are compiled into the final browser bundle.

/// admonition | `main.ts` entrypoint file compiling and aggregating separate modules.
    type: example

```typescript title="assets/ts/main.ts"
/// <reference path="./types.ts" /> // (1)

// 2. Import modules and components
import "./module-uploader";
import "./module-dropzone";
import "./module-scheduler";
```

1. Links global typings for the CKAN sandbox and module system.
2. Every script file that needs to be included in the final compiled bundle must be imported here.

///

---

## Key Settings & Workarounds

### A. The Concatenation Workaround (Prepended Semicolon)

CKAN's WebAssets combines multiple JavaScript files from different extensions into a single asset file.

If a script file from a preceding extension does not end with a semicolon, and
your script starts with an IIFE parenthesis `(function(){ ... })()`, the
browser interpreter will merge them and attempt to evaluate the preceding
script output as a function:

```javascript
// Result of merging without a semicolon (causes runtime syntax errors):
(function(){ /* previous script */ })()(function(){ /* your script */ })()
```

Prepending `;` before the compiled IIFE guarantees that the script blocks are
parsed as separate statements:

```javascript
// Result of merging with prepend-semicolon:
(function(){ /* previous script */ })();(function(){ /* your script */ })()
```

### B. Typing the CKAN Module System (`types.ts`)

CKAN does not provide official TypeScript definitions. Extensions define
these globals manually in `assets/ts/types.ts`.

```typescript title="assets/ts/types.ts"
export {};

declare global {
  interface ISandbox {
    notify: {
      initialize: (element: HTMLElement | JQuery) => JQuery;
      create: (title: string, message: string, type?: string) => JQuery;
    };
    client: {
      url(path: string): string;
      call(type: "POST" | "GET", path: string, data?: object, success?: Function, error?: Function): void;
    };
    jQuery: JQueryStatic;
    publish(topic: string, ...args: any[]): void;
    subscribe(topic: string, callback: Function): void;
  }

  interface IModule {
    $: JQueryStatic;
    el: JQuery;
    sandbox: ISandbox;
    initialize(): void;
    teardown?(): void;
  }

  interface ICkan {
    sandbox: {
      setup: (callback: (sandbox: ISandbox) => void) => void;
      (): ISandbox;
    };
    module: <T extends object>(
      name: string,
      initializer: ($: JQueryStatic) => T & ThisType<T & IModule>
    ) => any;
  }

  interface Window {
    ckan: ICkan;
  }
}
```

---

## Example: Typing in Action

This example demonstrates how to enable type declarations in your TypeScript files and how compile-time type-safety prevents common JavaScript bugs.

### Enabling Types in Module Files

There are two ways to tell the TypeScript compiler about the global `ckan` and `sandbox` declarations defined in `types.ts`:

* **Automatic Resolution (Recommended)**: Since `tsconfig.json` includes the source directory (`"include": ["ckanext/myextension/assets/ts/*.ts"]`), the compiler automatically loads `types.ts` globally. You don't need any import or reference statements in your modules.
* **Explicit Reference Directive**: If you have files outside the configured `include` paths, add a triple-slash reference directive at the very top of your file:
  ```typescript
  /// <reference path="./types.ts" />
  ```

---

### How TypeScript Helps You Code

Below is an example showing how the compiler guides developers, catches parameter errors, and provides autocompletions.

```typescript title="assets/ts/my-module.ts"
window.ckan.module("myextension-uploader", function ($) {
  return {
    options: {
      action: "files_file_create",
      selector: ".btn-upload",
    },

    initialize() {
      // 1. Autocomplete: typing 'this.el.' will suggest JQuery methods like 'on', 'off', 'find'
      this.el.on("click", this.options.selector, this._onClick);

      // 2. Typo Protection:
      // If you type 'this.options.actions' (plural), the compiler throws:
      // Property 'actions' does not exist on type '{ action: string; selector: string; }'
      console.log(this.options.action);
    },

    _onClick(event: Event) {
      event.preventDefault();

      // 3. API Parameter Check:
      // If you attempt to call the API with incorrect arguments:
      // 'this.sandbox.client.call("POST", this.options.action, "invalid_payload")'
      // The compiler will highlight "invalid_payload" and fail:
      // Argument of type 'string' is not assignable to parameter of type 'object | undefined'
      this.sandbox.client.call(
        "POST",
        this.options.action,
        { storage: "default" }, // Correct payload object
        (result: any) => {
          this.sandbox.publish("upload:success", result);
        }
      );
    }
  };
});
```

---

## Run Tasks

To run the compilation and bundle your scripts:

```sh
# Compile assets once
npx vite build

# Run compilation in watch mode (recompiles automatically when files are modified)
npx vite build -w
```

You can add these commands to your `package.json` script registry:

```json title="package.json"
{
  "scripts": {
    "build-scripts": "vite build",
    "watch-scripts": "vite build -w"
  }
}
```

This lets you run them via `npm run build-scripts` or `npm run watch-scripts`.

Alternatively, if you use a `Makefile` to unify commands, add these rules:

```makefile title="Makefile"
watch-scripts:  ## Watch and recompile TypeScript modules
	npx vite build -w

compile-scripts:  ## Compile production JavaScript bundle
	npx vite build
```
