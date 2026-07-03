# Создание плагина с capability для webSH

## Цель

Создать плагин, который регистрирует собственную capability (domain) и обрабатывает вызовы через Switchboard.

Вы научитесь:
- создавать структуру каталога плагина
- писать `manifest.json` с Pydantic-валидацией
- реализовывать `backend.py` с наследованием от `BasePlugin`
- использовать декоратор `@capability` с Pydantic-схемой
- подключать UI-виджет через manifest.json

## Предварительные требования

- работающее ядро webSH (см. [start-kernel.md](start-kernel.md))
- базовая структура webSH в `D:\github\webSH`

## Шаг 1: Структура каталога плагина

Каждый плагин — это директория в `plugins/` с обязательными файлами:

```
plugins/my_plugin/
├── manifest.json        # метаданные и список capability
├── backend.py           # Python-модуль с class plugin экземпляром
└── ui/                  # опционально: статические файлы для виджетов
    └── index.html
```

## Шаг 2: manifest.json

Файл `manifest.json` валидируется моделью `PluginManifest` (loader.py строка 18):

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

Создайте `plugins/my_greeter/manifest.json`:

```json
{
    "id": "my_greeter",
    "version": "1.0.0",
    "author": "webSH",
    "description": "Greeter plugin — демонстрация capability",
    "compatibility_version": ">=1.0.0",
    "capabilities": [
        "greeter.hello",
        "greeter.goodbye"
    ]
}
```

**Code-first:** При загрузке `Loader._load_plugin()` (loader.py строка 54) читает файл через `json.load()`, затем создаёт `PluginManifest(**manifest_data)`. Pydantic вызовет ошибку валидации, если `id` отсутствует или `capabilities` не список строк.

## Шаг 3: backend.py — BasePlugin и @capability

Создайте `plugins/my_greeter/backend.py`:

```python
from core.sdk import BasePlugin, capability
from pydantic import BaseModel, Field
from loguru import logger

class HelloParams(BaseModel):
    name: str = "World"
    greeting: str = "Hello"

class GoodbyeParams(BaseModel):
    name: str = "World"

class MyGreeter(BasePlugin):
    VERSION = "1.0.0"

    @capability("greeter.hello", schema=HelloParams)
    async def hello(self, params: HelloParams, context):
        logger.info(f"greeter.hello called by {context.caller_id}")
        return {
            "message": f"{params.greeting}, {params.name}!",
            "from": self.name
        }

    @capability("greeter.goodbye", schema=GoodbyeParams)
    async def goodbye(self, params: GoodbyeParams, context):
        return {"message": f"Goodbye, {params.name}!"}

    async def on_activate(self):
        logger.info("MyGreeter activated!")

    async def on_deactivate(self):
        logger.info("MyGreeter deactivated!")

plugin = MyGreeter()
```

**Code-first разбор:**

### Декоратор `@capability` (sdk.py строка 127):

```python
def capability(domain: str, schema: Optional[Type[BaseModel]] = None):
    def decorator(func: Callable):
        func._is_capability = True
        func._capability_domain = domain
        func._capability_schema = schema
        @wraps(func)
        async def wrapper(self, params: Any, context: Any):
            return await func(self, params, context)
        return wrapper
    return decorator
```

Декоратор помечает метод флагами `_is_capability`, `_capability_domain`, `_capability_schema`. Сам метод остаётся асинхронным.

### Автоматическая регистрация через `sh_plugin_init` (sdk.py строка 63):

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
```

Этот хук вызывается для каждого плагина после загрузки всех модулей. Он сканирует все атрибуты экземпляра `plugin` и регистрирует в `Registry` каждый метод, помеченный `@capability`.

### Глобальная переменная `plugin`

Loader ищет `plugin = MyGreeter()` в модуле (loader.py строка 90):

```python
plugin_instance = getattr(module, "plugin", None)
if not plugin_instance:
    logger.warning(f"No 'plugin' instance found in {manifest.id}")
    return
