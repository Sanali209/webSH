# Справочник API ядра webSH

Ядро webSH (Capability Broker) состоит из модулей в `core/`. Ниже — полный API каждого модуля.

## Switchboard (`core/switchboard.py`)

Центральный диспетчер. Принимает `CapabilityEnvelope`, проверяет глубину стека, разрешает хендлер через Registry, валидирует params через кэшированный TypeAdapter, вызывает хендлер.

### Класс `Switchboard`

```python
class Switchboard:
    def __init__(self, max_trace_depth: int = 10)
```

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `max_trace_depth` | `int` | `10` | Макс. глубина trace_stack (защита от циклов) |

### `dispatch(envelope: CapabilityEnvelope) -> dict`

Главный метод. Возвращает `{"status": "success", "data": ..., "correlation_id": ...}` или `{"status": "error", ...}`.

**Алгоритм:**

1. Проверка `len(context.trace_stack) < max_trace_depth`
2. `context.trace_stack.append("kernel.switchboard")`
3. `handler = registry.resolve(envelope.domain)`
4. `adapter = self._get_adapter(envelope.domain)` — кэшированный TypeAdapter
5. Если adapter есть: `params = adapter.validate_python(envelope.params)` — Schema Guard
6. `result = await handler(params, envelope.context)`
7. Возврат `{"status": "success", "data": result, "correlation_id": envelope.correlation_id}`

### `_get_adapter(domain_query: str) -> Optional[TypeAdapter]`

Кэширует TypeAdapter по ключу `domain_query`. Схема берётся из `registry.get_schema()`.

**Глобальный экземпляр:**

```python
switchboard = Switchboard()
```

## Registry (`core/registry.py`)

Реестр capability, схем, плагинов и UI-расширений.

### Класс `Registry`

```python
class Registry:
    def __init__(self)
```

### Внутренние хранилища

| Атрибут | Тип | Ключ | Значение |
|---------|-----|------|----------|
| `_capabilities` | `Dict[str, Callable]` | `"domain@version"` | Хендлер (async def) |
| `_schemas` | `Dict[str, Type[BaseModel]]` | `"domain@version"` | Pydantic модель |
| `_latest_versions` | `Dict[str, str]` | `"domain"` | Последняя зарегистрированная версия |
| `_plugins` | `Dict[str, Any]` | `"plugin_id"` | Метаданные плагина (model_dump) |
| `_ui_extensions` | `Dict[str, Any]` | `"plugin_id"` | UI-расширения (PluginUI.model_dump) |

### `register(domain, version, handler, schema=None)`

Регистрирует capability.

```python
def register(
    self,
    domain: str,
    version: str,
    handler: Callable,        # async def handler(params, context)
    schema: Optional[Type[BaseModel]] = None
)
```

- Сохраняет по ключу `f"{domain}@{version}"`
- Если `schema` — сохраняет в `_schemas`
- Обновляет `_latest_versions` (сравнение строк)

### `resolve(domain_query: str) -> Optional[Callable]`

Находит хендлер.

```python
def resolve(self, domain_query: str) -> Optional[Callable]
```

- Если `"@"` в запросе — прямой поиск по `_capabilities`
- Иначе — `_capabilities.get(f"{domain_query}@{_latest_versions[domain_query]}")`

### `get_schema(domain_query: str) -> Optional[Type[BaseModel]]`

Находит Pydantic-схему для домена. Логика разрешения версии — как у `resolve()`.

### `register_plugin(manifest_data: Dict[str, Any])`

Сохраняет метаданные плагина. `manifest_data` — результат `PluginManifest.model_dump()`.

### `get_plugin(plugin_id: str) -> Optional[Dict]`

Возвращает метаданные плагина по ID.

### `list_plugins() -> List[Dict]`

Возвращает список всех зарегистрированных плагинов.

### `register_ui_extension(plugin_id: str, ui_data: Dict[str, Any])`

Сохраняет UI-расширения плагина.

### `get_ui_extensions() -> Dict[str, Any]`

Возвращает сырые UI-расширения (по plugin_id).

