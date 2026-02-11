# Задача 5.1: Dockerfile для Hugging Face (Phase 5)

**Цель:** Подготовить образ, совместимый с Hugging Face Spaces (порт 7860, Python 3.11, Multi-stage build).

## Контекст
*   **Файлы:** `Dockerfile`, `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 5)
*   **Библиотеки:** `node:20-alpine`, `python:3.11-slim`

## Подзадачи

1.  [ ] **Build Stage (Svelte)**
    *   Создать `stage: builder`
        *   `FROM node:20-alpine AS builder`
        *   `WORKDIR /app/shell`
        *   `COPY shell/package.json shell/pnpm-lock.yaml ./`
        *   `RUN npm install -g pnpm && pnpm install --frozen-lockfile`
        *   `COPY shell/ ./`
        *   `RUN pnpm build`
        *   *Output:* `/app/shell/dist`
2.  [ ] **Runtime Stage (FastAPI)**
    *   Создать `stage: runtime`
        *   `FROM python:3.11-slim`
        *   `WORKDIR /app`
        *   `COPY --from=builder /app/shell/dist ./dist`
        *   `COPY requirements.txt ./`
        *   `RUN pip install --no-cache-dir -r requirements.txt`
        *   `COPY core/ ./core`
        *   `COPY plugins/ ./plugins`
        *   `RUN mkdir data` (Persistence)
        *   `useradd -m -u 1000 appuser && chown -R appuser:appuser /app`
        *   `USER appuser`
        *   `ENV PYTHONPATH=/app PORT=7860`
        *   `EXPOSE 7860`
        *   `CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "7860"]`

## Автоматические тесты
*   **Local Build:** `docker build -t hf-space .`
*   **Local Run:** `docker run -p 7860:7860 hf-space`
*   **Curl Test:** `curl http://localhost:7860/health` -> 200 OK

## Пункты самопроверки
*   [ ] Образ меньше 500MB (slim python, multi-stage).
*   [ ] Приложение запускается на порту 7860.
*   [ ] Пользователь не root (безопасность HF).

## Критерии выполнения (Definition of Done)
1.  Dockerfile готов и протестирован локально.
2.  Образ собирается и запускается без ошибок.
3.  Размер образа оптимизирован.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
