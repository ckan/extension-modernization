---
name: ckan-docker-dev
description: Developing, mounting extensions, and configuring env variables inside the ckan-docker environment.
---

# CKAN Docker Development Guide

This skill provides comprehensive instructions on developing CKAN extensions inside Docker containers.

---

## Extension Installation Workflow

To develop an extension locally, place its source code in your host workspace and compile it into the development container.

1. **Volume Mount**: Place the extension source folder inside the host's `src/` directory (which maps to `/srv/app/src_extensions` inside the container).
2. **Compile Source**: Install the extension in editable mode inside the container:
   ```bash
   bin/install_src
   ```
3. **Restart Service**: Force Python's path registry to reload:
   ```bash
   bin/restart
   ```

---

## Environment Variables Mapping

Docker configurations are loaded from the local `.env` file and translated to `ckan.ini` keys via `ckanext-envvars`.

### Variable Conversion Format
* Convert keys to uppercase.
* Replace dots (`.`) with double underscores (`__`).
* Prepend `CKAN__` for core options and `CKAN___` for custom extension options.

| `ckan.ini` Option | `.env` Variable |
| :--- | :--- |
| `ckan.site_title` | `CKAN__SITE_TITLE` |
| `scheming.dataset_schemas` | `CKAN___SCHEMING__DATASET_SCHEMAS` |

```env
# Example configuration in .env
CKAN___SCHEMING__DATASET_SCHEMAS=ckanext.scheming:dataset.json
```

---

## The `CKAN_PLUGINS` vs. `CKAN__PLUGINS` Mismatch

To prevent plugin loading failures on container boot, understand the boot scripts.

* **`CKAN_PLUGINS` (Single Underscore)**: Read by the `prerun.py` startup script to write configurations to `/srv/app/ckan.ini` and run core DB migrations before CKAN boots.
* **`CKAN__PLUGINS` (Double Underscore)**: Read by `ckanext-envvars` at runtime inside the Python application.

Define **both** variables in your `.env` file to ensure the list of plugins matches between boot setup and application runtime:

```env
CKAN_PLUGINS=image_view text_view datastore datapusher envvars scheming_datasets
CKAN__PLUGINS=image_view text_view datastore datapusher envvars scheming_datasets
```

---

## Container Shell Access and Migrations

Use `docker exec` to run administrative commands inside the running development container.

### Execute Database Upgrades for Extensions
```bash
docker exec -it ckan-dev ckan db upgrade -p my_plugin_name
```

### Run Tests Inside Container
```bash
docker exec -it ckan-dev pytest --ckan-ini=/srv/app/ckan.ini /srv/app/src_extensions/ckanext-myextension/
```
