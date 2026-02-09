# Design Document: PC Center OS (v2.5)

Этот документ описывает архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM. Система спроектирована по принципу **Микроядра**, где ядро (Kernel) обеспечивает только базовую инфраструктуру, а вся функциональность реализуется через плагины.

> **Важно:** Архитектура ориентирована на **Доверенные Плагины (Trusted Plugins)**. Система не предоставляет песочницу для изоляции вредоносного кода. Безопасность обеспечивается на уровне проверки манифеста и репутации источника.

---

## 1. Концепция и Философия

**PC Center** — это платформа, которая превращает локальный компьютер в мощный сервер автоматизации с веб-интерфейсом.

*   **Микроядро (Micro-Kernel):** Ядро минималистично и стабильно. Оно не знает о файлах, парсерах или нейросетях. Его задача — управлять ресурсами и связывать плагины.
*   **Fail-Safe:** Падение одного плагина не должно приводить к краху всей системы.
*   **Single Source of Truth:** Все данные (метаданные, тексты, векторы) хранятся в едином гибридном хранилище **LanceDB**, но разделены логически.
*   **Schema-Driven:** Интерфейс настроек и валидация данных строятся автоматически на основе Pydantic-схем.
*   **Core SDK:** Единый набор инструментов для разработки плагинов, скрывающий сложность PyArrow и Taskiq.

---

## 2. Технологический Стек

| Компонент | Технология | Роль |
| :--- | :--- | :--- |
| **Backend** | **Python 3.11+, FastAPI** | API Gateway, Orchestration, Static File Serving. |
| **Plugin System** | **Pluggy** | Механизм обнаружения и загрузки модулей. |
| **Data Storage** | **LanceDB** | Гибридное хранилище (Векторы + Метаданные). |
| **Data Processing** | **Polars + Apache Arrow** | Молниеносные Join-ы и аналитика в памяти. |
| **Background Tasks** | **Taskiq (ZeroMQ)** | Распределенная очередь задач. |
| **Frontend** | **Svelte (Vite)** | Реактивный UI, SPA. Скомпилирован в static assets. |
| **Styling** | **Skeleton UI + Tailwind** | Дизайн-система. |
| **Notifications** | **Desktop-notifier** | Нативные пуш-уведомления ОС. |
| **Configs** | **SQLite** | Хранение системных настроек и реестра плагинов. |
| **Observability** | **Loguru + OpenTelemetry** | Логирование и распределенная трассировка. |

---

## 3. Архитектура Ядра (The Kernel)

Ядро выполняет роль операционной системы для модулей.

### 3.1. Ключевые Сервисы

1.  **Frontend Serving & API Gateway:**
    *   **Single Port (8000):** FastAPI обслуживает как API (`/api/...`), так и статические файлы фронтенда (`/`).
    *   **SPA Support:** Все запросы, не относящиеся к API, перенаправляются на `index.html`.
    *   **Plugin UI Mounting:** Статические файлы плагинов (папка `ui/`) автоматически монтируются по пути `/plugins/{id}/ui`, позволяя фронтенду динамически подгружать модули.
    *   **Error Boundaries:** Перехватывает исключения в коде плагинов, предотвращая падение сервера (500 Internal Server Error -> JSON "Plugin Unavailable").

2.  **Module Federation Loader:**
    *   Динамически импортирует Python-код плагинов.
    *   Строит **Граф Зависимостей** (Dependency Graph) для корректного порядка загрузки.

3.  **Event Orchestrator:**
    *   Шина событий (Pub/Sub) на базе `asyncio`.
    *   Поддержка **Distributed Tracing**: каждое событие имеет `correlation_id` для отслеживания цепочки вызовов (FileProvider -> Watchdog -> Parser).
    *   Дублирование событий в **WebSockets** для реактивного обновления UI.

4.  **Resource Controller:**
    *   Управляет воркерами **Taskiq**.
    *   **Resource Quotas:** Лимитирует количество параллельных задач для каждого плагина, чтобы один "тяжелый" модуль не завис систему.

5.  **Database Orchestrator:**
    *   Управляет подключениями к **LanceDB**.
    *   Обеспечивает изоляцию данных через **Scoped Access** (см. раздел Данных).
    *   Запускает миграции схем при обновлении плагинов.

6.  **Capability Registry:**
    *   Реестр возможностей плагинов (например, `opener:text/plain`, `searcher:vectors`). Позволяет ядру знать, какой плагин вызвать для открытия файла.

### 3.2. Жизненный Цикл Плагина (Lifecycle)

Ядро управляет состояниями через хуки:

