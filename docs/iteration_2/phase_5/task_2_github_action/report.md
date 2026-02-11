# Отчет о выполнении задачи 5.2: GitHub Action для Деплоя

**Статус:** Выполнено

## Проделанная работа

1.  **Создана структура директорий:**
    *   Создана директория `.github/workflows`.

2.  **Создан Workflow файл `.github/workflows/deploy.yml`:**
    *   Настроен триггер на `push` в ветку `main`.
    *   Настроен ручной запуск `workflow_dispatch` с опциональным параметром `tag`.

3.  **Реализованы Jobs:**
    *   **Test (Playwright):**
        *   Использует `ubuntu-latest`.
        *   Рабочая директория установлена в `./shell`.
        *   Кэширует `pnpm` зависимости (используя `shell/pnpm-lock.yaml`).
        *   Устанавливает зависимости (`pnpm install --frozen-lockfile`) и Playwright (`npx playwright install --with-deps chromium`).
        *   Запускает Unit тесты (`pnpm test`).
        *   Запускает E2E тесты (`pnpm exec playwright test`).
        *   Загружает артефакт `playwright-report` в случае успеха или неудачи.
    *   **Build and Push (Docker):**
        *   Зависит от успешного выполнения job `test`.
        *   Использует `docker/setup-buildx-action` и `docker/login-action` (для HF Registry).
        *   Собирает и пушит Docker образ в `hf.co/${{ secrets.HF_USERNAME }}/pc-center:latest`.
        *   Использует кэширование GitHub Actions (`type=gha`) для ускорения сборки.

## Результат
GitHub Action настроен и готов к использованию после пуша изменений в репозиторий. Для работы требуются настроенные секреты `HF_USERNAME` и `HF_TOKEN` в настройках репозитория.
