# Design Document: PC Center OS (v14.0 - Unified Architecture)

Этот документ описывает полную архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM.

> **Унифицированная Архитектура (v14.0):** Синтез моделей **"Single Process"**, **"Reactive Broker"** и **"Security Barrier"**. Система представляет собой ультратонкое ядро на базе FastAPI, которое управляет жизненным циклом плагинов и маршрутизацией сигналов, обеспечивая безопасность через механизм Аудита и Согласия.

---

## 1. Концепция: Single Process Kernel

В отличие от традиционных микросервисных архитектур, PC Center запускается как **Единый Процесс** (Monolithic Runtime with Logical Isolation).

*   **FastAPI как Контент-Менеджер:** Служит единой точкой входа (Port 8000) для API, основного UI (Shell) и статики плагинов.
*   **Zero CORS:** Фронтенд и бэкенд живут на одном домене, устраняя сетевые задержки и сложности настройки.
*   **Атомарность:** Плагин — это папка. Загрузка происходит мгновенно при старте ядра.

---

## 2. Архитектура Ядра (The Core)

Ядро состоит из трех функциональных слоев:

### 2.1. Loader (Загрузчик)
Отвечает за динамическую загрузку кода и статики.
*   **Backend:** Ищет `backend.py` в папках плагинов и загружает их в память через `importlib`.
*   **Frontend:** Монтирует папки `/ui` плагинов как статические пути FastAPI (`/plugins/{id}/ui`).

### 2.2. Registry (Реестр Способностей)
База данных доступных функций. Хранит не код, а метаданные:
*   **Capabilities:** Что плагин умеет (например, `ai.summarize`).
*   **Schemas:** Pydantic-схемы входных и выходных данных для валидации.

### 2.3. Switchboard (Реактивный Диспетчер)
Умный маршрутизатор сообщений.
*   **Broker Logic:** Принимает сигнал -> Валидирует схему -> Проверяет права -> Вызывает функцию.
*   **Hybrid Transport:**
    *   *Local:* Прямой вызов Python-функции (Zero-latency).
    *   *Remote:* Проксирование HTTP-запроса в Docker-контейнер (для внешних микросервисов).

---

## 3. Протоколы Взаимодействия

### 3.1. Handshake Protocol (Регистрация)
При старте плагин отправляет **Manifest Payload**:

```json
{
  "id": "task_tracker",
  "type": "local",
  "version": "1.0.0",
  "capabilities": [
    {
      "domain": "core.task.create",
      "input_schema": { ...json_schema... }
    }
  ],
  "integrations": {
    "slots": [ { "id": "ui.sidebar", "component": "Icon.js" } ]
  },
  "permissions": ["storage.read", "ui.notify"]
}
```

### 3.2. Signal Protocol (Обмен данными)
Все взаимодействие происходит через унифицированный API:

`POST /api/v1/call`
```json
{
  "domain": "core.task.create",
  "params": { "title": "Buy milk" },
  "context": { "caller_id": "shell" }
}
```

---

## 4. Frontend: Pluggable Shell

Пользовательский интерфейс строится по принципу **"Intent Registry"**. Шелл не знает о плагинах, он знает только о Слотах.

### 4.1. Система Слотов
1.  **Shell:** Объявляет слоты (`sidebar`, `tray`, `dashboard`).
2.  **Plugin:** Заявляет `ui_extensions` в манифесте.
3.  **Kernel:** Отдает Шеллу список скриптов для загрузки через `GET /api/v1/ui/extensions`.

### 4.2. Динамический Импорт
Шелл использует Native ES Modules для загрузки компонентов плагинов без пересборки.

```javascript
// Shell (Svelte)
const module = await import(`/plugins/${pluginId}/ui/widget.js`);
```

### 4.3. View Manager
Плагины не могут создавать окна сами. Они отправляют сигнал `ui.view.open`, и Шелл открывает соответствующий компонент в новой вкладке или модальном окне.

---

## 5. Безопасность: Audit & Consent

В условиях отсутствия песочницы (Sandbox), безопасность обеспечивается декларативным контролем.

### 5.1. Установка и Аудит
1.  Новый плагин получает статус `PENDING_AUDIT`.
2.  **SecurityAuditor** анализирует манифест и классифицирует риски:
    *   🟢 **Low:** UI, Theme (Разрешено).
    *   🟠 **High:** Network, Storage Write (Требует согласия).
    *   🔴 **Critical:** OS Execute, File Delete (Требует подтверждения).
3.  Пользователь должен явно принять риски в UI перед активацией.

### 5.2. Runtime Barrier (Перехватчик)
`Switchboard` блокирует вызовы, если:
*   Плагин не имеет статуса `ACTIVE`.
*   Плагин пытается вызвать домен, не указанный в `permissions` манифеста.
*   Отсутствует валидный `X-Plugin-Token` (защита от CSRF/XSS со стороны фронтенда).

---

## 6. Реализация (Reference Implementation)

```text
/pc_center
├── main.py              # FastAPI, Loader, Switchboard
├── /core
│   ├── broker.py        # Logic: Discovery, Validation, Dispatch
│   ├── security.py      # Logic: Audit, Barrier
├── /plugins             # User Plugins
│   └── /demo_plugin
│       ├── manifest.json
│       ├── backend.py   # Python Code (Loaded by importlib)
│       └── /ui          # JS Code (Served by StaticFiles)
```

**Workflow:**
1.  `python main.py` запускает сервер.
2.  `Loader` сканирует `/plugins`, импортирует `backend.py`, регистрирует Capabilities.
3.  `FastAPI` монтирует `/plugins/.../ui` как статику.
4.  Пользователь открывает `localhost:8000`.
5.  Shell загружается, запрашивает расширения и рендерит рабочий стол.
