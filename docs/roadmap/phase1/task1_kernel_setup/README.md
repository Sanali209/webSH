# Task 1.1: Kernel Core & FastAPI Setup

## 1. Вводная часть
Перед началом исполнения: **детально изучить текущую архитектуру в `docs/DESIGN.md` и `docs/DESIGN_EXTENDED.md`**.

## 2. Инструкция по выполнению
1. Создать виртуальное окружение Python 3.11 (`python -m venv venv`).
2. Настроить файл `.gitignore` (исключить `venv/`, `__pycache__/`, `.env`, файлы данных БД).
3. **Развернуть инфраструктуру:** Запустить `docker compose up -d` для запуска Redis и Jaeger.
4. Настроить базовое FastAPI приложение в `main.py`.
5. Реализовать "Dashboard" старт-скрин через `rich.layout.Layout`, отображая статус всех подсистем и подключение к Docker-сервисам.
6. Организовать базовую структуру папок согласно `docs/DESIGN.md` (раздел 8).

## 3. Спецификация API (Integration Details)
- **Endpoints:**
    - `GET /health` -> Возвращает статус Ядра и доступность Redis/OTel.
- **Environment:**
    - `REDIS_URL=redis://localhost:6379/0`
    - `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`

## 4. Зависимости (Dependencies)
- `fastapi`, `uvicorn`, `rich`, `loguru`, `pydantic-settings`, `redis`.

## 5. Принципы кода и архитектуры
- [ ] **Type Safety:** Использование Python 3.11+ Type Hints и `Annotated` для валидации.
- [ ] **Validation Speed:** Использование `model_validate_json()` для входящих пакетов.
- [ ] **Infrastructure Check:** При старте ядро должно проверять доступность Redis и OTel Collector.
- [ ] **Clean Startup:** Грейсфул-шатдаун и очистка ресурсов.

## 6. Безопасность и Валидация
- Валидация всех переменных окружения через `Pydantic Settings`.
- Обработка ConnectionError при недоступности Docker-сервисов.

## 7. Самопроверка (Self-Review)
- [ ] Сервер запускается и отвечает на пинг.
- [ ] В логах Rich отображается "Redis: CONNECTED".
- [ ] Отсутствуют висящие процессы после завершения.

## 8. План исполнения
1. [ ] Создание и активация `venv`, установка базовых зависимостей.
2. [ ] Запуск Docker-контейнеров.
3. [ ] Создание `.gitignore`.
4. [ ] Инициализация `main.py` и проверка соединений.
5. [ ] Настройка эндпоинта `/health`.

## 9. Цели готовности (Definition of Done)
- [ ] Сервер запускается и видит инфраструктуру.
- [ ] Код соответствует принципам SOLID.
- [ ] Документированы команды для запуска.
