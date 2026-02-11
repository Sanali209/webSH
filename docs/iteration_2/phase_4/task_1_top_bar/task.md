# Задача 4.1: Top Bar и Динамическое Меню (Phase 4)

**Цель:** Реализовать верхнюю панель, динамически загружающую пункты меню (кнопки, индикаторы) из плагинов.

## Контекст
*   **Файлы:** `shell/src/components/TopBar.svelte`, `core/registry.py`
*   **Документация:** `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 4)
*   **Библиотеки:** `import()`, `svelte`

## Подзадачи

1.  [ ] **Backend: API Реестра UI**
    *   В `core/main.py` или `core/routers/registry.py`: Эндпоинт `GET /api/v1/registry/ui-extensions`.
    *   Возвращать JSON: `[{ id: 'system_clock', type: 'top_bar.item', entry_point: '/plugins/system_clock/ui/bar.js', ... }]`.
2.  [ ] **Frontend: Загрузка Расширений**
    *   В `shell/src/lib/services/extensionLoader.ts`:
        *   `loadExtensions()`: Получать список с `/api/v1/registry/ui-extensions`.
        *   Фильтровать `type === 'top_bar.item'`.
        *   `import(/* @vite-ignore */ url)`: Динамически загружать модуль.
    *   **Компонент:** `extension.default` (Svelte-компонент) или `mount(element)` (Vanilla JS).
3.  [ ] **Frontend: Top Bar Компонент**
    *   В `shell/src/components/TopBar.svelte`:
        *   Левая часть: Логотип, Меню "Пуск".
        *   Правая часть: Контейнер для динамических расширений.
        *   `<svelte:component this={ext.component} />`: Рендерить загруженные компоненты.

## Автоматические тесты
*   **Unit (Backend):** Тест API `/registry/ui-extensions`.
*   **E2E (Playwright):**
    1.  Загрузить "fake plugin" (mock API response).
    2.  Проверить, что в Top Bar появилась новая кнопка.
    3.  Нажать кнопку -> проверить действие (console.log или alert).

## Пункты самопроверки
*   [ ] API возвращает список расширений.
*   [ ] Top Bar корректно отображает динамические кнопки.
*   [ ] Ошибка загрузки одной кнопки не ломает весь Top Bar.

## Критерии выполнения (Definition of Done)
1.  Top Bar рендерится.
2.  Динамические кнопки плагинов загружаются и работают.
3.  Тесты проходят.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
