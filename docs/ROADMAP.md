# Roadmap: PC Center OS (v2.1)

Этот документ описывает план разработки **PC Center** по стадиям, от базового ядра до полноценной экосистемы плагинов.

---

## Phase 1: Core Micro-OS Foundation (Фундамент Микроядра)
**Цель:** Создать стабильную, изолированную платформу, способную загружать и управлять плагинами.

- [ ] **Project Setup:**
  - [ ] Структура репозитория (`/core`, `/plugins`, `/web`, `/tests`).
  - [ ] Настройка окружения (Poetry/Pipenv, Docker Compose).
  - [ ] Базовый `main.py` с FastAPI.

- [ ] **Core SDK Implementation:**
  - [ ] Разработка базового класса `PluginBase`.
  - [ ] Создание хелперов для работы с БД и Taskiq.
  - [ ] Определение стандартных Pydantic-моделей для настроек.

- [ ] **Plugin System (Pluggy):**
  - [ ] `PluginManager`: Логика сканирования `/plugins` и чтения `manifest.json`.
  - [ ] `DependencyGraph`: Проверка зависимостей и порядка загрузки.
  - [ ] `LifecycleHooks`: Реализация хуков `on_load`, `on_activate`.

- [ ] **Testing Infrastructure:**
  - [ ] **Unit Tests:** Покрытие тестами компонентов ядра (EventBus, PluginManager).
  - [ ] **Integration Tests:** Тесты загрузки фиктивных плагинов.

- [ ] **Event Orchestrator & Tracing:**
  - [ ] Асинхронная шина событий (`AsyncEventBus`).
  - [ ] Интеграция `Loguru` + `correlation_id` для трассировки событий.
  - [ ] WebSocket-шлюз для трансляции событий на фронтенд.

- [ ] **API Gateway & Isolation:**
  - [ ] Динамическое монтирование роутов (`app.include_router`).
  - [ ] `SandboxMiddleware`: Перехват исключений плагинов (Error Boundaries).

---

## Phase 2: Data & Search Engine (Движок Данных и Поиска)
**Цель:** Реализовать "Single Source of Truth" на базе LanceDB и обеспечить безопасный доступ к данным.

- [ ] **LanceDB Core Integration:**
  - [ ] Подключение и инициализация `Core Metadata Table`.
  - [ ] Схема данных Core (PyArrow): `entity_id`, `path`, `tags`, `meta`.

- [ ] **Database Orchestrator:**
  - [ ] `DatabaseManager`: Управление подключениями.
  - [ ] `PluginDatabaseContext`: Scoped Access (доступ только к своим таблицам + core read-only).
  - [ ] Автоматическое префиксирование имен таблиц (`plugin_{id}_`).

- [ ] **Migration Engine:**
  - [ ] Проверка версий схем плагинов при старте.
  - [ ] Базовый механизм миграций.

- [ ] **Search Orchestrator:**
  - [ ] Реализация гибридного поиска (Векторный + Текстовый).
  - [ ] Интеграция **Polars** для объединения результатов (Join).
  - [ ] Алгоритм **Reciprocal Rank Fusion (RRF)**.

- [ ] **Automated Data Tests:**
  - [ ] Тесты миграции схем LanceDB.
  - [ ] Тесты целостности данных при множественном доступе.

---

## Phase 3: Essential System Plugins & Frontend Loader (Первые Модули)
**Цель:** Оживить систему, добавив базовые функции работы с файлами и интерфейс.

- [ ] **Frontend Core (Svelte):**
  - [ ] Настройка Vite + Svelte + Skeleton UI.
  - [ ] `DesktopView`: Сетка иконок.
  - [ ] `ModuleLoader`: Логика динамического импорта JS-модулей плагинов.

- [ ] **End-to-End (E2E) Testing:**
  - [ ] Playwright тесты: Загрузка страницы, открытие плагина, навигация.
  - [ ] Проверка работы WebSockets в UI.

- [ ] **System Plugin: File Provider:**
  - [ ] Сканирование локальной директории.
  - [ ] Watchdog: Отслеживание изменений файлов в реальном времени.
  - [ ] Запись метаданных в `Core Metadata Table`.

- [ ] **System Plugin: LLM Provider:**
  - [ ] Интеграция с локальной моделью (Ollama/Transformers).
  - [ ] API для генерации эмбеддингов (для других плагинов).

---

## Phase 4: Advanced Modules (Продвинутые Плагины)
**Цель:** Продемонстрировать мощь архитектуры на реальных задачах.

- [ ] **Plugin: Web Parser:**
  - [ ] Своя таблица `plugin_parser_vectors` (спутник).
  - [ ] Taskiq Worker: Скачивание и парсинг страниц.
  - [ ] Генерация векторов через LLM Provider.

- [ ] **Plugin: Deduplicator:**
  - [ ] Своя таблица `plugin_dedup_hashes`.
  - [ ] Алгоритм перцептивного хэширования (для картинок).
  - [ ] Поиск дубликатов через Cross-Table Query.

- [ ] **Performance Testing:**
  - [ ] Бенчмарки LanceDB при 100+ таблицах.
  - [ ] Профилирование памяти Polars при больших Join-ах.

---

## Phase 5: Optimization & UI Polish (Полировка)
**Цель:** Довести систему до состояния Release Candidate.

- [ ] **Notifications:**
  - [ ] Интеграция `desktop-notifier`.
  - [ ] Центр уведомлений в UI.

- [ ] **Health Checks & Monitoring:**
  - [ ] API статуса плагинов (Health Check).
  - [ ] Автоматическое отключение "зависших" модулей.

- [ ] **Performance Tuning:**
  - [ ] Оптимизация Polars запросов.
  - [ ] Кэширование частых поисковых запросов.
  - [ ] Улучшение UX настроек (валидация на лету).
