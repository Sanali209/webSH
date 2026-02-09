# Project Setup

**Goal:** Initialize the repository structure and configure the development environment.

## Steps

1.  **Initialize Repository Structure**
    - Create the following top-level directories:
        - `core/`: For kernel logic (PluginManager, EventBus).
        - `plugins/`: For user and system plugins.
        - `web/`: For the Svelte frontend.
        - `tests/`: For the Pytest suite.

2.  **Configure `pyproject.toml`**
    - Set up the project using Poetry.
    - Add the following dependencies:
        - `fastapi`
        - `uvicorn`
        - `pluggy`
        - `taskiq`
        - `loguru`
    - Configure build system and metadata.

3.  **Create `docker-compose.yml`**
    - Set up a `docker-compose.yml` file for local development.
    - Include services for:
        - Redis (if needed for Taskiq/Celery).
        - ZeroMQ (if needed).
    - Ensure ports are mapped correctly for the API and Frontend.

## Testing

-   **Directory Verification:** Run `ls -R` to verify the directory structure is created.
-   **Dependency Check:** Run `poetry install` and ensure all dependencies are installed without errors.
-   **Docker Verification:** Run `docker-compose config` to validate the YAML syntax.
-   **Service Start:** Run `docker-compose up -d` and ensure containers start successfully.
