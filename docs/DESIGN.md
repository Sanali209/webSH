# Design Document: PC Center OS (v13.0)

Этот документ описывает архитектуру **PC Center** — отказоустойчивой, модульной «Web OS» для локальной автоматизации, управления файлами и работы с LLM.

> **Революция Архитектуры (v13.0):** Реализация **"Security Audit & Consent" (Аудит и Согласие)**. Механизм автоматического анализа манифестов, категоризации рисков и интерактивного подтверждения пользователем.

---

## 1. Философия: Доверие и Контроль

Вместо жесткой песочницы используется декларативная безопасность. Плагин «признается» в намерениях через манифест, а пользователь их одобряет.
*   **Автоматический Аудит:** При установке плагин анализируется на наличие опасных разрешений.
*   **Управление Согласием:** Пользователь видит понятный отчет о рисках перед активацией.
*   **runtime-проверка:** Ядро блокирует любые действия плагина, пока он не перейдет в статус `ACTIVE`.

---

## 2. Процесс Установки (Installation Flow)

Когда плагин появляется в системе, он не активен сразу.

1.  **Сканирование:** Ядро читает `manifest.json`.
2.  **Статус PENDING_AUDIT:** Плагин загружен, но его сигналы блокируются Switchboard.
3.  **Генерация Отчета:** Сервис `SecurityAuditor` сопоставляет права с уровнями риска.
4.  **Вердикт Пользователя:** В Шелле появляется окно аудита. Только после нажатия "Принять" плагин становится `ACTIVE`.

---

## 3. Категоризация Рисков (Risk Levels)

| Уровень | Цвет | Домены (Примеры) | Действие системы |
|---|---|---|---|
| **Low** | 🟢 | `ui.slot.*`, `theme.change` | Разрешено автоматически. |
| **Medium** | 🟡 | `storage.read`, `ai.summarize` | Упоминается в отчете. |
| **High** | 🟠 | `network.request`, `storage.write` | Требует явного "Ок" при установке. |
| **Critical** | 🔴 | `os.execute`, `storage.delete` | Требует повторного подтверждения. |

---

## 4. Реализация Аудитора (Backend Logic)

Сервис анализирует манифест и возвращает JSON-отчет для UI.

```python
class SecurityAuditor:
    SENSITIVE_DOMAINS = {
        "storage.delete": "Критический: Удаление ваших данных",
        "network.request": "Высокий: Отправка данных на внешние сервера",
        "os.execute": "Критический: Запуск системных команд",
    }

    def generate_report(self, manifest: dict) -> dict:
        permissions = manifest.get("permissions", [])
        report = {"plugin_id": manifest["id"], "risks": [], "is_safe": True}

        for perm in permissions:
            if perm in self.SENSITIVE_DOMAINS:
                risk_level = "high" if "delete" in perm or "network" in perm else "critical"
                report["risks"].append({
                    "scope": perm,
                    "description": self.SENSITIVE_DOMAINS[perm],
                    "level": risk_level
                })
                report["is_safe"] = False

        return report
```

---

## 5. Runtime Проверка (Switchboard Barrier)

Диспетчер (Switchboard) при каждом вызове проверяет статус аудита.

```python
async def call(self, caller_id: str, domain: str, params: dict):
    # 1. Проверяем статус аудита (SQLite)
    if not self.config_db.is_plugin_active(caller_id):
        raise PermissionError(f"Plugin {caller_id} is pending audit or disabled.")

    # 2. Проверяем разрешения (Security Barrier)
    if not self.barrier.verify(caller_id, domain):
        raise PermissionError(f"Access to {domain} denied by policy.")

    # 3. Исполняем вызов
    provider = self.registry.find_provider(domain)
    return await provider.execute(params)
```

---

## 6. Интерфейс Аудита (UI Shell)

Шелл отображает пользователю не JSON, а понятные предупреждения:

> **Установка плагина "Web Scraper Pro"**
>
> Этот плагин запрашивает следующие разрешения:
> *   🟢 Доступ к боковой панели (UI)
> *   🟠 Чтение файлов в папке /Downloads (Storage)
> *   🟠 Доступ к сети интернет (Network)
>
> `[ Отмена ]` `[ Подтвердить и запустить ]`

---

## 7. Преимущества Архитектуры

1.  **Доверие:** Пользователь точно знает, какой плагин "лезет" в сеть.
2.  **Безопасность Обновлений:** Если новая версия плагина добавит разрешение `storage.delete`, Ядро снова переведет его в `PENDING_AUDIT`.
3.  **Тонкое Ядро:** Вся логика проверок — это простой match строк по списку правил.
