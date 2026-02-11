# Task 1.2: Switchboard & Signal Routing

## 1. Вводная часть
Перед началом исполнения: **детально изучить описание Switchboard в `docs/DESIGN_EXTENDED.md` раздел 1**.

## 2. Инструкция по выполнению
1. Реализовать класс `Switchboard` для маршрутизации сигналов.
2. Создать эндпоинт `POST /api/v1/call`, принимающий `CapabilityEnvelope`.
3. Реализовать логику `Audit & Resolve` для сопоставления доменов и провайдеров.
4. Использовать `model_validate_json()` и `TypeAdapter` для высокоскоростной валидации сигналов.

## 3. Спецификация API (Integration Details)
- **Capability Call:** `POST /api/v1/call`
- **Envelope Schema:** `CapabilityEnvelope` (см. `DESIGN.md` раздел 3).
- **Registry Lookup:** Поиск по `domain@version`.

## 4. Зависимости (Dependencies)
- `pydantic`, `fastapi`, `uuid`, `orjson`.

## 5. Принципы кода и архитектуры
- [ ] **Loose Coupling:** Ядро не знает о внутренней логике плагинов.
- [ ] **Schema Guard:** Валидация `params` против схем в Registry через кэшированные `TypeAdapter`.
- [ ] **Performance:** Минимальный оверхед при маршрутизации (использование Hash-карт).
- [ ] **Audit Trail:** Каждый сигнал получает уникальный `correlation_id` при входе.

## 6. Безопасность и Валидация
- Проверка `caller_id` в контексте сигнала.
- Защита от круговых вызовов (Circular Dependencies) через лимит `trace_stack`.

## 7. Самопроверка (Self-Review)
- [ ] `pytest tests/test_switchboard.py` проверяет маршрутизацию к Mock-плагину.
- [ ] Замер скорости: 1000 микро-сигналов в секунду на одном ядре.

## 8. План исполнения
1. [ ] Инициализация Switchboard.
2. [ ] Интеграция с Registry.
3. [ ] Реализация API эндпоинта.

## 9. Цели готовности (Definition of Done)
- [ ] Сигналы успешно доходят до адресатов.
- [ ] Валидация схем работает корректно.
- [ ] Логи трассировки пишутся в консоль.
