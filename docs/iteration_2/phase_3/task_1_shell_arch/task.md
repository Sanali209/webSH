# Задача 3.1: Архитектура Шелла (Phase 3)

**Цель:** Создать каркас Single Page Application (Svelte 5) с глобальным состоянием, менеджером UI и режимом разработки.

## Контекст
*   **Файлы:** `shell/src/`, `shell/src/lib/stores/`, `shell/vite.config.js`
*   **Документация:** `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 3)
*   **Библиотеки:** `svelte`, `vite` (runes), `penpal`

## Подзадачи

1.  [ ] **Инициализация Svelte 5**
    *   Убедиться, что проект в `shell/` использует Svelte 5.
    *   Создать структуру папок: `components`, `lib`, `stores`, `routes`.
    *   Включить поддержку Runes (`$state`, `$derived`).
2.  [ ] **Global Store (Runes)**
    *   В `shell/src/lib/stores/ui.svelte.ts`: Создать глобальный класс `UIState`.
        *   `activeDesktop: number = $state(0)`
        *   `desktops: Desktop[] = $state([])`
        *   `widgets: Widget[] = $state([])`
    *   **Dev Mode:** Добавить флаг `isDevMode` (из `import.meta.env`).
3.  [ ] **UI Manager (Persistence)**
    *   В `shell/src/lib/services/uiManager.ts`:
        *   `saveState()`: Сохранять `UIState` в `localStorage` (как fallback).
        *   `loadState()`: Загружать при старте.
        *   **API Sync:** Отправлять состояние на `/api/v1/desktop/sync` (будет реализовано в Backend).
4.  [ ] **Error Boundary**
    *   В `shell/src/lib/components/ErrorBoundary.svelte`:
        *   Создать компонент-обертку.
        *   Использовать `<svelte:boundary>` (если доступно) или `try/catch` в `onMount`.
        *   Показывать заглушку "Error loading widget" вместо краша.
5.  [ ] **Skeleton Loading**
    *   В `shell/src/lib/components/WidgetSkeleton.svelte`:
        *   Простой CSS-компонент с анимацией загрузки.

## Автоматические тесты
*   **Unit (Vitest):** Тестирование `UIState` (изменение активного стола, добавление виджета).
*   **E2E (Playwright):** Проверка, что приложение грузится и показывает Skeleton.

## Пункты самопроверки
*   [ ] Приложение собирается без ошибок (`pnpm build`).
*   [ ] Состояние сохраняется после перезагрузки страницы (localStorage).
*   [ ] Ошибка в компоненте не ломает все приложение.

## Критерии выполнения (Definition of Done)
1.  Каркас приложения готов.
2.  Состояние управляется через Runes.
3.  Error Boundary и Skeleton реализованы.
4.  Тесты проходят.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