### `list_extensions() -> Dict[str, List[Dict]]`

Группирует UI-расширения по типу. Возвращает:
```python
{
    "widgets": [...],       # WidgetSchema + plugin_id
    "applications": [...],  # ViewSchema → type="application"
    "shortcuts": [...],     # ShortcutSchema
    "top_bar": [...]        # TopBarItemSchema
}
```

**Глобальный экземпляр:**

```python
registry = Registry()
```

## SDK (`core/sdk.py`)

Инструменты для создания плагинов.

### `VERSION = "1.0.0"`

Текущая версия SDK. Сверяется с `compatibility_version` в manifest.json.

### Класс `BaseSettings`

```python
class BaseSettings(BaseModel):
    pass
```

Базовый класс для настроек плагина. Наследуйте и определяйте поля Pydantic.

### Класс `BasePlugin`

Базовый класс для всех плагинов.

```python
class BasePlugin:
    def __init__(self):
        self.name = self.__class__.__name__
        self.id: Optional[str] = None  # Задаётся Loader
```

#### Методы

| Метод | Возврат | Описание |
|-------|---------|----------|
| `get_settings_model()` | `Optional[Type[BaseModel]]` | Переопределите для возврата Pydantic-модели настроек |
| `get_settings_schema()` | `Dict[str, Any]` | JSON Schema из `get_settings_model()`, через `settings_to_json_schema` |
| `get_ui_manifest()` | `Dict[str, Any]` | UI-расширения, определённые кодом (альтернатива manifest.json) |
| `async on_activate()` | `None` | Вызывается при активации плагина |
| `async on_deactivate()` | `None` | Вызывается при деактивации |
| `async call(domain, params, context)` | `Any` | Вызов другой capability (заглушка) |
| `async emit(event, params)` | `None` | Эмиссия события (заглушка) |
| `get_state(key, default)` | `Any` | Получение состояния (заглушка) |

#### `sh_plugin_init(self, registry)` — хук Pluggy

Автоматическая регистрация capability:

```python
@hookimpl
def sh_plugin_init(self, registry):
    for attr_name in dir(self):
        attr = getattr(self, attr_name)
        if hasattr(attr, "_is_capability"):
            registry.register(
                domain=attr._capability_domain,
                version=getattr(self, "VERSION", "1.0.0"),
                handler=attr,
                schema=getattr(attr, "_capability_schema", None)
            )
    # Если get_ui_manifest() не пуст — регистрирует UI
    ui_manifest = self.get_ui_manifest()
    if ui_manifest and self.id:
        registry.register_ui_extension(self.id, ui_manifest)
```

### Декоратор `@capability(domain, schema=None)`

```python
def capability(domain: str, schema: Optional[Type[BaseModel]] = None)
```

Помечает метод как capability. Устанавливает атрибуты:
- `func._is_capability = True`
- `func._capability_domain = domain`
- `func._capability_schema = schema`

### Декоратор `@on_event(pattern)`

```python
def on_event(pattern: str)
```

Помечает метод как обработчик событий. Устанавливает:
- `func._is_event_handler = True`
- `func._event_pattern = pattern`

## Schemas (`core/schemas.py`)

Pydantic-модели протокола webSH.

### `Context`

```python
class Context(BaseModel):
    caller_id: str                                # Кто вызвал capability
    token: Optional[str] = None                   # Токен авторизации
    parent_id: Optional[str] = None               # ID родительского вызова
    trace_stack: List[str] = Field(default_factory=list)  # Стек трассировки
    timestamp: datetime = Field(default_factory=datetime.now)
```

### `CapabilityEnvelope`

```python
class CapabilityEnvelope(BaseModel):
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str                                    # Например "hello.ping"
    params: Dict[str, Any] = Field(default_factory=dict)
    context: Context
```

### `PluginUI` и вложенные модели

