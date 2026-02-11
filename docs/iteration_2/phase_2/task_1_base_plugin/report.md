# Report Task 2.1: BasePlugin

## Выполненные работы

1.  **Refactoring BasePlugin (`core/sdk.py`)**:
    *   Добавлен класс `BaseSettings` (наследует `BaseModel`) для создания схем настроек.
    *   Добавлены методы `get_settings_model()` и `get_ui_manifest()` в `BasePlugin`.
    *   Реализован метод `export_settings_schema()` для экспорта JSON Schema настроек.
    *   Обновлен хук `sh_plugin_init`: теперь он вызывает `get_ui_manifest()` и регистрирует UI в реестре (`registry.register_ui_extension`).

2.  **Loader Integration (`core/loader.py`)**:
    *   Теперь загрузчик инъектирует `manifest.id` в экземпляр плагина (`plugin_instance.id`) перед регистрацией. Это позволяет плагину знать свой ID при инициализации.

3.  **Tests**:
    *   Созданы модульные тесты в `tests/core/test_base_plugin_refactor.py`.
    *   Проверена генерация схемы настроек.
    *   Проверена регистрация UI через хук инициализации.
    *   Проверены значения по умолчанию.

## Результат
Базовый класс `BasePlugin` теперь поддерживает программное определение UI и настроек, интегрируясь с Pydantic и системой загрузки плагинов.
