# Как добавить capability в webSH

Capability — это единица функциональности в webSH. Каждая capability представлена доменом (например, `fs.read`, `hello.ping`) и реализована в методе плагина, помеченном декоратором `@capability`.

## Через декоратор `@capability` (SDK-способ)

**Где:** `plugins/<имя_плагина>/backend.py`

```python
from core.sdk import BasePlugin, capability
from pydantic import BaseModel, Field

class MyParams(BaseModel):
    value: str = Field(..., description="Входной параметр")

class MyPlugin(BasePlugin):
    @capability("my.domain", schema=MyParams)
    async def my_handler(self, params: MyParams, context):
        # params.value — уже валидирован TypeAdapter
        # context.caller_id — кто вызвал
        # context.trace_stack — стек вызовов
        return {"result": f"Processed: {params.value}"}

plugin = MyPlugin()
```

**Что происходит:**

1. Декоратор `@capability` (sdk.py :127) устанавливает на метод флаги `_is_capability`, `_capability_domain`, `_capability_schema`.
2. Хук `sh_plugin_init` (sdk.py :63) сканирует все методы экземпляра и вызывает `registry.register()` для каждого помеченного.
3. `Registry.register()` (registry.py :18) сохраняет хендлер по ключу `"domain@version"`.
4. При вызове через `POST /api/v1/call` Switchboard находит хендлер через `registry.resolve()`, валидирует params через кэшированный `TypeAdapter`, и `await handler(params, context)`.

## Через прямой вызов Registry.register() (для динамических capability)

Если capability должна быть зарегистрирована условно (например, после проверки конфигурации), можно вызвать регистрацию напрямую:

```python
from core.registry import registry

async def dynamic_handler(params, context):
    return {"message": "Динамическая capability"}

registry.register(
    domain="my.dynamic",
    version="1.0.0",
    handler=dynamic_handler,
    schema=None  # можно передать Pydantic модель
)
```

## Без схемы (raw-params)

Если схема не нужна, `@capability` можно вызвать без аргумента `schema`:

```python
@capability("my.raw")
async def raw_handler(self, params, context):
    # params — сырой dict (не проверяется)
    return {"echo": params}
```

В этом случае Switchboard пропускает шаг Schema Guard (switchboard.py :41):

```python
adapter = self._get_adapter(envelope.domain)
if adapter:  # adapter is None
    params = adapter.validate_python(envelope.params)
```

## Capability с версионированием

Registry поддерживает версионирование через ключи `"domain@version"`. Для вызова конкретной версии укажите `@` в domain:

```python
# Регистрация
registry.register("my.domain", "2.0.0", handler_v2, schema_v2)

# Вызов — явная версия
curl -X POST /api/v1/call \
  -d '{"domain": "my.domain@2.0.0", ...}'

# Вызов — неявная, берётся latest
curl -X POST /api/v1/call \
  -d '{"domain": "my.domain", ...}'
```

Механизм latest-версии (registry.py :25):

```python
if domain not in self._latest_versions or version > self._latest_versions[domain]:
    self._latest_versions[domain] = version
```

## Проверка регистрации

```bash
# Все плагины и их capability
curl http://127.0.0.1:8000/api/v1/plugins

# Все capability плагина hello_world
curl http://127.0.0.1:8000/api/v1/plugins | jq '.[] | select(.id=="hello_world")'
```

## Capability, вызывающая другую capability

Из метода плагина можно вызвать другую capability через HTTP (сам на себя) или напрямую через registry:

```python
from core.registry import registry
from core.schemas import Context

class MyPlugin(BasePlugin):
    @capability("my.composite")
    async def composite(self, params, context):
        # Прямой вызов через Registry (без HTTP)
        handler = registry.resolve("hello.ping")
        if handler:
            result = await handler({"name": "from_composite"}, context)
            return {"inner_result": result}
        return {"error": "hello.ping not found"}
```

## Правила и ограничения

| Правило | Причина |
|---------|---------|
| Имя домена — строка с точкой (`.`), например `fs.list` | Switchboard и Registry используют `domain` как ключ |
| Не регистрируйте домены, начинающиеся с `kernel.` или `system.` | Зарезервировано для системных capability |
| Сигнатура хендлера: `async def handler(params, context)` | Switchboard вызывает `handler(params, context)` |
| Возвращаемое значение должно быть сериализуемо в JSON | FastAPI преобразует ответ в ORJSONResponse |
| Не меняйте `context.trace_stack` внутри хендлера | Trace check защищает от циклов |

## Типовые ошибки

| Ошибка | Причина | Исправление |
|--------|---------|-------------|
| `No provider found for domain: xxx` | Capability не зарегистрирована | Проверьте `@capability` и manifest.json |
| `Input should be a valid string` | Schema Guard отклонил params | Сверьте тип параметра с Pydantic схемой |
| Handler не async | Switchboard ожидает coroutine | Добавьте `async def` |
| `'coroutine' object is not iterable` | Забыли `await` при вызове хендлера | `result = await handler(...)` |

## Итог

Добавление capability сводится к трём строкам кода: декоратор `@capability`, Pydantic-схема (опционально), и вызов `registry.register()` автоматически через SDK.
