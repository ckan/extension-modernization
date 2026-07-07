---
icon: lucide/cog
---

# Gulp

CKAN theme extensions often contain stylesheets that grow over time.

For initial simplification of CSS files you can use available CSS features,
such as [`@scope`][scope], [nested rules][nested-classes] or
[CSS-functions][css-functions], that are widely supported in modern
browsers. For anything else, use [LESS][less], [SASS][sass], or
[Stilus][stilus]. SCSS is the most common choice across extensions, but nothing
stops you from using other preprocessors, as long as you don't need to modify
existing CSS framework.

[scope]: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@scope
[nested-classes]: https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Nesting/Using
[css-functions]: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/Functions
[less]: https://lesscss.org/
[sass]: https://sass-lang.com/
[stilus]: https://stylus-lang.com/

To further improve stylesheet processing, you can use task runner, such as
[Gulp][gulp]. For example, it can be used to compile, prettify, modernize, combine and
sort your SCSS files.

[gulp]: https://gulpjs.com/

## Installation

In order to use it, you need Gulp itself, and a number of additional
packages. All of them can be installed via NPM or similar package manager.

```sh
npm i -d gulp \
         gulp-clean-css \
         gulp-if \
         gulp-postcss \
         gulp-sass \
         gulp-sourcemaps \
         gulp-touch-fd \
         postcss-sort-media-queries \
         sass
```

This command will create `package.json` in the current directory, if you don't
have one yet. And it will add all the dependencies to it. Aditionally, it will
create `package-lock.json` and `node_modules/` folder where downloaded packages
are stored.

---

## Configuration (`gulpfile.js`)

Gulp is a task runner(somewhat similar to `GNU Make`, or python's
`Click`). Tasks are defined in the `gulpfile.js` which can be created next to
the `package.json`:

```
ckanext-midnight-blue-theme/
├── package.json
├── gulpfile.js
└── ckanext/
    └── myextension/
        ├── assets/
        │   ├── css/
        │   │   └── main.css  # Compiled output
        │   └── scss/         # SASS source files
        │       ├── main.scss
        │       └── main-rtl.scss
```


Inside `gulpfile.js` you define "tasks" - functions that are executed when you
"run task". For SCSS processing we are going to create two tasks:

* `build`: compile and minify SCSS into CSS
* `dev`: start a watcher that recompiles CSS whenever source SCSS is
  changed. Additionally it will include sourcemaps into output, so that you'll
  see the original SCSS inside your browser's development tools.

/// admonition | `gulpfile.js` configuration used to compile and optimize SASS code.
    type: example

```javascript title="gulpfile.js"
const { resolve } = require("path");
const { src, dest, watch } = require("gulp");

const if_ = require("gulp-if");
const sourcemaps = require("gulp-sourcemaps");
const sass = require("gulp-sass")(require("sass"));
const postcss = require("gulp-postcss");
const combineQueries = require("postcss-sort-media-queries");
const touch = require("gulp-touch-fd");
const cleanCSS = require("gulp-clean-css");

// Debug/Development flag
const isDev = () => !!process.env.DEBUG;

// compute absolute path to the source and target compilation directories
const assetsDir = resolve(__dirname, "ckanext/myextension/assets");
const srcDir = resolve(assetsDir, "scss");
const destDir = resolve(assetsDir, "css");

const build = () =>
  src([resolve(srcDir, "main.scss")]) // (1)!
    .pipe(if_(isDev, sourcemaps.init())) // (2)!

    .pipe(
      sass({
        loadPaths: ["node_modules"],  // (3)!
        silenceDeprecations: ["import", "legacy-js-api", "color-functions"],
      }).on("error", sass.logError),
    )

    .pipe(postcss([combineQueries])) // (4)!

    // Build optimization and minification
    .pipe(
      if_(
        isDev,
        sourcemaps.write(), // (5)!
        cleanCSS({ // (6)!
          level: 2,
          format: {
            breaks: { afterProperty: true, afterRuleBegins: true },
          },
        }),
      ),
    )

    .pipe(dest(destDir))

    // Force CKAN cache invalidation
    .pipe(touch()); // (7)!

const watchStyles = () =>
  watch(resolve(srcDir, "**/*.scss"), { ignoreInitial: false }, build);

exports.dev = watchStyles;
exports.build = build;
```