```python
class WidgetSchema(BaseModel):
    id: str
    size: Literal["1x1", "2x2", "2x1", "4x2"]
    entry_point: str
    title: str
    type: Literal["widget"] = "widget"
    model_config = ConfigDict(extra='forbid')

class TopBarItemSchema(BaseModel):
    id: str
    entry_point: str
    component: Optional[str] = None
    type: Literal["top_bar.item"] = "top_bar.item"
    model_config = ConfigDict(extra='forbid')

class ViewSchema(BaseModel):
    id: str
    title: str
    entry_point: str
    model_config = ConfigDict(extra='forbid')

class ShortcutSchema(BaseModel):
    icon: str
    title: str
    action: str
    model_config = ConfigDict(extra='forbid')

class PluginUI(BaseModel):
    widgets: List[WidgetSchema] = Field(default_factory=list)
    views: List[ViewSchema] = Field(default_factory=list)
    shortcuts: List[ShortcutSchema] = Field(default_factory=list)
    top_bar: List[TopBarItemSchema] = Field(default_factory=list)
```

### Состояние рабочего стола

```python
class WidgetConfig(BaseModel):
    id: str
    x: int
    y: int
    w: int
    h: int
    type: str                        # "widget" | "icon"
    label: Optional[str] = None
    icon: Optional[str] = None
    component: Optional[str] = None
    props: Optional[str] = None

class DesktopConfig(BaseModel):
    id: int
    widgets: List[WidgetConfig]
```

## Loader (`core/loader.py`)

### `PluginManifest`

```python
class PluginManifest(BaseModel):
    id: str
    version: str = "1.0.0"
    compatibility_version: str = ">=1.0.0"
    author: str = "Unknown"
    description: str = ""
    capabilities: List[str] = Field(default_factory=list)
    ui: Optional[PluginUI] = None
```

### `PluginLoader`

```python
class PluginLoader:
    def __init__(self, plugins_dir: str = "plugins"):
        self.pm = pluggy.PluginManager("sh")
        self.pm.add_hookspecs(PluginSpec)
        self.loaded_plugins = []
        self.plugin_paths = {}
```

| Метод | Описание |
|-------|----------|
| `discover_and_load()` | Сканирует `plugins_dir`, загружает каждый плагин, вызывает `sh_plugin_init` |
| `_load_plugin(plugin_path)` | Читает manifest, валидирует, проверяет версию, импортирует, регистрирует |

## Hooks (`core/hooks.py`)

```python
class PluginSpec:
    @hookspec
    def sh_plugin_init(self, registry):
        """Called during plugin initialization."""
```

**Глобальные экземпляры:**

```python
from core.switchboard import switchboard
from core.registry import registry
from core.loader import loader
```

## REST API (определён в `main.py`)

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/api/v1/call` | POST | Вызов capability (тело: CapabilityEnvelope) |
| `/api/v1/plugins` | GET | Список загруженных плагинов |
| `/api/v1/registry/ui-extensions` | GET | UI-расширения (сгруппированы) |
| `/api/v1/desktop/sync` | GET | Получить состояние рабочего стола |
| `/api/v1/desktop/sync` | POST | Сохранить состояние рабочего стола |
| `/ws` | WebSocket | Двусторонний канал (echo) |
| `/api/v1/debug/stream` | WebSocket | Real-time трассировка (OpenTelemetry spans) |
| `/health` | GET | Проверка состояния |
| `/health/ui/{plugin_id}` | GET | Проверка UI-файлов плагина |

## Зависимости (code-first)

| Компонент | Технология | Назначение |
|-----------|-----------|-----------|
| Плагины | Pluggy | Hook system: `sh_plugin_init` |
| Валидация | Pydantic v2 | Schemas, TypeAdapter, PluginManifest |
| Очередь | Taskiq + Redis | Асинхронное выполнение задач |
| Трассировка | OpenTelemetry OTLP | Span export в Jaeger |
| Хранилище | LanceDB | Состояние рабочего стола, данные плагинов |
| UI мост | Penpal | iframe-коммуникация (widget ↔ shell) |
| Фронтенд | Svelte 5 | Shell webSH |
| Безопасность | Secure (CSP) | Заголовки безопасности |
| Статика | WhiteNoise | Раздача dist/ |
| Сервер | FastAPI + Uvicorn | ASGI сервер |