```

Без `plugin = MyGreeter()` загрузчик пропустит плагин.

## Шаг 4: Тестирование capability

Перезапустите ядро и вызовите новую capability:

```bash
# greeter.hello
curl -X POST http://127.0.0.1:8000/api/v1/call \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "greeter.hello",
    "params": {"name": "webSH", "greeting": "Привет"},
    "context": {"caller_id": "test", "trace_stack": []}
  }'
```

Ответ:

```json
{
  "status": "success",
  "data": {"message": "Привет, webSH!", "from": "MyGreeter"},
  "correlation_id": "..."
}
```

### Schema Guard в действии

Попробуйте передать неверный параметр:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/call \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "greeter.hello",
    "params": {"name": 123},
    "context": {"caller_id": "test", "trace_stack": []}
  }'
```

Ответ (switchboard.py строка 47):

```json
{
  "status": "error",
  "type": "schema_validation_error",
  "details": [
    {
      "type": "string_type",
      "loc": ["name"],
      "msg": "Input should be a valid string",
      "input": 123
    }
  ],
  "correlation_id": "..."
}
```

**Как работает Schema Guard (switchboard.py строка 41):**

```python
adapter = self._get_adapter(envelope.domain)
if adapter:
    params = adapter.validate_python(envelope.params)
```

Метод `_get_adapter()` (строка 13) ищет схему в `Registry.get_schema()`, создаёт `TypeAdapter` и кэширует его:

```python
def _get_adapter(self, domain_query: str) -> Optional[TypeAdapter]:
    if domain_query in self._adapter_cache:
        return self._adapter_cache[domain_query]
    schema = registry.get_schema(domain_query)
    if schema:
        adapter = TypeAdapter(schema)
        self._adapter_cache[domain_query] = adapter
        return adapter
```

## Шаг 5: Добавление UI-виджета

Если плагину нужен интерфейс, укажите `ui` в manifest.json и поместите HTML/CSS/JS в `ui/`.

Пример `plugins/my_greeter/manifest.json` с UI:

```json
{
    "id": "my_greeter",
    "version": "1.0.0",
    "capabilities": ["greeter.hello"],
    "ui": {
        "widgets": [
            {
                "id": "greeter.widget",
                "size": "2x2",
                "entry_point": "/plugins/my_greeter/ui/index.html",
                "title": "Greeter"
            }
        ]
    }
}
```

UI-файлы монтируются в main.py (строка 61):

```python
for plugin_id in loader.loaded_plugins:
    plugin_path = loader.plugin_paths.get(plugin_id)
    if plugin_path:
        ui_path = os.path.join(plugin_path, "ui")
        if os.path.exists(ui_path):
            app.mount(f"/plugins/{plugin_id}/ui", StaticFiles(directory=ui_path), ...)
```

## Жизненный цикл плагина

```
Loader._load_plugin(plugin_path)
  ├── 1. Чтение manifest.json
  ├── 2. Валидация PluginManifest (Pydantic)
  ├── 3. Проверка compatibility_version >= SDK_VERSION
  ├── 4. Динамический импорт backend.py (importlib)
  ├── 5. Регистрация в Pluggy (plugin_instance)
  ├── 6. Регистрация в Registry (manifest + capabilities)
  ├── 7. Регистрация UI-расширений если manifest.ui
  └── 8. После загрузки всех: pm.hook.sh_plugin_init(registry=registry)
       └── BasePlugin.sh_plugin_init() — сканирует @capability и вызывает registry.register()
```

## Полный чеклист

- [ ] manifest.json с корректным `id` и `capabilities`
- [ ] `backend.py` с классом, наследующим `BasePlugin`
- [ ] глобальная переменная `plugin = MyPlugin()`
- [ ] метод с `@capability("domain.name")` и Pydantic-схемой
- [ ] `compatibility_version` совместима с SDK VERSION
- [ ] (UI) секция `ui.widgets` в manifest.json
- [ ] (UI) файлы в `ui/` с корректным `entry_point`

## Итог

Вы создали плагин, который:
- регистрирует capability `greeter.hello` и `greeter.goodbye` в Registry
- проходит Schema Guard (TypeAdapter + Pydantic) при каждом вызове
- доступен через `POST /api/v1/call`

Код плагина — это минимальный шаблон для расширения webSH.
