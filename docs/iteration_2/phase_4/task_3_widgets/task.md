# Задача 4.3: Widget Lifecycle и Изоляция (Phase 4)

**Цель:** Обеспечить безопасную загрузку и взаимодействие с UI плагинов через Sandboxed Iframe и библиотеку Penpal.

## Контекст
*   **Файлы:** `shell/src/components/WidgetHost.svelte`, `shell/src/lib/services/widgetBridge.ts`
*   **Документация:** `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 4)
*   **Библиотеки:** `penpal`

## Подзадачи

1.  [ ] **Установка зависимостей**
    *   `pnpm add penpal` в `shell/package.json`.
2.  [ ] **Widget Host Component**
    *   В `shell/src/components/WidgetHost.svelte`:
        *   `src: string` (URL виджета, напр. `/plugins/X/ui/widget.html`).
        *   `<iframe src={src} sandbox="allow-scripts allow-popups">`.
        *   `bind:this={iframeElement}`.
    *   **Подключение Penpal:**
        *   `onMount`: `connectToChild({ iframe, methods: { ... } })`.
        *   `methods`: `getApiToken()`, `getDesktopId()`, `emitEvent(name, data)`.
3.  [ ] **Widget Bridge Service**
    *   В `shell/src/lib/services/widgetBridge.ts`:
        *   `createConnection(iframe: HTMLIFrameElement, context: WidgetContext)`.
        *   Возвращать `Promise<Connection>`.
        *   Обрабатывать `connection.destroy()` при размонтировании.
4.  [ ] **Плагин-сторона (Client SDK)**
    *   Создать `plugins/sdk-js/index.js` (минимальный бандл для плагинов).
    *   Экспортировать `connectToParent()`.
    *   Методы: `api.call(method, params)`, `api.on(event, handler)`.

## Автоматические тесты
*   **Unit (JS):** Тест `WidgetBridge` (mock iframe postMessage).
*   **E2E (Playwright):**
    1.  Загрузить тестовый виджет (простой HTML с JS).
    2.  Виджет вызывает `await parent.getApiToken()`.
    3.  Проверить, что токен получен.
    4.  Проверить, что iframe имеет sandbox атрибут.

## Пункты самопроверки
*   [ ] Iframe создается с правильным `src`.
*   [ ] Penpal успешно соединяется (handshake).
*   [ ] Методы API вызываются из ифрейма.
*   [ ] Ошибка в виджете не ломает Shell (изоляция работает).

## Критерии выполнения (Definition of Done)
1.  Виджеты загружаются в изолированных iframe.
2.  Двустороннее общение (Host <-> Widget) работает через Penpal.
3.  SDK для плагинов (JS) доступен.
4.  Тесты проходят.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
