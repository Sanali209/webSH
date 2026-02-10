# PC Center User Guide

Welcome to the **PC Center** User Guide! This document provides detailed instructions on how to install, configure, and use the PC Center application.

## Table of Contents

1.  [Introduction](#introduction)
2.  [Installation](#installation)
    *   [Prerequisites](#prerequisites)
    *   [Setup Steps](#setup-steps)
3.  [Getting Started](#getting-started)
    *   [Accessing the Dashboard](#accessing-the-dashboard)
    *   [Navigation Overview](#navigation-overview)
4.  [Features & Plugins](#features--plugins)
    *   [System Dashboard](#system-dashboard)
    *   [File System Explorer](#file-system-explorer)
    *   [Web Parser](#web-parser)
    *   [File Deduplicator](#file-deduplicator)
    *   [Script Engine](#script-engine)
    *   [LLM Integration](#llm-integration)
5.  [Troubleshooting](#troubleshooting)

---

## Introduction

**PC Center** is a modular, local "Web OS" designed to give you powerful tools for managing your computer directly from a web browser. It runs locally on your machine, ensuring privacy and speed.

Key capabilities include:
*   **System Monitoring:** View CPU, Memory, and Disk usage in real-time.
*   **File Management:** Browse, search, and manage files.
*   **Web Archiving:** Save web pages for offline reading and search.
*   **Automation:** Create visual workflows to automate tasks.
*   **AI Assistance:** chat with local LLMs (Large Language Models) for help and analysis.

---

## Installation

### Prerequisites

*   **Docker Desktop**: Ensure Docker is installed and running. [Download Docker](https://www.docker.com/products/docker-desktop)
*   **Git**: Version control tool. [Download Git](https://git-scm.com/downloads)

### Setup Steps

1.  **Clone the Repository:**
    Open a terminal and run:
    ```bash
    git clone https://github.com/yourusername/pc-center.git
    cd pc-center
    ```

2.  **Start the Application:**
    Run the following command to build and start the containers:
    ```bash
    docker-compose up --build
    ```
    *Note: The first run may take a few minutes as it downloads necessary images and dependencies.*

3.  **Verify Installation:**
    Once the logs show `Application startup complete`, open your browser and navigate to:
    `http://localhost:5173`

---

## Getting Started

### Accessing the Dashboard

Upon visiting `http://localhost:5173`, you will be greeted by the **System Dashboard**. This is your central command center.

### Navigation Overview

*   **Top Bar:**
    *   **Theme Switcher:** Toggle between Light and Dark mode.
    *   **System Tray:** Shows active plugin indicators and notifications.
*   **Sidebar / Main Navigation:**
    *   **Dashboard:** Returns to the main overview.
    *   **Files:** Opens the File Explorer.
    *   **Settings:** Configure global application settings.

---

## Features & Plugins

PC Center is built on a plugin architecture. Here are the core plugins included:

### System Dashboard
The default view providing a grid of widgets.
*   **Resource Monitor:** Real-time graphs for CPU and Memory usage.
*   **Quick Actions:** Shortcuts to common tasks.
*   **Recent Activity:** A log of recent system events.

### File System Explorer
A full-featured file manager running in your browser.
*   **Browse:** Navigate your local file system.
*   **Search:** Quickly find files by name or content.
*   **Preview:** View images, text files, and code directly in the browser.
*   **Manage:** Copy, move, delete, and rename files.

### Web Parser
An advanced tool for archiving the web.
*   **Archive:** Input a URL to download and save its content.
*   **Search:** Full-text search across all archived pages.
*   **Offline Access:** Read saved pages even without an internet connection.
*   **Security:** Automatically blocks unsafe URLs and tracks.

### File Deduplicator
Reclaim disk space by finding duplicate files.
*   **Scan:** select a directory to scan for duplicates.
*   **Review:** See a list of duplicate groups with file details.
*   **Clean:** Selectively delete duplicates while keeping the original safe.

### Script Engine
Automate your workflow with a visual editor.
*   **Visual Editor:** Drag and drop nodes to create logic flows (similar to n8n).
*   **Triggers:** Start scripts on file changes, schedules, or webhooks.
*   **Actions:** Manipulate files, send notifications, or call other plugins.

### LLM Integration
Chat with AI running locally on your machine.
*   **Chat Interface:** A conversational UI for interacting with the AI.
*   **Context:** The AI can access data from other plugins (e.g., search your archived web pages).
*   **Privacy:** All processing happens locally; no data is sent to the cloud.

---

## Troubleshooting

### Common Issues

**1. "Connection Refused" or "Site can't be reached"**
*   Ensure Docker is running.
*   Check if the containers are up: `docker-compose ps`
*   Verify port `5173` (Frontend) and `8000` (Backend) are not in use by other applications.

**2. Plugins not loading**
*   Check the browser console (F12) for errors.
*   Check the backend logs: `docker-compose logs -f backend`
*   Ensure the `plugins/` directory is correctly mounted in Docker.

**3. Performance is slow**
*   If using the **Web Parser** or **Deduplicator** on large directories, it may consume significant CPU/RAM.
*   Check Docker resource limits in Docker Desktop settings.

### Getting Help
If you encounter a bug or have a feature request, please open an issue on the GitHub repository.
