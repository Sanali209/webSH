# Task 4.1: System Executor (Taskiq)

## 1. Вводная часть
Перед началом исполнения: **изучить роль Executor в `docs/DESIGN.md` раздел 5.2 и преимущества асинхронных воркеров**.

## 2. Инструкция по выполнение
1. Реализовать плагин `system_executor` на базе **Taskiq**.
2. В качестве брокера использовать **Redis**, развернутый в Docker (`redis://localhost:6379/0`).
3. Реализовать Capability `core.execute`, принимающую параметры функции и контекста.
4. Обеспечить публикацию события `task.finished` через Switchboard по завершении.

## 3. Спецификация API (Integration Details)
- **Broker:** `taskiq_redis.RedisAsyncBroker`.
- **Connection:** Чтение `REDIS_URL` из переменных окружения.
- **Signal In:** `core.execute(func_name, params, priority)`.
- **Signal Out:** `task.finished(correlation_id, status, result)`.

## 4. Зависимости (Dependencies)
- `taskiq`, `taskiq-redis`, `redis`.

## 5. Принципы кода и архитектуры
- [x] **Native Async:** Использование только асинхронных брокеров.
- [x] **Worker Isolation:** Каждая задача выполняется в отдельном инстансе воркера.
- [x] **Docker Dependency:** Перед запуском тестов убедиться, что контейнер `websh-redis` активен (или локальный Redis).

## 6. Безопасность и Валидация
- Whitelist разрешенных функций для выполнения.
- Валидация аргументов задачи через Pydantic перед отправкой в брокер.

## 7. Самопроверка (Self-Review)
- [x] Долгая задача (sleep 10s) не блокирует HTTP сервер Ядра.
- [x] Команда `docker ps` показывает активный контейнер Redis (или verified connection).

## 8. План исполнения
1. [x] Настройка Redis брокера в коде.
2. [x] Реализация Capability обработчика.
3. [x] Воркер-логика.

## 9. Цели готовности (Definition of Done)
- [x] Фоновое выполнение задач работает.
- [x] Система масштабируема путем добавления новых воркеров.
