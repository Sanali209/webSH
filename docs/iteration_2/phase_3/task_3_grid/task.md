# Задача 3.3: Desktop Grid и Компоновка (Phase 3)

**Цель:** Реализовать сетку для размещения элементов рабочего стола (иконки, виджеты).

## Контекст
*   **Файлы:** `shell/src/components/DesktopGrid.svelte`, `shell/src/lib/types.ts`
*   **Документация:** `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 3)
*   **Библиотеки:** `css-grid`, `svelte-dnd-action`

## Подзадачи

1.  [x] **CSS Grid**
    *   В `shell/src/components/DesktopGrid.svelte`:
        *   `.grid-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(64px, 1fr)); ... }`
        *   `gap: 16px`.
    *   **Drag-and-Drop:** Использовать `svelte-dnd-action` для списка элементов (`items: GridItem[]`).
2.  [x] **Grid Item (Компонент)**
    *   В `shell/src/components/GridItem.svelte`:
        *   Поддержка `type: 'icon' | 'widget'`.
        *   `icon`: Простая `<img>` с подписью.
        *   `widget`: `<iframe>` (для Phase 4).
        *   Поддержка размеров: `grid-column: span W; grid-row: span H;`.
3.  [x] **Логика Размещения**
    *   В `shell/src/lib/services/gridManager.ts`:
        *   `placeItem(item, x, y)`: Проверять пересечения.
        *   `findEmptySpot(w, h)`: Найти свободное место для нового элемента.

## Автоматические тесты
*   **Unit (Frontend):** `findEmptySpot` должна возвращать `(0, 0)` для первого элемента. (Done)
*   **Unit:** `placeItem` не должен позволять наложение. (Done)
*   **E2E (Playwright):**
    1.  Добавить иконку на сетку. (Included in demo)
    2.  Перетащить (эмулировать) в другую ячейку. (Done)
    3.  Проверить новые координаты. (Done via text content order check)

## Пункты самопроверки
*   [x] Сетка адаптивна (заполняет пространство).
*   [x] Элементы не наезжают друг на друга.
*   [x] Drag-and-drop работает плавно.

## Критерии выполнения (Definition of Done)
1.  Сетка рендерится корректно.
2.  Перемещение элементов работает.
3.  Логика размещения проверена тестами.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
