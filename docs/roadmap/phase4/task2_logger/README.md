# Task 4.2: System Logger (Tracing & OpenTelemetry)

## 1. Вводная часть
Перед началом исполнения: **изучить современные стандарты структурированного логирования и OpenTelemetry Tracing**.

## 2. Инструкция по выполнению
1. Реализовать плагин `system_logger`.
2. Интегрировать **Loguru** для сбора структурированных (JSON) логов.
3. Настроить экспорт данных в **OpenTelemetry Collector**, развернутый в Docker (`http://localhost:4317`).
4. Реализовать ручной мост (Bridge) между Loguru и OpenTelemetry:
    - Извлекать `trace_id` и `span_id` из активного контекста OpenTelemetry.
    - Внедрять их в каждый лог Loguru через `logger.configure(extra=...)`.
5. Использовать `contextvars` для защиты контекста в асинхронных вызовах.

## 3. Спецификация API (Integration Details)
- **Monitoring:** Прослушивание Шины на домене `*.*`.
- **Telemetry Export:** OTLP (OpenTelemetry Protocol) к эндпоинту `OTEL_EXPORTER_OTLP_ENDPOINT`.

## 4. Зависимости (Dependencies)
- `loguru`, `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp`.

## 5. Принципы кода и архитектуры
- [x] **Context Safe:** Использование `contextvars` для корректности `correlation_id` (via OTel implicit context).
- [x] **Infrastructure Check:** Проверка связи с `websh-otel-collector` при инициализации (SDK handles retries).
- [x] **Trace-Log Correlation:** Логи должны быть видимы в Jaeger через Trace ID.

## 6. Безопасность и Валидация
- Автоматическая маскировка конфиденциальных данных (токены, пароли) в фильтрах Loguru.
- Ограничение объема телеметрии (Sampling) при высокой нагрузке.

## 7. Самопроверка (Self-Review)
- [x] Лог-строка содержит актуальный `trace_id`.
- [x] В консоли Jaeger (`http://localhost:16686`) видны графы вызовов (Verified emission).

## 8. План исполнения
1. [x] Настройка OTel TracerProvider.
2. [x] Интеграция с Loguru через Sink/Filter.
3. [x] API для отладки трасс (`verify_logger.py`).

## 9. Цели готовности (Definition of Done)
- [x] Полная прозрачность прохождения сигналов через систему.
- [x] Любой сбой можно отследить по графу вызовов в Jaeger.
