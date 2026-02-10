# Design Document: PC Center OS (v6.0)

Этот документ описывает архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM.

> **Революция Архитектуры (v6.0):** Переход на модель **"Minimal Broker Core"**. Ядро — это абсолютно пустая «шина» (Switchboard), которая не владеет даже системой фоновых задач. Taskiq/Celery вынесены в `core.executor`.

---

## 1. Философия: Ядро как Диспетчер Сигналов

Ядро выполняет только три функции:
1.  **Registry (Реестр):** Хранит список того, кто что умеет (Capabilities) и куда можно встроиться (Integration Points).
2.  **Broker (Брокер):** Передает вызовы (Call) и данные (Context) от потребителя к поставщику, проверяя типы (Pydantic).
3.  **Loader (Загрузчик):** Запускает код плагинов (Python/JS) или регистрирует внешние микросервисы.

**Фоновые задачи (Task System):** Теперь выполнение тяжелых задач — это не встроенная функция ядра, а внешний ресурс `core.executor`, на который другие плагины подписываются через Брокера.

---

## 2. Архитектура Фоновых Вычислений (Executor as a Service)

### 2.1. Регистрация Task-системы (Провайдер)
Системный плагин (например, `system_taskiq`) регистрирует возможность выполнения задач.

```python
# plugins/system_taskiq/main.py
from core.broker import Capability

class TaskiqCapability(Capability):
    domain = "core.executor"
    # Метаданные о мощностях
    metadata = { "concurrency": 4, "queues": ["default", "heavy"] }

    class Input(BaseModel):
        plugin_id: str
        function_name: str
        args: dict
        priority: str = "medium"

    async def execute(self, params: Input):
        # Логика отправки задачи в воркер Taskiq
        task = await broker_taskiq.send_task(
            params.plugin_id,
            params.function_name,
            params.args
        )
        return {"task_id": task.id}
```

### 2.2. Заказ Исполнения (Потребитель)
Плагины не знают про Taskiq. Они просто просят Ядро найти `core.executor`.

```python
# plugins/deduplicator/logic.py

async def start_dedup(files):
    # Запрашиваем у ядра исполнителя
    executor = await kernel.find_capability(domain="core.executor")

    # Отправляем задачу
    await executor.execute(
        plugin_id="deduplicator",
        function_name="process_files",
        args={"files": files}
    )
```

---

## 3. Capability System 2.0: Параметризация

Capability — это объект с метаданными и схемой параметров. Это позволяет гибко выбирать провайдеров (например, "быстрый LLM" или "бесплатный LLM").

---

## 4. UI как Плагин (The Shell Concept)

Ядро при старте отдает пустой `index.html`. `bootstrap.js` запрашивает `/api/core/shell`, и Ядро перенаправляет на активный плагин-оболочку (например, `system_desktop_v2`).

*   **Integration Points:** Плагины инжектируются в UI через слоты, регистрируемые Shell-плагином.

---

## 5. Микросервисы как Capabilities

Ядро умеет работать с внешними Docker-контейнерами. Они регистрируются как Capabilities, и Ядро проксирует вызовы к ним. Это позволяет выносить тяжелые вычисления (AI, GPU) на другие машины.

---

## 6. Итоговая Структура Ядра (The Ultra-Thin Kernel)

Ядро — это "умный коммутатор".

### 6.1. Состав Системы
1.  **Kernel (The Switchboard):** Реестр ссылок и валидатор Pydantic-пакетов.
2.  **System Plugin `storage`:** Реализует Capability `data.access` (LanceDB/SQLite).
3.  **System Plugin `executor`:** Реализует Capability `core.executor` (Taskiq).
4.  **System Plugin `shell`:** Реализует Capability `ui.shell` (Рабочий стол).
5.  **System Plugin `auth`:** Реализует Capability `core.identity`.

### 6.2. Обработка Результатов (Callback Pattern)
Если Task-система вынесена в плагин, результат возвращается через события:
1.  Плагин-исполнитель заканчивает задачу.
2.  Он кидает в общую шину Ядра событие `task.finished` с `correlation_id`.
3.  Плагин-заказчик подхватывает результат.

### 6.3. Преимущества
*   **Свобода технологий:** Замените Taskiq на Celery или Ray без изменения кода плагинов.
*   **Распределенность:** Ядро на ноутбуке, Executor на сервере с GPU.
*   **Микросервисность:** Executor может быть внешним Docker-контейнером.

Ядро теперь полностью развязано с реализацией и занимается только маршрутизацией.
