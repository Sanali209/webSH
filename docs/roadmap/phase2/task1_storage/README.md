# Task 2.1: System Storage (LanceDB)

## 1. Вводная часть
Перед началом исполнения: **изучить возможности LanceDB и PyArrow, а также роль плагина в `docs/DESIGN.md` раздел 5.1**.

## 2. Инструкция по выполнению
1. Реализовать плагин `system_storage`.
2. Настроить инстанс LanceDB для хранения метаданных сущностей.
3. Реализовать Capability `storage.metadata`, `storage.vector` и `storage.search`.
4. Обеспечить сохранение данных в локальную директорию `.pc_center/data`.

## 3. Спецификация API (Integration Details)
- **Signals:**
    - `storage.metadata.upsert` (ID, data)
    - `storage.vector.search` (query_vector, limit)
    - `storage.search` (query_string)
- **Data Format:** Apache Arrow (через PyArrow).

## 4. Зависимости (Dependencies)
- `lancedb`, `pyarrow`, `polars`, `pandas`.

## 5. Принципы кода и архитектуры
- [ ] **Data Locality:** Индексы LanceDB должны храниться в профиле пользователя.
- [ ] **Schema First:** Каждая таблица имеет строгую Arrow-схему.
- [ ] **Vector Optimization:** Использование IVF-PQ индексов для поиска (если данных много).
- [ ] **Async Wrapper:** Выпуск блокирующих вызовов DB в отдельные потоки через `asyncio.to_thread`.

## 6. Безопасность и Валидация
- Проверка структуры Entity перед записью.
- Защита от переполнения диска при больших объемах векторов.

## 7. Самопроверка (Self-Review)
- [ ] Успешная запись 1000 записей и поиск по ним за < 50мс.
- [ ] Векторный поиск возвращает релевантные ID.

## 8. План исполнения
1. [ ] Инициализация LanceDB.
2. [ ] Реализация CRUD методов.
3. [ ] Настройка векторного индекса.

## 9. Цели готовности (Definition of Done)
- [ ] Система поиска работает.
- [ ] Данные персистентны (сохраняются после рестарта).
- [ ] Плагин корректно сообщает о своих Capability в Registry.
