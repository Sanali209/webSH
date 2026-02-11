# Задача 1.3: Docker и Окружение (Phase 1)

**Цель:** Обеспечить воспроизводимую и переносимую сборку ядра и фронтенда Шелла в Docker-контейнере.

## Контекст
*   **Файлы:** `Dockerfile`, `docker-compose.yml`, `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 1)
*   **Библиотеки:** `python-slim`, `node` (multi-stage)

## Подзадачи

1.  [ ] **Docker: Build Stage (Svelte)**
    *   Создать этап (stage) `ui-builder` в Dockerfile.
    *   Использовать `node:20-alpine`.
    *   Установить зависимости (`pnpm install`).
    *   Собрать статику (`pnpm build`).
    *   Выходная директория: `/app/dist`.
2.  [ ] **Docker: Runtime Stage (FastAPI)**
    *   Создать этап (stage) `runtime` в Dockerfile.
    *   Использовать `python:3.11-slim`.
    *   Скопировать артефакты сборки из `ui-builder` в `/app/dist`.
    *   Установить зависимости (`pip install -r requirements.txt`).
    *   Настроить переменные окружения (ENV).
    *   **Port:** `EXPOSE 7860`.
    *   **CMD:** `uvicorn core.main:app --host 0.0.0.0 --port 7860`.
3.  [ ] **Docker Compose**
    *   Создать `docker-compose.yml` для локальной разработки.
    *   Определить сервис `app` (FastAPI).
    *   Определить сервис `redis` (если нужен).
    *   Смонтировать локальную папку `plugins` в контейнер.
4.  [ ] **Security Best Practices**
    *   Не запускать от root (создать пользователя `appuser`).
    *   Минимизировать количество слоев.
    *   Использовать `.dockerignore` (исключить `__pycache__`, `venv`, `node_modules`).

## Автоматические тесты
*   **CI:** GitHub Action (будет настроен в Phase 5) должен успешно собрать образ.
*   **Local:** `docker build -t pc-center-core .` должен пройти без ошибок.

## Пункты самопроверки
*   [ ] Docker образ собирается (меньше 500MB желательно).
*   [ ] Контейнер запускается и отдает статику по порту 7860.
*   [ ] Контейнер не падает при отсутствии томов.

## Критерии выполнения (Definition of Done)
1.  Образ собирается локально и в CI.
2.  Контейнер запускается и функционален.
3.  Соблюдены практики безопасности Docker.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
