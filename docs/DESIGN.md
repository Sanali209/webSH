# Design Document: PC Center OS (v9.0)

Этот документ описывает архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM.

> **Революция Архитектуры (v9.0):** Реализация **"FastAPI Thin Kernel" (Ультратонкое Ядро)**. Ядро работает как прокси между HTTP-запросами браузера и вызовами функций в Python-модулях, загружаемых динамически.

---

## 1. Архитектурная Схема

*   **Ядро (Kernel):** Запускает FastAPI и управляет жизненным циклом.
*   **FastAPI:**
    *   Служит шиной для API (`/api/v1/call`).
    *   Раздает основной Shell (Рабочий стол) из `dist/`.
    *   Динамически монтирует папки `/ui` каждого плагина как статические пути.
*   **Лоадер (Loader):** Ищет в папках плагинов файлы `backend.py` и импортирует их в память (importlib).

---

## 2. Структура Проекта

```text
/pc_center
├── main.py              # Запуск FastAPI и Ядра
├── /core                # Код Диспетчера (Switchboard)
├── /dist                # Скомпилированный Shell (UI Рабочего стола)
└── /plugins
    └── /my_plugin       # Папка плагина
        ├── manifest.json
        ├── backend.py   # Python-код (Исполняется Ядром)
        └── /ui          # JS/CSS (Раздается FastAPI как статика)
```

> **Важно:** Backend (Python) исполняется на сервере. Frontend (JS) раздается браузеру как статика и общается с сервером через API.

---

## 3. Реализация Ядра (Conceptual Code)

Ядро состоит из Диспетчера (Switchboard) и Лоадера.

```python
import os
import importlib.util
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# --- СЛОЙ ДИСПЕТЧЕРА (SWITCHBOARD) ---
class Switchboard:
    def __init__(self):
        self.capabilities = {} # Реестр функций

    def register(self, manifest, backend_module):
        plugin_id = manifest["id"]
        for cap in manifest.get("capabilities", []):
            domain = cap["domain"]
            self.capabilities[domain] = {
                "plugin_id": plugin_id,
                "handler": getattr(backend_module, "handle_signal"),
                "schema": cap["input_schema"]
            }

bus = Switchboard()

# --- ЛОАДЕР ПЛАГИНОВ ---
def load_plugins():
    plugins_root = "./plugins"
    for folder in os.listdir(plugins_root):
        path = os.path.join(plugins_root, folder)

        # 1. Читаем манифест
        # ... (json.load manifest.json)

        # 2. Исполняем Backend (Python)
        spec = importlib.util.spec_from_file_location(f"p_{folder}", f"{path}/backend.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Регистрируем возможности
        bus.register(manifest, module)

        # 3. Раздаем Frontend (Static)
        ui_path = f"{path}/ui"
        if os.path.exists(ui_path):
            app.mount(f"/plugins/{manifest['id']}/ui", StaticFiles(directory=ui_path))
```

---

## 4. API и Поток Данных

### 4.1. Вызов Capability (API Broker)
Frontend (JS) делает POST-запрос, чтобы вызвать функцию Backend (Python).

```http
POST /api/v1/call
{
  "domain": "ai.text.summarize",
  "params": { "text": "..." }
}
```

**Обработчик в Ядре:**
```python
@app.post("/api/v1/call")
async def call_capability(signal: dict):
    domain = signal.get("domain")
    if domain in bus.capabilities:
        handler = bus.capabilities[domain]["handler"]
        return await handler(signal["params"])
    return {"error": "Capability not found"}
```

### 4.2. Загрузка UI (Shell)
1.  Пользователь открывает `localhost:8000`.
2.  FastAPI отдает `dist/index.html` (Shell).
3.  Shell загружается и запрашивает список плагинов.
4.  Shell динамически импортирует JS-модули плагинов по путям `/plugins/{id}/ui/index.js`.

---

## 5. Преимущества Реализации

1.  **Чистое разделение:** Backend — в памяти Python, Frontend — в браузере.
2.  **Модульность:** Плагины полностью изолированы в своих папках.
3.  **Производительность:** Прямой вызов Python-функций (без HTTP overhead для локальных плагинов) через `getattr`.
4.  **Простота:** Весь механизм ядра умещается в ~100 строк кода.
