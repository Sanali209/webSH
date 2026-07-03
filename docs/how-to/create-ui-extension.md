# Как создать UI-расширение для webSH

UI-расширения позволяют добавлять виджеты, приложения, ярлыки и элементы TopBar на рабочий стол webSH. Они регистрируются через manifest.json плагина и загружаются фронтендом через `extensionLoader.ts`.

## Типы UI-расширений

| Тип | Pydantic-модель | Описание |
|-----|-----------------|----------|
| `widget` | `WidgetSchema` | iframe-виджет на рабочем столе (размеры: 1x1, 2x2, 2x1, 4x2) |
| `top_bar.item` | `TopBarItemSchema` | элемент в верхней панели |
| `application` | `ViewSchema` | полноэкранное приложение (загружается как компонент) |
| `shortcut` | `ShortcutSchema` | ярлык-иконка на рабочем столе |

## Шаг 1: Определите UI в manifest.json

Секция `ui` в manifest.json валидируется Pydantic-моделью `PluginUI` (schemas.py :55):

```python
class PluginUI(BaseModel):
    widgets: List[WidgetSchema] = Field(default_factory=list)
    views: List[ViewSchema] = Field(default_factory=list)
    shortcuts: List[ShortcutSchema] = Field(default_factory=list)
    top_bar: List[TopBarItemSchema] = Field(default_factory=list)
```

Пример для каждого типа:

```json
{
  "id": "my_extensions",
  "version": "1.0.0",
  "ui": {
    "widgets": [
      {
        "id": "my.ext.widget",
        "size": "2x2",
        "entry_point": "/plugins/my_extensions/ui/widget.html",
        "title": "Мой виджет"
      }
    ],
    "views": [
      {
        "id": "my.ext.app",
        "title": "Моё приложение",
        "entry_point": "app.html"
      }
    ],
    "shortcuts": [
      {
        "icon": "home",
        "title": "Домой",
        "action": "open:my.ext.app"
      }
    ],
    "top_bar": [
      {
        "id": "my.ext.status",
        "entry_point": "status.html",
        "component": null
      }
    ]
  }
}
```

**Code-first:** Модель `WidgetSchema` (schemas.py :24) использует `Literal["1x1", "2x2", "2x1", "4x2"]` для `size` и `extra='forbid'` — любые лишние поля приведут к ошибке валидации.

## Шаг 2: Регистрация UI-расширения

При загрузке плагина Loader вызывает (loader.py :109):

```python
if manifest.ui:
    registry.register_ui_extension(manifest.id, manifest.ui.model_dump())
```

`Registry.register_ui_extension()` (registry.py :72):

```python
def register_ui_extension(self, plugin_id: str, ui_data: Dict[str, Any]):
    self._ui_extensions[plugin_id] = ui_data
```

Альтернативно: через SDK, если UI определяется динамически (sdk.py :82):

```python
class MyPlugin(BasePlugin):
    def get_ui_manifest(self) -> Dict[str, Any]:
        return {
            "widgets": [{
                "id": "my.dynamic.widget",
                "size": "2x2",
                "entry_point": "/plugins/my_ext/ui/index.html",
                "title": "Dynamic Widget"
            }]
        }
```

## Шаг 3: Виджет с iframe (Penpal bridge)

Для iframe-виджетов webSH использует библиотеку Penpal для безопасной коммуникации между родительским окном и iframe.

**Родительская сторона** — `widgetBridge.ts`:

```typescript
import { connect, WindowMessenger } from 'penpal';

export const createConnection = (
    iframe: HTMLIFrameElement,
    methods: Record<string, any>
) => {
    const connection = connect({
        messenger: new WindowMessenger({
            remoteWindow: iframe.contentWindow!,
            allowedOrigins: ['*'],
        }),
        methods,
    });
    return {
        destroy: connection.destroy,
        promise: connection.promise,
    };
};
```

