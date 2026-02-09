# UI Polish

**Goal:** Enhance the visual appeal and user experience.

## Steps

1.  **Implement `ThemeSwitcher`**
    - Create a toggle in the settings/sidebar.
    - Switch between Dark and Light mode (using Tailwind classes or CSS variables).
    - Persist the preference in local storage.

2.  **Add `Skeleton` Loading States**
    - In `FileExplorer.svelte` and other data-heavy components.
    - Display skeleton loaders while data is fetching.

3.  **Enhance Settings UI**
    - Add a search bar to filter settings.
    - Provide live validation feedback for input fields (using Pydantic error messages).

4.  **Add "About" Page**
    - Display Core version.
    - List installed plugins and their versions.

## Testing

-   **Manual/E2E:**
    -   **Theme:** Toggle theme and verify styles change. Refresh page and verify theme persists.
    -   **Skeleton:** Throttling network speed to verify skeletons appear.
