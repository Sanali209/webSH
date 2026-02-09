# Phase 5: Optimization & UI Polish

**Goal:** Refine the system for stability, performance, and user experience.

## 1. Notifications (`plugins/system_notifications`)
- [ ] Implement `NotificationManager` (backend):
  - `send(message, severity)`.
  - Use `desktop-notifier` for OS-level alerts.
- [ ] Implement UI Components (`web/src/lib/components/notifications/`):
  - Toast notifications (top-right).
  - Notification History/Center (sidebar).

## 2. Health Checks (`core/health.py`)
- [ ] Implement `HealthCheckService`:
  - Periodically ping all active plugins.
  - Check `Taskiq` queue depth.
  - Check LanceDB connection status.
- [ ] Add API endpoint `/api/health` -> JSON status.
- [ ] If plugin fails check -> `deactivate()` and notify user.

## 3. Optimization (`core/optimization.py`)
- [ ] Implement `QueryCache`:
  - Cache search results (LRU) for frequent queries.
  - Invalidate cache on file changes (`fs_provider`).
- [ ] Optimize Polars:
  - Use `scan_parquet` (lazy loading) instead of `read_parquet`.
  - Filter early before joining.

## 4. UI Polish (`web/src/`)
- [ ] Implement `ThemeSwitcher` (Dark/Light mode).
- [ ] Add `Skeleton` loading states for File Explorer.
- [ ] Enhance Settings UI:
  - Add search bar for settings.
  - Live validation feedback (Pydantic errors).
- [ ] Add "About" page with version info (`Core` + `Plugins`).
