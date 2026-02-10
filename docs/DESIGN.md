# Design Document: PC Center OS (v7.0)

Этот документ описывает архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM.

> **Революция Архитектуры (v7.0):** Переход на модель **"Reactive Dispatcher" (Реактивный Диспетчер)**. Реализуется гибридная архитектура "Switchboard", сочетающая In-Memory Service Bus (для скорости) и HTTP Gateway (для микросервисов).

---

## 1. Философия: Ядро как Реактивный Диспетчер

Шина Ядра состоит из трех независимых слоев:
1.  **Registry (Реестр):** База данных «способностей» (Capabilities). Хранит не код, а «адреса» и Pydantic-схемы.
2.  **Dispatcher (Диспетчер):** Логика поиска провайдера по ограничениям (constraints) и валидация пакетов.
3.  **Transport (Транспорт):** Адаптеры, которые знают, как доставить сигнал (локальный вызов `asyncio`, HTTP POST или WebSocket).

---

## 2. Реализация Шины (The Switchboard)

### 2.1. Пакет Сигнала (Универсальный Конверт)
Мы используем `pydantic.JsonSchemaValue`, чтобы ядро могло валидировать данные, даже не имея импортированного класса модели плагина.

```python
from pydantic import BaseModel, AnyHttpUrl
from typing import Any, Dict, Optional

class CapabilityEnvelope(BaseModel):
    domain: str             # например, "ai.image.gen"
    params: Dict[str, Any]  # Данные
    context: Dict[str, Any] # Метаданные (auth, correlation_id)
```

### 2.2. Логика Диспетчера (Core Bus)
Ядро работает как «умный прокси».

```python
class Switchboard:
    def __init__(self):
        self.registry = {} # {domain: [ProviderObject]}

    async def call(self, domain: str, params: dict, constraints: dict = None):
        # 1. Поиск провайдера
        providers = self.registry.get(domain, [])
        provider = self._select_best_provider(providers, constraints)

        # 2. Валидация (ядро проверяет params по сохраненной JSON-схеме провайдера)
        self._validate_params(params, provider.input_schema)

        # 3. Маршрутизация на транспорт
        return await provider.transport.send(params)

    async def emit(self, event_name: str, data: dict):
        """Для интеграционных точек (Pub/Sub)"""
        # Рассылка всем подписчикам (Shell, Logs, и т.д.)
        pass
```

---

## 3. Транспортная Стратегия (Hybrid Transport)

Мы используем **Internal Asyncio + HTTP Proxy**. Это позволяет ядру оставаться «тонким» (без Redis), но подключать любые сервисы.

| Технология | Использование | Плюсы |
|---|---|---|
| **Internal Asyncio** | Локальные Python-плагины | Максимальная скорость, zero-latency. |
| **HTTP (FastAPI)** | Внешние микросервисы (Docker) | Языковая независимость, масштабируемость. |

### Как это работает:
1.  **Микросервисы (HTTP Transport):** Если провайдер — это Docker-контейнер, его `transport.send` просто делает `httpx.post()`. Для вызывающего плагина это прозрачно.
2.  **Параметры (Constraints):** В вызов `call` передаются `constraints={"gpu": True}`. Диспетчер фильтрует провайдеров, у которых в метаданных есть GPU.

---

## 4. Capability System 2.0: Реестр Схем

Ядро хранит `input_schema` каждого плагина в JSON-виде. При вызове оно использует `pydantic.TypeAdapter` (или аналог), чтобы проверить, что плагин-отправитель не шлет мусор, не импортируя код провайдера.

---

## 5. UI и Интеграция (Pub/Sub)

Интеграционные точки (Slots) работают через `bus.emit`.

1.  **Shell Plugin:** "Я хочу отрисовать Sidebar". Подписывается на событие `ui.sidebar.inject`.
2.  **User Plugin:** Делает `bus.emit("ui.sidebar.inject", {...})`.
3.  **Shell:** Получает событие и обновляет UI.

---

## 6. Итоговая Структура Системы

*   **Task-система:** Плагин, регистрирующий `core.execute`. Принимает `params` и уводит их в воркер.
*   **Desktop:** Плагин, подписанный на `ui.slot.*`. Визуализирует поток данных из шины.
*   **Storage:** Плагин, реализующий `data.access`.

Ядро превратилось в чистый **Реактивный Диспетчер**, управляющий потоками данных между независимыми агентами.
