# Design Document: PC Center OS (v11.0)

Этот документ описывает архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM.

> **Революция Архитектуры (v11.0):** Реализация **"Single Process Architecture" (Единый Процесс)**. FastAPI становится "Единым Окном", раздавая API, основной Shell и UI плагинов на одном порту (8000), устраняя необходимость в Node.js/Nginx на продакшене.

---

## 1. Концепция: FastAPI как Контент-Менеджер

В этой модели Ядро выполняет три роли одновременно:
1.  **API Маршруты:** Обрабатывают сигналы (`/api/v1/call`).
2.  **Статика Шелла:** Раздает ядро системы (Рабочий стол) из папки `dist/`.
3.  **Статика Плагинов:** Динамически «подмешивает» папки плагинов в общее дерево URL.

**Преимущества:**
*   **Zero CORS:** Фронтенд и бэкенд живут на одном домене/порту.
*   **Атомарность:** Плагин — это папка. Загрузил — и он доступен и в API, и в UI.
*   **Безопасность:** FastAPI Middleware может защищать даже статические файлы плагинов.

---

## 2. Реализация Ядра (Single Process Code)

`main.py` динамически монтирует UI плагинов.

```python
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# 1. Загрузка Backend-логики (см. v9.0)
# load_plugin_backends()

# 2. Динамическое монтирование UI плагинов
def mount_plugin_uis():
    plugins_path = "./plugins"
    for plugin_id in os.listdir(plugins_path):
        ui_dir = os.path.join(plugins_path, plugin_id, "ui")
        if os.path.isdir(ui_dir):
            # Теперь UI плагина доступен по адресу: /plugins/{id}/ui/index.js
            app.mount(
                f"/plugins/{plugin_id}/ui",
                StaticFiles(directory=ui_dir),
                name=f"ui_{plugin_id}"
            )

mount_plugin_uis()

# 3. Монтирование основного UI (Shell)
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

    # SPA Handler (отдает index.html на все остальные пути)
    @app.get("/{full_path:path}")
    async def serve_gui(full_path: str):
        return FileResponse("dist/index.html")
```

---

## 3. Обнаружение UI-расширений

Чтобы Шелл узнал, какие скрипты загружать, Ядро предоставляет API.

### 3.1. Эндпоинт `GET /api/v1/ui/extensions`
Ядро сканирует манифесты и возвращает список точек входа.

```json
[
  {
    "slot": "sidebar",
    "plugin_id": "task_tracker",
    "entry": "/plugins/task_tracker/ui/Icon.js"
  }
]
```

### 3.2. Динамический Импорт (Client-Side)
Шелл использует этот путь для импорта модуля.

```javascript
// Код внутри Shell UI (Svelte)
async function loadPluginUI(pluginId) {
    // Прямой импорт из FastAPI статики!
    const module = await import(`/plugins/${pluginId}/ui/index.js`);
    return module.default;
}
```

---

## 4. Режим Разработки (Dev Mode)

В продакшене FastAPI отдает статику. В разработке нам нужен Hot Module Replacement (HMR).

**Стратегия `DEV_MODE`:**
1.  **True (Dev):** Ядро возвращает ссылки на Vite Dev Server (`http://localhost:5173/src/plugins/...`).
2.  **False (Prod):** Ядро возвращает ссылки на скомпилированную статику (`/plugins/...`).

Это позволяет разработчику видеть изменения мгновенно, а пользователю — запускать систему одной командой `python main.py`.
