# Capability Broker — архитектура webSH

## Общая концепция

webSH реализован как **ультратонкое ядро** с брокерской системой сообщений. Вместо классического монолита с жёсткими зависимостями, ядро не знает о возможностях плагинов — оно лишь маршрутизирует запросы.

Архитектурная формула: **Ядро → Switchboard → Registry → Handler(плагин)**

```
┌──────────────────────────────┐
│         Shell (Svelte 5)     │
│   DesktopGrid, WidgetHost    │
└──────────┬───────────────────┘
           │ HTTP POST /api/v1/call
           │ WebSocket /ws
┌──────────▼───────────────────┐
│  main.py (FastAPI Kernel)     │
│                               │
│  ┌────────────────────────┐  │
│  │    Switchboard          │  │  ← Центральный диспетчер
│  │  dispatch(envelope)     │  │
│  └──────┬─────────────────┘  │
│         │                     │
│  ┌──────▼──────┐             │
│  │  Registry    │             │  ← Хранилище capabilities
│  │  resolve()   │             │
│  └─────────────┘             │
│                               │
│  ┌─────────────┐            │
│  │  Schema Guard │           │  ← Pydantic-валидация
│  │  TypeAdapter  │           │
│  └─────────────┘            │
│                               │
│  ┌──────────────────┐       │
│  │  Plugins (8+)     │       │  ← Реальные обработчики
│  │  system_fs        │       │
│  │  system_storage   │       │
│  │  system_executor  │       │
│  │  ...              │       │
│  └──────────────────┘       │
└──────────────────────────────┘
```

## Компоненты ядра

### Switchboard (`core/switchboard.py`)

Центральный диспетчер. Порядок обработки `CapabilityEnvelope`:

1. **Trace check** — проверка глубины `context.trace_stack` для защиты от циклических вызовов
2. **Resolve** — `registry.resolve(domain)` ищет handler по ключу `domain@version` или latest
3. **Schema Guard** — Pydantic `TypeAdapter` (кэшированный) валидирует `params`
4. **Dispatch** — асинхронный вызов handler(params, context)
5. **Возврат** — `{"status": "success"/"error", "data": ..., "correlation_id": ...}`

Ключевой поток в `core/switchboard.py`:

```python
async def dispatch(self, envelope: CapabilityEnvelope) -> dict:
    # 1. Trace check
    if len(envelope.context.trace_stack) > MAX_DEPTH:
        raise CircularCallError(...)
    # 2. Resolve
    handler = self.registry.resolve(envelope.domain)
    # 3. Schema Guard (validation)
    validated = self._validate_params(envelope.domain, envelope.params)
    # 4. Dispatch
    result = await handler(validated, envelope.context)
    # 5. Return
    return {"status": "success", "data": result, "correlation_id": envelope.correlation_id}
```

### Registry (`core/registry.py`)

Хранилище всех зарегистрированных capabilities:

- `_capabilities: Dict[str, Callable]` — ключ `domain@version` → handler
- `_schemas: Dict[str, Type[BaseModel]]` — Pydantic-схемы для каждого домена
- `_latest_versions: Dict[str, str]` — отслеживание последней версии
- `_plugins: Dict[str, PluginMeta]` — метаданные плагинов
- `_ui_extensions: Dict[str, List]` — UI-декларации (widgets, views, shortcuts, top_bar)

Метод `resolve(domain)` поддерживает версионирование: `fs.list@1.0` или просто `fs.list` (latest).

### Loader (`core/loader.py`)

Загрузчик плагинов с валидацией:

1. Сканирует `plugins/` директорию
2. Читает `manifest.json` → валидирует через `PluginManifest` (Pydantic)
3. Проверяет `compatibility_version` (семантическое версионирование)
4. Динамический импорт `backend.py`
5. Регистрирует `plugin` в **Pluggy** (`self.pm.register()`)
6. Регистрирует метаданные и UI-расширения в Registry
7. **Rich**-отчёты об ошибках при загрузке

### SDK (`core/sdk.py`)

Базовый класс `BasePlugin`:

```python
class BasePlugin:
    @capability("domain.name", schema=MyParams)
    async def my_handler(self, params: MyParams, context):
        ...

    @on_event("event.name")
    async def my_listener(self, data):
        ...
```

Ключевые методы:
- `sh_plugin_init` (Pluggy hook) — автоматически обнаруживает `@capability`-декорированные методы
- `get_settings_model()` / `get_settings_schema()` — JSON Schema для UI
- `get_ui_manifest()` — программная декларация UI-расширений
- `call(domain, params)` / `emit(event, data)` — cross-plugin вызовы
- `on_activate()` / `on_deactivate()` — жизненный цикл

## Протокол обмена

**CapabilityEnvelope** (запрос):
```json
{
  "correlation_id": "uuid-v4",
  "domain": "fs.list",
  "params": {"path": "."},
  "context": {
    "caller_id": "shell",
    "token": "jwt-token",
    "trace_stack": [],
    "timestamp": "2025-01-01T00:00:00Z"
  }
}
```

**Ответ**:
```json
{
  "status": "success",
  "data": [{"name": "file.txt", "is_dir": false}],
  "correlation_id": "uuid-v4"
}
```

## Трейсинг и наблюдаемость

**Два слоя трейсинга**:

1. **OpenTelemetry** (`core/tracing.py`) — OTLP-экспорт в Jaeger, `BroadcasterSpanProcessor`
2. **WebSocket broadcast** (`core/debug.py`) — `TraceBroadcaster` рассылает каждый завершённый span в реальном времени через `/api/v1/debug/stream`

**Docker Compose**: Redis (Taskiq broker) + Jaeger (OTLP gRPC) + app (FastAPI + WhiteNoise)

## Сравнение с альтернативами

| Аспект | webSH (Capability Broker) | Традиционный монолит | Микросервисы |
|--------|---------------------------|----------------------|--------------|
| Связанность | Минимальная (через Registry) | Высокая (прямые импорты) | Минимальная (через сеть) |
| Добавление фичи | Новый плагин + manifest | Изменение ядра | Новый сервис + деплой |
| Валидация | Schema Guard (автоматически) | Ручная | Ручная / gRPC |
| Сетевые задержки | 0 (in-process) | 0 | Значительные |
| Изоляция | Sandbox путей + CSP | Нет | Полная |
| Версионирование | domain@version | Нет | API versioning |

## Ключевые паттерны

1. **Capability Broker** — ядро не знает о возможностях, только маршрутизирует
2. **Convention over Configuration** — `backend.py` + `manifest.json` = плагин
3. **Schema Guard** — каждый вызов валидируется через Pydantic
4. **Trace Stack** — защита от циклических cross-plugin вызовов
5. **UI как декларация** — плагин декларирует widgets/views/shortcuts, Shell рендерит