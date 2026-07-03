# Запуск ядра webSH и загрузка плагинов

## Цель

Запустить ядро Capability Broker (Switchboard + Registry + Loader), загрузить все плагины из `plugins/` и убедиться, что API `/api/v1/call` отвечает на capability-запросы.

## Что вы получите

Работающий FastAPI-сервер webSH (PC Center v3.0), который:
- сканирует `plugins/` и валидирует manifest.json каждого плагина через `PluginManifest` (Pydantic)
- проверяет `compatibility_version` плагина против SDK_VERSION
- динамически импортирует `backend.py` каждого плагина
- регистрирует плагины в Pluggy (единственный хук `sh_plugin_init`)
- регистрирует capability-хендлеры и UI-расширения в `Registry`
- монтирует статические UI-файлы плагинов по `/plugins/{id}/ui`

## Предварительные требования

- Python >= 3.11
- Redis (через Docker Compose или локально)
- Установленные зависимости:

```bash
pip install -r requirements.txt
```

## Шаг 1: Структура проекта

Код ядра лежит в `core/`:

```
core/
├── __init__.py
├── switchboard.py    # центральный диспетчер
├── registry.py       # реестр capability и UI-расширений
├── loader.py         # загрузчик плагинов
├── sdk.py            # BasePlugin + декораторы capability/on_event
├── schemas.py        # CapabilityEnvelope, Context, PluginUI, WidgetConfig
├── hooks.py          # pluggy hookspec (sh_plugin_init)
├── executor.py       # Taskiq + Redis ListQueueBroker
├── settings.py       # Pydantic Settings (REDIS_URL, HOST, PORT...)
├── tracing.py        # OpenTelemetry OTLP + BroadcasterSpanProcessor
├── debug.py          # TraceBroadcaster WebSocket
├── dashboard.py      # Rich-панель состояния
└── utils.py
```

## Шаг 2: Запуск инфраструктуры (Docker Compose)

```bash
# Redis + Jaeger
docker compose up -d redis jaeger
```

Проверка:

```bash
docker compose ps
# redis и jaeger должны быть в статусе Up
```

## Шаг 3: Запуск ядра

```bash
python main.py
```

Успешный запуск в консоли:

```
INFO  | Kernel: Ready
INFO  | Successfully loaded plugin: hello_world (v1.0.0)
INFO  | Registered capability: hello.ping@1.0.0 (Schema: Yes)
INFO  | Successfully loaded plugin: clock (v1.0.0)
INFO  | Registered UI extensions for plugin: clock
INFO  | Successfully loaded plugin: shortcut (v1.0.0)
INFO  | Registered UI extensions for plugin: shortcut
INFO  | Successfully connected to Redis
INFO  | Tracing initialized. Exporting to http://localhost:4317
INFO  | Uvicorn running on http://127.0.0.1:8000
```

**Что происходит под капотом (code-first):**

В `main.py`, функция `lifespan` (асинхронный контекстный менеджер) выполняет:

```python
from core.tracing import setup_tracing
setup_tracing()  # Инициализация OpenTelemetry TracerProvider

loader.discover_and_load()  # Загрузка плагинов
```

`Loader.discover_and_load()` (loader.py строка 35):

```python
def discover_and_load(self):
    for entry in os.scandir(self.plugins_dir):
        if entry.is_dir():
            self._load_plugin(entry.path)
    self.pm.hook.sh_plugin_init(registry=registry)
```

## Шаг 4: Проверка — вызов capability

Проверяем, что capability `hello.ping` зарегистрирована и отвечает:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/call \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "hello.ping",
    "params": {"name": "webSH"},
    "context": {"caller_id": "test", "trace_stack": []}
  }'
```

**Успешный ответ:**

```json
{
  "status": "success",
  "data": {"message": "Hello, webSH!"},
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Как это работает (code-first):**

1. FastAPI эндпоинт `/api/v1/call` (main.py строка 149):

```python
@app.post("/api/v1/call")
async def capability_call(envelope: CapabilityEnvelope):
    return await switchboard.dispatch(envelope)
```

2. `Switchboard.dispatch()` (switchboard.py строка 24):

```python
async def dispatch(self, envelope: CapabilityEnvelope) -> Any:
    # 1. Trace check — защита от циклических вызовов
    if len(envelope.context.trace_stack) >= self.max_trace_depth:
        raise RuntimeError("Max trace depth exceeded")

    # 2. Добавление текущего узла в трейс
    envelope.context.trace_stack.append("kernel.switchboard")

    # 3. Разрешение хендлера через Registry
    handler = registry.resolve(envelope.domain)

    # 4. Schema Guard — TypeAdapter из кэша
    adapter = self._get_adapter(envelope.domain)
    if adapter:
        params = adapter.validate_python(envelope.params)

    # 5. Асинхронный вызов хендлера
    result = await handler(params, envelope.context)
```

3. `Registry.resolve()` (registry.py строка 30):

```python
def resolve(self, domain_query: str) -> Optional[Callable]:
    if "@" in domain_query:
        return self._capabilities.get(domain_query)
    latest_version = self._latest_versions.get(domain_query)
    return self._capabilities.get(f"{domain_query}@{latest_version}")
```

## Шаг 5: Проверка — список плагинов

```bash
curl http://127.0.0.1:8000/api/v1/plugins
```

Ответ:

```json
[
  {
    "id": "hello_world",
    "version": "1.0.0",
    "description": "SDK Verification Plugin",
    "capabilities": ["hello.ping"]
  }
]
```

## Шаг 6: Проверка — UI-расширения

```bash
curl http://127.0.0.1:8000/api/v1/registry/ui-extensions
```

Ответ:

```json
{
  "widgets": [
    {
      "id": "clock.widget",
      "size": "2x2",
      "entry_point": "/plugins/clock/ui/index.html",
      "title": "Clock",
      "type": "widget",
      "plugin_id": "clock"
    }
  ],
  "applications": [],
  "shortcuts": [],
  "top_bar": []
}
```

**Как UI-расширения попадают в ответ:**

`Registry.list_extensions()` (registry.py строка 85) группирует расширения по типу, проходя по `self._ui_extensions` и разбирая секции `widgets`, `views`, `shortcuts`, `top_bar`.

## Возможные проблемы

| Проблема | Причина | Решение |
|----------|---------|---------|
| `Plugin ... requires SDK version >=1.0.0, but current version is ...` | Несовместимая версия SDK в manifest.json vs core/sdk.py | Проверьте `compatibility_version` в manifest.json |
| `No 'plugin' instance found in ...` | В backend.py нет глобального `plugin = YourPlugin()` | Добавьте `plugin = YourPlugin()` |
| `Failed to connect to Redis` | Redis не запущен | `docker compose up -d redis` |
| `No provider found for domain: ...` | Capability не зарегистрирована | Проверьте manifest.json и декоратор `@capability` |

## Итог

Ядро webSH запущено, плагины загружены, capability-запросы обрабатываются через Switchboard с валидацией схем, UI-расширения доступны через REST API.
