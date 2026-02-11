---
title: PC Center v3.0
emoji: 🖥️
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# PC Center v3.0

PC Center v3.0 is a modular "Web OS" desktop environment built on the principles of an ultra-thin kernel and a broker messaging system. It features a Single-Server Core (FastAPI) and a Shell UI (Svelte 5).

## Key Features

*   **Capability Broker:** The Kernel acts as a high-performance signal switchboard, routing requests between self-contained plugins.
*   **Single-Server Core:** A unified FastAPI server that serves the API, the Shell, and dynamic Plugin UIs.
*   **Plugin System:** Modular Python + JS plugins that register "Capabilities" and "Slots".
*   **Shell UI:** A Svelte 5 + Vite based desktop environment with a grid system, window management, and dynamic component injection.
*   **Reactive State:** Shared state store for real-time UI synchronization.

## Installation

### Prerequisites

*   **Docker & Docker Compose** (Recommended for running the full stack)
*   **Node.js 20+** (For local frontend development)
*   **Python 3.10+** (For local backend development)

### Clone the Repository

```bash
git clone https://github.com/your-username/pc-center.git
cd pc-center
```

## Usage

### Run with Docker Compose (Recommended)

To start the entire stack, including Core, Redis, and Jaeger:

```bash
docker-compose up --build
```

The application will be available at [http://localhost:7860](http://localhost:7860).

### Run Locally (Development)

1.  **Start the Backend (Core):**

    ```bash
    # Install Python dependencies
    pip install -r requirements.txt

    # Run the server
    uvicorn main:app --reload --host 0.0.0.0 --port 7860
    ```

2.  **Start the Frontend (Shell):**

    ```bash
    cd shell
    pnpm install
    pnpm dev
    ```

    The shell will be available at [http://localhost:5173](http://localhost:5173).

## Iteration 2 Status

Current progress and roadmap for Iteration 2 (Integration & Shell) can be found here: [Iteration 2 Roadmap](docs/iteration_2/roadmap.md).

For architectural details, please refer to the [Design Document](docs/DESIGN.md).
