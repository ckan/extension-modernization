---
icon: lucide/container
---

# Docker Development

Using Docker simplifies local development by isolating CKAN, PostgreSQL, Solr, and Redis. This guide provides a step-by-step walkthrough, starting with running a bare CKAN container stack manually, transitioning to a Docker Compose development environment, and configuring custom extensions.

---

## Running a Bare CKAN Instance with Docker Run

Before setting up a development workspace, you can spin up a clean, containerized CKAN instance manually using `docker run`. This helps verify that database, Solr, and Redis connections are configured correctly.

### Set Up a Docker Network
Create a dedicated network so the containers can resolve each other by name:

```bash
docker network create ckan-network
```

### Run Dependency Services
Start the PostgreSQL database, Solr search index, and Redis containers on the network:

```bash
# 1. Start PostgreSQL
docker run -d --name ckan-db \
  --network ckan-network \
  -e POSTGRES_USER=ckan \
  -e POSTGRES_PASSWORD=ckan_password \
  -e POSTGRES_DB=ckan_default \
  postgres:15

# 2. Start CKAN-compatible Solr
docker run -d --name ckan-solr \
  --network ckan-network \
  ckan/ckan-solr:2.10-solr9

# 3. Start Redis
docker run -d --name ckan-redis \
  --network ckan-network \
  redis:7-alpine
```

### Run the CKAN Container
Start the CKAN web container, mapping port 5000 and passing connection environment variables:

```bash
docker run -d --name ckan-web \
  --network ckan-network \
  -p 5000:5000 \
  -e CKAN_SQLALCHEMY_URL=postgresql://ckan:ckan_password@ckan-db/ckan_default \
  -e CKAN_SOLR_URL=http://ckan-solr:8983/solr/ckan \
  -e CKAN_REDIS_URL=redis://ckan-redis:6379/0 \
  -e CKAN_SITE_URL=http://localhost:5000 \
  ckan/ckan-base:2.10
```

Once started, navigate to [http://localhost:5000](http://localhost:5000) to view the clean, running CKAN portal.

---

## Transitioning to Docker Compose for Development

While `docker run` is useful for quick verification, active extension development is best managed using `docker-compose`. This automates mounting host directories, caching dependencies, and managing settings via environment files.

Initialize the standard development stack:

```bash
# Build and start the development containers in the background
bin/compose up -d
```

This starts the `ckan-dev` container, mapping your local workspace directories to the container filesystem.

---

## Mounting and Installing Local Extensions

To write code and test changes on your host machine, mount your extension's source directory and install it in editable mode inside the running development container.

### Step 1: Place Source Code
Clone your extension repository (e.g. `ckanext-scheming`) into the `src/` folder of your host `ckan-docker` workspace:

```
ckan-docker/
├── src/
│   └── ckanext-scheming/                 # Your extension source code
```

The container automatically maps the host `src/` folder to `/srv/app/src_extensions` inside the filesystem.

### Step 2: Install in Editable Mode
Run the installation helper script from the host to compile the extension and link it to the container's active Python virtual environment:

```bash
bin/install_src
```

This runs `pip install -e .` inside the container for all sub-folders found in `src_extensions/`.

### Step 3: Restart and Verify
Restart the container to force Gunicorn/Supervisor to reload the Python module path:

```bash
bin/restart
```

---

## Configuring Settings via Environment Variables

To register your extension's plugins or configure specific INI settings, use the `.env` file located in the root of your `ckan-docker` directory.

### Environment Variable Format
Settings are mapped to `ckan.ini` using the `ckanext-envvars` library. Convert settings to uppercase and replace dots (`.`) with double underscores (`__`):

```env
# Mappings to ckan.ini settings
CKAN__SITE_TITLE="My Local Portal"
CKAN___SCHEMING__DATASET_SCHEMAS=ckanext.scheming:ckan_dataset.json
```

!!! warning "Avoid INI Syntax in `.env` Files"
    Do not place raw `ckan.ini` key-value pairs (containing spaces or dots) directly inside the `.env` file. Doing so causes Docker Compose parsing errors. Always format them as standard shell variables.

---

## Enabling Plugins with `CKAN__PLUGINS`

If you add your extension's plugin to `.env` but find it is not active upon container boot, check the container logs:

```
[prerun] Setting the following plugins in /srv/app/ckan.ini: image_view text_view datastore datapusher envvars
```

### The Cause
The boot sequence writes the plugin list into the static `/srv/app/ckan.ini`
file before CKAN starts. In the official `ckan/ckan-base` and `ckan/ckan-dev`
images (2.9 to 2.12, built from the `ckan/ckan-docker-base` repository),
the **`prerun.py`** script reads it from the **`CKAN__PLUGINS`** (double
underscore) environment variable.
`CKAN_PLUGINS` (single underscore) is not read by these images.

If your plugin is missing from `CKAN__PLUGINS`, it is not written into
`ckan.ini` and is not loaded.

### The Fix
Add your plugin to `CKAN__PLUGINS` in your `.env` file:

```env
CKAN__PLUGINS=image_view text_view datastore datapusher envvars scheming_datasets
```

---

## Database Migrations for Extensions

If your extension requires custom database tables, run the alembic migrations from inside the container context:

```bash
# Open interactive shell in ckan-dev container
bin/compose exec ckan-dev /bin/bash

# Inside container: apply database migrations
ckan db upgrade -p my_plugin_name
```

---

## Running Pytest inside the Container

To execute your extension's test suite inside the container environment (with container-bound Postgres and Solr services):

```bash
# Execute pytest on your extension's tests directory
bin/compose exec ckan-dev pytest --ckan-ini=/srv/app/ckan.ini /srv/app/src_extensions/ckanext-scheming/ckanext/scheming/tests/
```