1. Specify source's entrypoint. If there are multiple entrypoints, like
   `main.scss` and `main-rtl.scss`, then can be provided as an array of
   filepaths.
2. Start collecting sourcemaps in development mode. This will be used by the
   `dev` task.
3. Allow including dependencies directly from `node_modules/`. In this way you
   can install bootstrap and include it without copying it into
   `assets/vendor/` of your extension.
4. Combine media-queries. For example, you can specify desktop styles via
   `@media (min-width: ...) {...}` in different places, and all of them will be
   aggregated inside a single media-query. Additionally, they will be sorted in
   mobile-first manner.
5. Add sourcemaps to the compiled CSS in dev mode.
6. Minify output in production mode, but keep line-breaks. This does not affect
   the filesize much, but reduces number of conflicts when merging
   pull-requests.
7. Sometimes gulp tends to skip updates of the file's modification
   time. Because of it, webassets may assume that styles were not changed and
   old version of styles will be served on the portal. To avoid this issue,
   enforce updating the modification time of the compiled file.

///

---

## Key Settings

### A. Environment Debugging (`isDev`)

The build pipeline checks the presence of the `DEBUG` environment variable
(`DEBUG=1 gulp build`).

- **In Development**: SASS source mapping is compiled alongside the CSS
  (`sourcemaps.write()`) to make inspection and debugging in the browser
  straightforward.
- **In Production**: Stylesheets are optimized and minified using `cleanCSS`
  (optimizations Level 2) for minimum file sizes.

### B. Dependency SASS Imports (`loadPaths`)

By configuring `loadPaths: ["node_modules"]` in the `sass` options, developers
can directly `@import` or `@use` design systems, fonts, or frameworks installed
via NPM without hardcoding absolute file paths (e.g., `@import
"bootstrap/scss/bootstrap"`).

### C. Media Query Sorting (`postcss-sort-media-queries`)

In modular responsive designs, `@media` rules are defined inline within
multiple components. PostCSS groups all identical media query breakpoints into
a single rule block at the end of the compiled CSS file, sorting them
mobile-first to ensure proper CSS specificity.

### D. WebAssets Cache Invalidation (`touch()`)
CKAN's WebAssets library packages assets and caches them aggressively. WebAssets uses the file modification time (`mtime`) on disk to detect changes.

Because Gulp compilation runs quickly, files may sometimes be written without changing the timestamps significantly. The `gulp-touch-fd` pipeline (via `.pipe(touch())`) updates the modification date of the output CSS files, forcing CKAN to invalidate its internal cache and serve the updated stylesheet immediately.

## Run tasks

To run the task execute

```sh
npx gulp build

# or
DEBUG=1 npx gulp dev
```

You can also check the list of available tasks:

```sh
npx gulp --tasks
```

According to the `gulpfile.js`, when you run any of these commands, Gulp will
compile `ckanext/myextension/assets/scss/main.scss` into
`ckanext/myextension/assets/css/main.css`.

You can also add these commands to `package.json`:

```json title="package.json"
...
    "scripts": {
        "build": "gulp build",
        "dev": "DEBUG=1 gulp dev"
    }
...
```

and execute tasks as `npm run build`/`npm run dev`. Note, you don't need to
specify `DEBUG=1` anymore, because it's added by the command definition inside
`package.json`.

Or, if you are using `Makefile` to unify task execution, it's also possible to
add rules there:

```make title="Makefile"
watch-styles:  ## watch and re-compile SCSS after every change
	DEBUG=1 npx gulp dev

compile-styles:  ## build production version of CSS assets
	npx gulp build
```
