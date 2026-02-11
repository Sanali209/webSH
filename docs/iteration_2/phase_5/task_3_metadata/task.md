# Задача 5.3: Метаданные README.md (Phase 5)

**Цель:** Обеспечить правильную конфигурацию Hugging Face Space через метаданные в README.md.

## Контекст
*   **Файлы:** `README.md`, `docs/iteration_2/iteration_plan_and_roadmap.md` (Фаза 5)
*   **Библиотеки:** `huggingface-cli` (опционально)

## Подзадачи

1.  [ ] **Добавление Metadata Header**
    *   В `README.md` (в корне репозитория):
        *   Добавить YAML frontmatter:
        ```yaml
        ---
        title: PC Center v3.0
        emoji: 🖥️
        colorFrom: blue
        colorTo: purple
        sdk: docker
        pinned: false
        ---
        ```
    *   **Важно:** Убедиться, что `sdk: docker` присутствует.
2.  [ ] **Описание проекта**
    *   Обновить README.md, добавив разделы:
        *   **Installation:** `git clone ...`, `pnpm install`, `docker build ...`.
        *   **Usage:** Как запустить локально (`uvicorn` или `docker`).
        *   **Iteration 2 Status:** Ссылка на `docs/iteration_2/roadmap.md`.

## Автоматические тесты
*   **HF Validation:** Попытаться создать Space с этим README.md (вручную или через API).
*   **Markdown Lint:** `npm install -g markdownlint-cli && markdownlint README.md`.

## Пункты самопроверки
*   [ ] README.md содержит YAML metadata.
*   [ ] `sdk: docker` указан корректно.
*   [ ] Markdown валиден.

## Критерии выполнения (Definition of Done)
1.  README.md обновлен.
2.  Hugging Face Space распознает Docker SDK.

---
**После выполнения:** Отметьте все пункты, создайте файл `report.md` в этой папке с описанием проделанной работы.