**Сторона iframe** (пример `plugins/clock/ui/index.html`):

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Clock</title></head>
<body>
<div id="clock"></div>
<script src="https://cdn.jsdelivr.net/npm/penpal@6/dist/penpal.min.js"></script>
<script>
const connection = Penpal.connect({
    methods: {
        getState: () => ({ time: new Date().toLocaleTimeString() }),
    }
});
connection.promise.then(parent => {
    // parent — методы, которые предоставляет webSH Shell
    // parent.call("hello.ping", {name: "Clock"})
});
</script>
</body>
</html>
```

## Шаг 4: Фронтенд — загрузка расширений

`extensionLoader.ts` загружает все расширения с бэкенда, преобразуя `entry_point` в URL и динамически импортируя компоненты:

```typescript
export async function loadExtensions(typeFilter?: string): Promise<Extension[]> {
    const response = await fetch('/api/v1/registry/ui-extensions');
    const data = await response.json();

    // Фильтрация по типу
    if (typeFilter === 'widget') items = data.widgets || [];
    else if (typeFilter === 'application') items = data.applications || [];
    // ...
}
```

**Логика разрешения URL** (extensionLoader.ts :53):

```typescript
if (!url.startsWith('/') && !url.startsWith('http')) {
    url = `/plugins/${item.plugin_id}/ui/${url}`;
}
```

Если `entry_point` заканчивается на `.html` — используется как iframe src. Иначе — динамический ES-импорт Svelte-компонента.

## Шаг 5: Добавление виджета на рабочий стол

`uiManager.ts` — `addWidget()`:

```typescript
export const addWidget = async (extension: Extension) => {
    // Определение размера
    let w = 1, h = 1;
    if (extension.type === 'widget') {
        const [width, height] = extension.size.split('x').map(Number);
        w = width || 2; h = height || 2;
    }

    // Поиск свободного места (gridManager.ts)
    const spot = findEmptySpot(currentWidgets, w, h);
    // ...

    // Создание WidgetConfig
    const newWidget = {
        id: crypto.randomUUID(),
        x: spot.x, y: spot.y, w, h,
        type: 'widget',
        component: `/plugins/${extension.plugin_id}/ui/${extension.entry_point}`
    };

    // Сохранение на бэкенд
    await syncWithBackend();
};
```

**Синхронизация с бэкендом** — `POST /api/v1/desktop/sync` отправляет массив `DesktopConfig` в LanceDB.

## Структура UI-файлов

Для каждого плагина UI-файлы монтируются автоматически в `main.py`:

```
plugins/my_extensions/
├── manifest.json
├── backend.py
└── ui/
    ├── widget.html       # iframe-виджет
    ├── app.html          # приложение
    ├── status.html       # top_bar элемент
    └── style.css
```

Монтирование (main.py :61):

```python
for plugin_id in loader.loaded_plugins:
    plugin_path = loader.plugin_paths.get(plugin_id)
    if plugin_path:
        ui_path = os.path.join(plugin_path, "ui")
        if os.path.exists(ui_path):
            app.mount(f"/plugins/{plugin_id}/ui", StaticFiles(directory=ui_path), ...)
```

## Проверка UI-расширений

```bash
# Все зарегистрированные UI-расширения (сгруппированы по типу)
curl http://127.0.0.1:8000/api/v1/registry/ui-extensions

# Проверка конкретного плагина
curl http://127.0.0.1:8000/health/ui/clock
# {"status": "available", "files": {"index.js": false, "manifest.json": false}}
```

## Продвинутые сценарии

### Динамический UI (через `get_ui_manifest`)

```python
class MyPlugin(BasePlugin):
    def get_ui_manifest(self):
        import json, os
        config_path = os.path.join("data", "my_ui_config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
        return {"widgets": []}
```

### Виджет с настройками

Используйте `get_settings_model()` и `get_settings_schema()` для генерации JSON Schema, которую фронтенд может применить в `SettingsModal.svelte`.

## Итог

UI-расширение создаётся добавлением секции `ui` в manifest.json плагина. Виджеты загружаются как iframe с Penpal-мостом, другие типы — как Svelte-компоненты. Синхронизация состояния рабочего стола идёт через POST/GET `/api/v1/desktop/sync`.
