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

## Walkthrough / Summary

### Execution Steps
1.  **Directory Initialization:** Created `core/`, `plugins/`, `web/`, and `tests/` directories. Added `.gitkeep` to empty directories to ensure they are tracked.
2.  **Poetry Configuration:** Created `pyproject.toml` and defined dependencies:
    -   `fastapi`, `uvicorn` for the API.
    -   `pluggy` for plugin management.
    -   `taskiq` for background tasks.
    -   `loguru` for logging.
    -   `pydantic` for validation.
    -   `websockets` for event bus.
3.  **Docker Setup:**
    -   Created `Dockerfile` using `python:3.11-slim` as the base image. It installs Poetry and project dependencies.
    -   Created `docker-compose.yml` defining `backend` (using the Dockerfile) and `redis` services.
4.  **Application Entrypoint:** Created `core/main.py` with a basic FastAPI application and lifespan manager.
5.  **Readme Creation:** Added a root `README.md` to satisfy poetry build requirements.
6.  **Verification:**
    -   Ran `poetry install` to lock and install dependencies successfully.
    -   Ran `docker compose config` to validate the compose file syntax.
    -   *Note: `docker compose build` failed due to sandbox environment limitations (overlayfs error), but the files are structured correctly.*
