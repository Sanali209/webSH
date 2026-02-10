# Design Document: PC Center OS (v5.0)

Этот документ описывает архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM.

> **Революция Архитектуры (v5.0):** Переход на модель **"Broker / Switchboard" (Брокер / Коммутатор)**. Ядро перестает быть операционной системой и становится Диспетчером. Оно ничего не знает ни о UI, ни о файлах. Оно знает только о Контрактах и Маршрутах.

---

## 1. Философия: Ядро как Брокер

Ядро выполняет только три функции:
1.  **Registry (Реестр):** Хранит список того, кто что умеет (Capabilities) и куда можно встроиться (Integration Points).
2.  **Broker (Брокер):** Передает вызовы (Call) и данные (Context) от потребителя к поставщику, проверяя типы (Pydantic).
3.  **Loader (Загрузчик):** Запускает код плагинов (Python/JS) или регистрирует внешние микросервисы.

**Desktop (Рабочий стол)** теперь — это просто один из плагинов с capability `ui.shell`. Вы можете заменить его на `ui.terminal` или `ui.voice_assistant`, не меняя ни строчки в ядре.

---

## 2. Capability System 2.0: Параметризация

Теперь Capability — это не просто строка "ocr". Это объект с метаданными и схемой параметров.

### 2.1. Регистрация Capability (со стороны Провайдера)
Плагин объявляет свои возможности, описывая схемы входа и выхода.

```python
# plugins/local_llm/main.py
from core.broker import Capability

class LLMCapability(Capability):
    domain = "ai.text_generation"
    # Параметры, описывающие мощность этого провайдера
    metadata = {
        "model": "llama3-8b",
        "speed": "fast",
        "cost": 0.0
    }

    class Input(BaseModel):
        prompt: str
        temperature: float = 0.7

    class Output(BaseModel):
        text: str

    async def execute(self, params: Input) -> Output:
        return await run_llama(params.prompt)
```

### 2.2. Вызов Capability (со стороны Потребителя)
Потребитель просит Ядро найти подходящий сервис, используя фильтрацию (Constraints).

```python
# plugins/task_tracker/logic.py

# Запрос с фильтрацией по параметрам!
provider = await kernel.find_capability(
    domain="ai.text_generation",
    constraints={
        "speed": "fast",     # Хочу быстрый
        "cost": 0.0          # Хочу бесплатный
    }
)

result = await provider.execute(prompt="Суммируй задачу...")
```

---

## 3. UI как Плагин (The Shell Concept)

Ядро при старте вообще не отдает HTML с интерфейсом. Оно отдает пустой `index.html` с маленьким загрузчиком (`bootstrap.js`).

1.  **Загрузка:** `bootstrap.js` спрашивает у Ядра: `GET /api/core/shell`.
2.  **Ядро:** Смотрит в конфиг, видит, что активный шелл — плагин `system_desktop_v2`.
3.  **Ответ:** Ядро возвращает URL скрипта плагина: `/plugins/system_desktop_v2/ui/main.js`.
4.  **Рендер:** Браузер загружает этот JS, и только тогда появляется рабочий стол.

**Преимущества:**
*   Разные интерфейсы для ПК, Планшета и Телефона (переключение плагина shell).
*   Автоматический fallback на `safe_mode_shell` (консольный UI), если основной UI упал.

---

## 4. Динамические Точки Интеграции (Integration Points)

Ядро не знает про существование "Сайдбара" или "Трея". Это знает Shell Plugin. Другие плагины инжектируются туда через брокер.

1.  **Shell Plugin регистрирует Slot:**
    ```python
    kernel.register_slot(
        slot_id="desktop.sidebar",
        schema=SidebarItemSchema # Pydantic-модель иконки
    )
    ```

2.  **User Plugin (TaskTracker) отправляет Injection Request:**
    ```python
    kernel.inject(
        slot_id="desktop.sidebar",
        data=SidebarItemSchema(icon="check", action="open_tasks")
    )
    ```

3.  **Ядро:** Проверяет валидность `SidebarItemSchema` и пересылает данные в Shell Plugin.
4.  **Shell Plugin:** Реактивно отрисовывает новую иконку.

---

## 5. Микросервисы как Capabilities

Ядро умеет работать с внешними Docker-контейнерами (например, тяжелый Stable Diffusion) так же, как с Python-функциями.

### 5.1. Регистрация через API
Микросервис при старте стучится в Ядро:

```http
POST /api/core/capabilities/register
{
  "domain": "ai.image_gen",
  "provider_id": "remote_sd_xl",
  "metadata": { "gpu": true, "version": "xl" },
  "transport": "http",
  "endpoint": "http://localhost:7860/generate",
  "input_schema": { ... },
  "output_schema": { ... }
}
```

### 5.2. Проксирование Ядром
Когда плагин вызывает `ai.image_gen`:
1.  Ядро видит, что провайдер — это HTTP Microservice.
2.  Ядро валидирует входные данные (Pydantic).
3.  Ядро само делает HTTP-запрос на `http://localhost:7860/generate`.
4.  Ядро возвращает результат вызывающему плагину.

**Итог:** Ваш Python-плагин вызывает генерацию картинки и не знает, кто её сделал: локальная функция или удаленный сервер.

---

## 6. Итоговая Структура Ядра (The Broker Kernel)

```text
/core
├── broker.py          # Маршрутизация вызовов, поиск Capability
├── registry.py        # Хранение метаданных (кто, где, какие параметры)
├── injection.py       # Управление слотами (Integration Points)
├── proxy.py           # Адаптер для HTTP микросервисов
└── loader.py          # Запуск локальных Python-плагинов
```

### Пример потока данных (Data Flow)
1.  **Plugin A (Shell):** "Я рисую рабочий стол. У меня есть слот `widget_area`."
2.  **Plugin B (Clock):** "Я умею показывать время. Я инжектируюсь в `widget_area`."
3.  **Plugin C (Voice):** "Я микросервис (Docker). Я регистрирую capability `audio.transcribe`."
4.  **Plugin D (Notes):** "Пользователь нажал 'Диктовать'. Ядро, дай мне кто-нибудь с `audio.transcribe`!"
5.  **Ядро:** "Ок, вот Plugin C. Я проксирую твой аудио-поток к нему."

### Главное преимущество
Вы полностью развязали руки.
*   Хотите сменить базу данных? Напишите плагин `db_postgres`, который реализует capability `storage.vector`.
*   Хотите переписать UI на React? Напишите плагин `react_shell`.
*   Хотите добавить интеграцию с Home Assistant? Зарегистрируйте его как внешний микросервис.

Ядро останется неизменным — ~300 строк кода, перекладывающего JSON и Pydantic объекты.
