# Задача 4.2: Диалог управления столом (Phase 4)

**Цель:** Создать интерфейс (Modal) для добавления виджетов, ярлыков и приложений на текущий рабочий стол.

## Контекст
*   **Файлы:** `shell/src/components/AddWidgetDialog.svelte`, `core/registry.py`
*   **Документация:** `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 4)
*   **Библиотеки:** `svelte-headlessui` (или кастомный Modal)

## Подзадачи

1.  [x] **Backend: Списки Реестра**
    *   В `core/registry.py`: Расширить метод `get_ui_extensions` (или `list_extensions`).
    *   Возвращать: `widgets`, `applications`, `shortcuts`.
2.  [x] **Frontend: Компонент Диалога**
    *   В `shell/src/components/AddWidgetDialog.svelte`:
        *   `isOpen: boolean`.
        *   `tabs: ['Виджеты', 'Приложения', 'Ярлыки']`.
        *   `filter: string` (поиск).
        *   `list: Extension[]` (фильтрованный по табу).
    *   **Действие:** При клике на элемент -> `onSelect(item)`.
3.  [x] **Frontend: Логика Добавления**
    *   В `shell/src/lib/services/uiManager.ts`:
        *   `addWidget(widgetId, desktopId)`:
            *   Получить метаданные виджета (размер, entry_point).
            *   Вызвать `gridManager.findEmptySpot`.
            *   Создать `GridItem` (type='widget').
            *   Сохранить состояние.

## Автоматические тесты
*   **Unit (Frontend):** Тест `addWidget`: проверяет, что массив виджетов увеличился.
*   **E2E (Playwright):**
    1.  Открыть Top Bar Menu -> "Добавить виджет".
    2.  Выбрать виджет из списка.
    3.  Нажать "Добавить".
    4.  Диалог закрывается.
    5.  Виджет появляется на Grid.

## Пункты самопроверки
*   [x] Диалог открывается и закрывается.
*   [x] Вкладки переключаются.
*   [x] Поиск работает.
*   [x] Выбор виджета добавляет его на стол.

## Критерии выполнения (Definition of Done)
1.  UI диалога готов.
2.  Списки загружаются с API.
3.  Добавление виджетов работает.
4.  Тесты проходят.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