*   `ON_LOAD`: Загрузка манифеста, проверка зависимостей, миграция схемы БД, монтирование UI ресурсов.
*   `ON_ACTIVATE`: Запуск фоновых процессов, подписка на события.
*   `ON_DEACTIVATE`: Приостановка работы, сохранение состояния.
*   `ON_UNLOAD`: Полная выгрузка, очистка ресурсов.

---

## 4. Слой Данных (Data Layer)

Мы используем стратегию **"Satellite Tables"** (Таблицы-Спутники) в **LanceDB**. Это обеспечивает гибкость NoSQL с надежностью схем Arrow.

### 4.1. Организация Таблиц

Все таблицы связаны единым ключом — `entity_id` (SHA-256 хэш файла или UUID).

1.  **Core Metadata Table (Master):**
    *   Хранит общие данные: `entity_id`, `path`, `filename`, `size`, `mtime`, `mime_type`, `tags`.
    *   Доступна всем плагинам в режиме **Read-Only**.

2.  **Plugin Satellite Tables:**
    *   Каждый плагин создает свои таблицы для специфичных данных.
    *   Пример: `plugin_web_parser_vectors` (содержит `vector_1536d`, `source_url`), `plugin_deduplicator_hashes` (содержит `perceptual_hash`).
    *   Ядро автоматически добавляет префикс `plugin_{id}_` к именам таблиц.

### 4.2. Database Access & Security

Плагины не работают с `lancedb.connect()` напрямую. Они получают объект контекста:

```python
class PluginDatabaseContext:
    def get_my_table(self, suffix="main"):
        # Возвращает таблицу "plugin_{id}_{suffix}"
        pass

    def get_core_table(self):
        # Возвращает core_metadata (Read-Only)
        pass
```

### 4.3. Hybrid Search Orchestrator

Сервис для глобального поиска.
1.  Выполняет векторный поиск по таблицам плагинов.
2.  Объединяет результаты с метаданными из Core Table через **Polars** (In-Memory Join).
3.  Использует **Reciprocal Rank Fusion (RRF)** для ранжирования смешанных результатов (текст + картинки).

---

## 5. Точки Интеграции и Системные Плагины

Система предоставляет два уровня интеграции: **Backend (Python)** и **UI (Svelte)**, а также концепцию **Системных Плагинов**.

### 5.1. Системные Плагины (Capability Providers)

Это плагины, которые предоставляют базовые возможности для работы ОС. Они используют тот же механизм плагинов, но могут иметь привилегированный доступ к `Core Table`.

#### Пример: `plugins/system_fs` (File System Provider)
Этот плагин — аналог "Windows Explorer".
*   **Capabilities:** `fs.scan`, `fs.watch`, `opener:directory`.
*   **Backend:**
    *   Сканирует диск (`os.walk`) и обновляет `core_metadata` в LanceDB.
    *   Следит за изменениями через `watchdog` (создание/удаление файлов).
*   **Frontend UI:**
    *   Реализует полноценный файловый менеджер (Grid/List View, Breadcrumbs).
    *   Предоставляет слоты `context_menu` для других плагинов.

#### Пример: `plugins/system_llm` (LLM Provider)
*   **Capabilities:** `llm.embed`, `llm.generate`.
*   **Backend:** Обертка над `ollama` или `transformers` для генерации векторов.

#### Пример: `plugins/system_script_engine` (Scripting Engine)
Новый системный плагин для поддержки автоматизации через Python-скрипты.
*   **Capabilities:** `script.run`, `workflow.node_provider`.
*   **Role:** Позволяет пользователям писать кастомные скрипты автоматизации, которые имеют доступ к Core SDK.
*   **Features:**
    *   Изолированное выполнение (насколько это возможно в рамках доверенной модели).
    *   API для регистрации узлов (nodes) в визуальном редакторе Workflow.

### 5.2. UI Integration Points (Svelte Slots)

Ядро предоставляет систему **Слотов** (Slots) — предопределенных мест в интерфейсе, куда плагины могут встраивать свои компоненты.

| Слот (Slot Name) | Описание | Пример использования |
| :--- | :--- | :--- |
| `system_tray` | Иконки в статус-баре (верхний/нижний бар). | Индикатор загрузки CPU, статус VPN. |
| `sidebar_nav` | Пункты в боковом меню навигации. | Ссылка на "Избранное", "Недавние". |
| `context_menu` | Пункты меню по ПКМ на файле/папке. | "Сканировать на вирусы", "Конвертировать в PDF". |
| `file_preview` | Компонент предпросмотра файла. | Вьюер для 3D-моделей, Markdown-редактор. |
| `dashboard_widget` | Виджеты на главном экране (Desktop). | Календарь, список задач, погода. |
| `settings_panel` | Вкладка в глобальных настройках. | Настройки конкретного плагина (авто-генерируемые). |

