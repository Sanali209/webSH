# Design Document: PC Center OS (v8.0)

Этот документ описывает архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM.

> **Революция Архитектуры (v8.0):** Стандартизация **"Handshake Protocol" (Протокол Рукопожатия)**. Это единственный момент, когда Ядро «всматривается» в плагин. После регистрации Ядро работает как почтальон, пересылая пакеты данных через Реактивный Диспетчер.

---

## 1. Философия: Ядро как Реестр и Диспетчер

Шина Ядра состоит из трех независимых слоев:
1.  **Registry (Реестр):** База данных «способностей» (Capabilities). Хранит манифесты и схемы.
2.  **Dispatcher (Диспетчер):** Логика поиска провайдера и валидация пакетов.
3.  **Transport (Транспорт):** Адаптеры (Internal Asyncio + HTTP Gateway).

---

## 2. Handshake Protocol (Протокол Регистрации)

Каждый модуль (Python-плагин или Docker-контейнер) отправляет Ядру **Manifest Payload** в формате JSON при старте.

### 2.1. Формат Манифеста
```json
{
  "id": "go_ocr_service",
  "type": "remote",
  "endpoint": "http://192.168.1.50:9000/process",
  "version": "1.0.0",
  "capabilities": [ ... ],
  "integrations": { ... }
}
```

**Основные поля (Header):**
| Поле | Тип | Описание |
|---|---|---|
| `id` | string | Уникальный ID (slug, н-р `task_tracker`). |
| `type` | enum | `local` (Python), `remote` (HTTP), `internal` (Core Module). |
| `endpoint` | url? | URL для remote плагинов (куда Ядру слать сигналы). |
| `version` | string | Версия плагина (SemVer). |

### 2.2. Секция Capabilities (Возможности)
Плагин описывает свои функции и схемы данных (JSON Schema).

```json
"capabilities": [
  {
    "domain": "ai.text.summarize",
    "description": "Суммаризация текстов через Llama3",
    "metadata": {
      "speed": "fast",
      "is_offline": true,
      "max_tokens": 8192
    },
    "input_schema": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "length": { "type": "integer", "default": 100 }
      },
      "required": ["text"]
    },
    "output_schema": {
       "type": "object",
       "properties": {
         "summary": { "type": "string" }
       }
    }
  }
]
```

### 2.3. Секция Integration Points (Слоты)
Плагин объявляет, куда он хочет встроиться.
*   **Consumers (Подписчики):** Слушают события.
*   **Producers (Инжекторы):** Вставляют свой UI/данные в чужой слот.

```json
"integrations": {
  "slots": [
    {
      "id": "ui.sidebar.action",
      "component_url": "/ui/sidebar_icon.js",
      "priority": 10
    },
    {
      "id": "ui.context_menu.file",
      "label": "Прочитать содержимое",
      "icon": "book-open"
    }
  ]
}
```

---

## 3. Signal Protocol (Протокол Обмена)

После регистрации общение происходит через унифицированные Сигналы.

### 3.1. Структура Сигнала (Request)
```json
{
  "correlation_id": "uuid-v4",
  "domain": "ai.text.summarize",
  "params": {
    "text": "Длинный текст для анализа...",
    "length": 50
  },
  "context": {
    "caller_id": "web_parser",
    "timestamp": 1739185472
  }
}
```

### 3.2. Алгоритм Обработки (The Broker Logic)
Когда Ядро получает Сигнал, оно проходит 4 стадии:

1.  **Discovery (Поиск):** Находит в Реестре всех провайдеров домена (н-р, `ai.text.summarize`).
2.  **Filtering (Фильтрация):** Если в запросе были `constraints` (н-р, `is_offline: true`), отсеивает неподходящих.
3.  **Validation (Валидация):** Берет `params` и проверяет их на соответствие `input_schema` провайдера.
    *   *Security Guard:* Если данные невалидны — Ядро возвращает ошибку 422, даже не беспокоя провайдера.
4.  **Dispatch (Доставка):**
    *   Для `local`: Вызывает асинхронную функцию в Python.
    *   Для `remote`: Делает HTTP POST запрос на `endpoint` провайдера.

---

## 4. Пример: Внешний Микросервис (Go OCR)

Представь, что отдельно запущен сервис на Go, который делает OCR. Он регистрируется через API Ядра:

```json
{
  "id": "go_ocr_service",
  "type": "remote",
  "endpoint": "http://192.168.1.50:9000/process",
  "version": "1.0.0",
  "capabilities": [
    {
      "domain": "vision.ocr",
      "metadata": { "languages": ["ru", "en"], "gpu": false },
      "input_schema": {
        "type": "object",
        "properties": { "image_url": { "type": "string" } }
      }
    }
  ],
  "integrations": {
    "slots": [
      { "id": "ui.file_preview.image", "label": "Распознать текст" }
    ]
  }
}
```

---

## 5. Преимущества Спецификации

1.  **Унификация:** Для Ядра нет разницы между «функцией в соседней папке» и «сервером в другой стране».
2.  **Безопасность:** Ядро работает как Schema Guard. Если плагин-отправитель попытается взломать плагин-получатель, отправив кривой JSON, Ядро это заблокирует.
3.  **Динамичность:** Можно зарегистрировать новый Capability прямо во время работы системы (через консоль или скрипт), и он тут же станет доступен всем.
