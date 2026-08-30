# CKAN Extension Guidelines

This repository contains documentation, standards, and guidelines for
modernizing CKAN (Comprehensive Knowledge Archive Network) extensions to align
with modern Python, JavaScript, and developer tooling standards.

---

## Documentation Categories

The guidelines are split into five main sections:

* **[Get Started](docs/index.md)**: Introduction to modernization principles,
  deprecation timelines, and core migration plans.
* **[Environment](docs/environment/)**: Developer tools setup, requirements
  management, Gulp task flows, Vite and TypeScript compilations, matrix GitHub
  Actions workflows, PyPI packaging, and Docker development environments.
* **[Development](docs/development/)**: Extension structure, writing
  declarative actions, validators, blueprints, CLI commands, database models
  using SQLAlchemy types, alembic migrations, blinker signals, and template
  helpers.
* **[Testing](docs/testing/)**: Guide on writing tests with Pytest. Includes
  details on factories, fixtures (like `tmp_path`, `ckan_config`, `app`,
  `cli`), views testing with BeautifulSoup, mock workers, and E2E testing using
  Playwright and Cypress.
* **[Frontend](docs/frontend/)**: Asset pipelines, Jinja2 template inheritance,
  custom WebAssets integration, and compiling JavaScript/CSS.
* **[Integrations](docs/integrations/)**: Community-contributed guides for
  integrating popular third-party extensions.

---

## Local Development

Use Python v3.10 or newer.

Install the required packaging dependencies inside your Python virtual environment:

```sh
# Using Make
make install

# Direct command
pip install zensical
```

To preview the documentation locally with hot-reloading:

```bash
# Using Make
make serve

# Direct command
zensical serve
```

Open [http://localhost:8000](http://localhost:8000) in your web browser to view the site.

## Contributions

These guidelines are community-maintained. If you find missing parameters,
outdated configurations, or spelling errors, please submit a pull request or
contact the maintainers.