**Механизм регистрации UI:**
Плагин экспортирует компоненты (Svelte) и регистрирует их в манифесте:
```json
"ui_extensions": [
  { "slot": "context_menu", "component": "ContextMenuAction.svelte", "label": "Analyze" }
]
```

---

## 6. Система Плагинов и Core SDK

Для упрощения разработки и унификации зависимостей вводится **Core SDK**.

### 6.1. Что дает SDK?
1.  **High-Level API:** Вместо raw PyArrow, плагин использует методы `sdk.save_document(doc)` и `sdk.search(query)`.
2.  **Dependency Management:** SDK фиксирует версии библиотек (`numpy`, `pydantic`), предотвращая "Dependency Hell". Все плагины используют версии из ядра.
3.  **Task Helper:** Декоратор `@sdk.background_task` автоматически регистрирует функцию в Taskiq и обрабатывает ошибки.

### 6.2. Структура Плагина

```text
/plugins/my_awesome_plugin/
├── manifest.json      # Паспорт модуля
├── config.py          # Pydantic-модель настроек
├── models.py          # PyArrow схемы таблиц
├── router.py          # FastAPI эндпоинты
├── backend.py         # Основная логика и хуки
├── workflow.py        # Узлы для системы автоматизации (если есть)
└── ui/                # Svelte компоненты (динамически подгружаемые)
    └── index.js       # Entry point для UI
```

### 6.3. Манифест (`manifest.json`)

```json
{
  "id": "web_parser",
  "type": "user",
  "name": "Web Parser Pro",
  "version": "1.2.0",
  "core_sdk_version": "^2.1.0",
  "permissions": ["network", "filesystem.read"],
  "dependencies": ["system_fs"],
  "capabilities": ["searcher:web"],
  "ui_extensions": [
    { "slot": "system_tray", "component": "StatusIcon.svelte" }
  ],
  "workflow_nodes": ["parse_url", "extract_images"]
}
```

### 6.4. Unified Settings (Настройки)

Плагин определяет настройки в `config.py` через Pydantic.
Ядро генерирует **JSON Schema**.
Frontend (Svelte) использует библиотеку генерации форм, чтобы отрисовать красивый UI настроек. Разработчику плагина не нужно верстать формы.

---

## 7. UI/UX Архитектура (Svelte)

Интерфейс строится как **Modular SPA**.

### 7.1. Режимы Просмотра
*   **Desktop Mode:** Сетка иконок, виджеты состояния системы.
*   **Module View:** Полноэкранный режим активного плагина.

### 7.2. Динамическая Загрузка (Micro-Frontends)
Плагины компилируются в отдельные JS-модули и помещаются в папку `ui/`.
Svelte-приложение ядра загружает их по требованию через `import('/plugins/{id}/ui/index.js')`. Это позволяет обновлять плагины без пересборки всего фронтенда.

---

## 8. Workflow Engine & Scripting (Новое)

Интеграция визуального программирования (n8n-style) и скриптинга.

### 8.1. Регистрация Узлов (Nodes)
Плагины могут экспортировать функциональность как "узлы" для Workflow Engine.
Это делается через декоратор `@workflow_node` в файле `workflow.py`.

```python
# plugins/web_parser/workflow.py
from core.workflow import workflow_node, NodeInput, NodeOutput

@workflow_node(
    id="parse_page",
    name="Парсить HTML",
    inputs=[NodeInput(name="url", type="string")],
    outputs=[NodeOutput(name="text", type="string"), NodeOutput(name="images", type="list")]
)
async def execute_parse(ctx, inputs):
    # Этот код будет запущен Taskiq воркером
    result = await parse_logic(inputs["url"])
    return {"text": result.text, "images": result.imgs}
```

### 8.2. Scripting Engine Plugin
Системный плагин, который отвечает за выполнение этих узлов и пользовательских скриптов.
*   Сканирует плагины на наличие `workflow.py`.
*   Регистрирует доступные узлы в реестре.
*   Предоставляет API для запуска графов (Workflows).

---

## 9. Безопасность и Стабильность

1.  **Trust Model:** Плагины считаются доверенными. Изоляция процессов (Docker/Wasm) отсутствует для упрощения архитектуры и производительности.
2.  **Permission Scoping:** Плагин декларирует права (`network`, `filesystem.write`) в манифесте для информирования пользователя.
3.  **Isolation:** Ошибки в одном плагине изолируются Middleware и не роняют сервер.
4.  **Validation:** Все данные на входе (API) и выходе (Event Bus) валидируются Pydantic-схемами.
