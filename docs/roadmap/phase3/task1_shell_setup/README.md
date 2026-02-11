# Task 3.1: System Shell Setup (Svelte + Vite)

## 1. Вводная часть
Перед началом исполнения: **изучить роль Шелла в `docs/DESIGN.md` раздел 5.3 и описание системы рабочих столов**.

## 2. Инструкция по выполнению
1. Инициализировать проект на Svelte + Vite в папке `/plugins/system_shell`.
2. Реализовать базовую навигацию между 5 рабочими столами.
3. Настроить `app.mount` в Ядре для раздачи статики Шелла.
4. Создать базовую структуру папок для компонентов (Header, Tray, Grid).

## 3. Спецификация API (Integration Details)
- **Globals:** `window.pc_center`
- **Exposed API:**
    - `pc_center.call(domain, params)` -> Promise
    - `pc_center.on(event, callback)`
    - `pc_center.store.get/set(key, value)`
- **Shared State:** `ui.active_desktop` (1-5).

## 4. Зависимости (Dependencies)
- `svelte`, `vite`, `axios` (или `fetch`), `lucide-svelte` (иконки).

## 5. Принципы кода и архитектуры
- [ ] **Reactive Runes:** Использование Svelte 5 Runes ($state, $derived, $effect).
- [ ] **Component Atomicity:** Разбиение UI на мелкие переиспользуемые части.
- [ ] **CSS Variables:** Использование единой темы (Colors, Spacing) через CSS-переменные.
- [ ] **Lazy Loading:** Динамический импорт редко используемых вкладок.

## 6. Безопасность и Валидация
- Санитизация данных перед выводом в HTML (XSS Protection).
- Обработка обрыва WebSocket соединения с Ядром.

## 7. Самопроверка (Self-Review)
- [ ] Интерфейс плавно переключается между 5 столами без перезагрузки.
- [ ] `window.pc_center` инициализирован и доступен из консоли браузера.

## 8. План исполнения
1. [ ] Scaffolding проекта.
2. [ ] Настройка Base API Wrapper.
3. [ ] Layout & Navigation.

## 9. Цели готовности (Definition of Done)
- [ ] Шелл отображает верхнюю панель и переключатель столов.
- [ ] Статика успешно отдается сервером FastAPI.
- [ ] Стейт активного стола синхронизирован.
