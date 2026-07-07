---
icon: lucide/git-merge
---

# GitHub CI/CD Workflows

To ensure code quality and prevent regressions, CKAN extensions run
automated checks on every push and pull request. This includes code syntax
linting and containerized test execution.

This guide outlines the standard GitHub Actions workflows configuration based on the patterns found in [test.yml (ckanext-theming)](file:///home/sergey/projects/core/ckanext-theming/.github/workflows/test.yml) and [test.yml (ckanext-files)](file:///home/sergey/projects/core/ckanext-files/.github/workflows/test.yml).

---

## Workflow Structure

Workflows are defined in YAML files under the `.github/workflows/` directory:

```
ckanext-myextension/
└── .github/
    └── workflows/
        └── test.yml           # Core linting and testing workflow
```

Typically, the workflow consists of two main jobs:

1. **`lint`**: A fast syntax and formatting check running directly on the runner.
2. **`test`**: A comprehensive container-based test execution environment with dedicated database and search services.

And it's recommended to add `publish` job, that uploads package to PyPI anytime
you create a new version tag. Check [publishing guide](publishing) for more
details.

---

## Code Linting (`lint`)

The linting job checks formatting rules and flags code complexity issues using **Ruff** (configured in your `pyproject.toml`).

```yaml title=".github/workflows/test.yml"
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Setup Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Ruff Check
        uses: astral-sh/ruff-action@v4.1.0
```

/// admonition
    type: info

You can use flake8 instead of ruff

```yaml title=".github/workflows/test.yml"
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Setup Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Install requirements
        run: pip install flake8

      - name: Check syntax
        run: flake8 . --count --select=E901,E999,F821,F822,F823 --show-source --statistics
```

///

---

## Container-Based Testing (`test`)

Running CKAN tests requires PostgreSQL, Solr, and Redis. Setting these up
manually on a GitHub Actions runner is complex and slow.

CKAN extensions run tests **inside** the official `ckan/ckan-dev` container
images, linking dedicated service containers.

### Configuration Template

```yaml title=".github/workflows/test.yml (continued)"
  test:
    strategy:
      matrix:
        ckan-version: ["2.10", "2.11", "2.12"] # Test against multiple versions
      fail-fast: false

    runs-on: ubuntu-latest
    container:
      # Run all steps inside the ckan-dev container
      image: ckan/ckan-dev:${{ matrix.ckan-version }}
      options: --user root

    services:
      # Dedicated Solr search index container
      solr:
        image: ckan/ckan-solr:${{ matrix.ckan-version }}-solr9

      # PostgreSQL database container
      postgres:
        image: ckan/ckan-postgres-dev:${{ matrix.ckan-version }}
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: postgres
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

      # Redis cache container
      redis:
        image: redis:7

    # Configure connection URLs for the containers
    env:
      CKAN_SQLALCHEMY_URL: postgresql://ckan_default:pass@postgres/ckan_test
      CKAN_DATASTORE_WRITE_URL: postgresql://datastore_write:pass@postgres/datastore_test
      CKAN_DATASTORE_READ_URL: postgresql://datastore_read:pass@postgres/datastore_test
      CKAN_SOLR_URL: http://solr:8983/solr/ckan
      CKAN_REDIS_URL: redis://redis:6379/1

    steps:
      - uses: actions/checkout@v7

      - name: Install requirements
        run: |
          # Installs the extension and its test dependencies
          pip install -e ".[dev,test]"

      - name: Setup test configuration
        run: |
          # CRITICAL: Replace default test-core ini path with the path on the dev container
          sed -i -e 's/use = config:.*/use = config:\/srv\/app\/src\/ckan\/test-core.ini/' test.ini

      - name: Initialize DB
        run: |
          ckan -c test.ini db init

      - name: Run tests
        run: |
          # Execute pytest and output coverage XML
          pytest --ckan-ini=test.ini --cov=ckanext.myextension --cov-report=xml --disable-warnings

      - name: Upload coverage reports to Codecov
        uses: codecov/codecov-action@v7
        if: ${{ !cancelled() }}
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
```

---

## Key Configurations Explained

### A. The `test-core.ini` Override (`sed` command)
Your local `test.ini` contains `use = config:../ckan/test-core.ini` pointing to your local CKAN core directory.

On the GitHub container, CKAN core is located at `/srv/app/src/ckan/`. The `sed` step rewrites the configuration path so that the test harness finds the correct test configuration within the container:
```bash
sed -i -e 's/use = config:.*/use = config:\/srv\/app\/src\/ckan\/test-core.ini/' test.ini
```

### B. Matrix Testing
The `strategy.matrix` allows you to run identical test suites simultaneously against different CKAN releases (e.g., `2.10`, `2.11`, or `master`). This immediately flags backward compatibility issues when new versions of CKAN are released.

### C. Services Networking
Because the job runs inside a container, services defined in the workflow (like `solr` and `postgres`) are available on the network under their service keys (`http://solr:8983`, `postgres://...`). The environment variables under `env` tell CKAN how to connect to these services.
