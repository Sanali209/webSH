# Задача 5.2: GitHub Action для Деплоя (Phase 5)

**Цель:** Автоматизировать сборку, тестирование и деплой приложения в Hugging Face Spaces.

## Контекст
*   **Файлы:** `.github/workflows/deploy.yml`
*   **Документация:** `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 5)
*   **Библиотеки:** `actions/checkout`, `actions/setup-node`, `docker/build-push-action`, `playwright`

## Подзадачи

1.  [ ] **Настройка Workflow**
    *   Создать `.github/workflows/deploy.yml`.
    *   **Triggers:** `push: branches: [ main ]` и `workflow_dispatch: inputs: { tag: string }`.
    *   **Jobs:** `test`, `build-and-push`.
2.  [ ] **Job 1: Test (Playwright)**
    *   `runs-on: ubuntu-latest`.
    *   `steps:`
        *   `actions/checkout@v4`.
        *   `actions/setup-node@v4` (v20, `cache: pnpm`).
        *   `npm install -g pnpm && pnpm install --frozen-lockfile`.
        *   `npx playwright install --with-deps chromium`.
        *   `pnpm test` (Unit).
        *   `pnpm exec playwright test` (E2E).
        *   *Artifacts:* `playwright-report`.
3.  [ ] **Job 2: Build and Push (Docker)**
    *   `needs: test`.
    *   `runs-on: ubuntu-latest`.
    *   `steps:`
        *   `actions/checkout@v4`.
        *   `docker/setup-buildx-action@v3`.
        *   `docker/login-action@v3` (registry: `hf.co`, username: `${{ secrets.HF_USERNAME }}`, password: `${{ secrets.HF_TOKEN }}`).
        *   `docker/build-push-action@v5`
            *   `context: .`
            *   `push: true`
            *   `tags: hf.co/${{ secrets.HF_USERNAME }}/pc-center:latest`
            *   `cache-from: type=gha`
            *   `cache-to: type=gha,mode=max`

## Автоматические тесты
*   **CI Validation:** Сам запуск Action в ветке должен пройти успешно (зеленый статус).
*   **Manual Trigger:** Проверка работы `workflow_dispatch`.

## Пункты самопроверки
*   [ ] Тесты Playwright проходят в CI.
*   [ ] Docker образ успешно пушится в HF Registry.
*   [ ] Секреты `HF_USERNAME` и `HF_TOKEN` настроены в GitHub Repository Settings.

## Критерии выполнения (Definition of Done)
1.  Workflow файл создан и валиден (YAML lint).
2.  CI запускает тесты и деплой при пуше в main.
3.  Деплой на HF Spaces обновляется автоматически.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
