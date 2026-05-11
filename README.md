# Кадровое агентство

Сервис по подбору персонала и поддержке офисных/операционных команд. Сайт позволяет работодателям публиковать вакансии и управлять откликами, а соискателям — создавать резюме и откликаться на вакансии.

## Быстрый старт (Windows PowerShell)

```powershell
# Перейти в папку проекта
Set-Location "c:\Users\Nikita\Desktop\kadr agents"

# Создать и активировать виртуальное окружение (если ещё не создано)
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# Установить зависимости
python -m pip install -r requirements.txt

# (опционально) заполнить тестовыми данными
python seed.py

# Установить секрет в переменной окружения
$env:SECRET_KEY = "replace-with-random-secret"

# Запустить приложение (по умолчанию на http://127.0.0.1:5000)
.\\.venv\Scripts\python.exe app.py
```

## Тесты

- Unit / интеграционные тесты: `pytest` (файлы в `tests/`).
- E2E (Playwright): тесты лежат в `tests/e2e/` и по умолчанию пропущены. Чтобы запустить E2E, установите браузеры и экспортируйте `RUN_E2E=1` и `E2E_BASE_URL`.

Пример запуска unit-тестов:

```powershell
.\\.venv\Scripts\python.exe -m pytest -q
```

Пример запуска E2E (локально):

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
.\\.venv\Scripts\python.exe app.py
# $env:RUN_E2E = "1"
# $env:E2E_BASE_URL = "http://127.0.0.1:5000"
.\\.venv\Scripts\python.exe -m pytest -q tests/e2e
```

## Тестовые аккаунты

- admin: `admin@example.com` / `admin123`
- employer: `employer@example.com` / `employer123`
- applicant: `applicant@example.com` / `applicant123`

## Что добавлено

- Unit-тесты для основных сценариев (`tests/`).
- Пример E2E-теста для регистрации и проверки через админ-панель (`tests/e2e/`).
- Обновлён контент публичных страниц и исправлен sticky footer.

## Выполнено

- UI/контент: нейтрализованы упоминания учебного проекта и технологических маркеров; актуализированы публичные страницы: `templates/base.html`, `templates/about.html`, `templates/index.html`, `templates/contacts.html`, `templates/admin.html`.
- Стили: исправлен закреплённый футер в `static/css/main.css` (layout → flex column + footer).
- Тесты: добавлены/обновлены unit- и интеграционные тесты (`tests/`), добавлены интеграционные сценарии `tests/test_user_flow.py` и проверки layout `tests/test_about_and_layout.py`.
- E2E: добавлен пример Playwright-теста `tests/e2e/test_user_admin_flow.py` (по умолчанию пропущен, требует `RUN_E2E=1`).
- Скрипты: создан `scripts/push_to_main.py` для упрощённого безопасного пуша в `main` (push не выполнялся автоматически).
- Документация: обновлены `README.md` и `ROADMAP.md` с актуальным состоянием и инструкциями.
- Ручной QA: частично выполнено — проверены базовые сценарии регистрации, создания резюме, отклика и доступ к админ-панели.
- Результат тестов (локально): `pytest` — 20 passed, 3 skipped.

## Примечания

E2E-тесты требуют установки Playwright-браузеров и запуска приложения перед тестами. В CI рекомендуется включать шаг установки браузеров и экспорт `RUN_E2E=1`.