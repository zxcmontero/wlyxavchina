# Кадровое агентство

Учебный веб-проект на Flask для соискателей, работодателей и администратора.

## Запуск проекта

Ниже приведён удобный набор команд для Windows PowerShell. Перед запуском убедитесь, что у вас установлен Python (рекомендуется 3.8+).

```powershell
# Перейти в папку проекта
Set-Location "c:\Users\Nikita\Desktop\kadr agents"

# Создать и активировать виртуальное окружение (если ещё не создано)
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# Установить зависимости
python -m pip install -r requirements.txt

# Заполнить тестовыми данными (seed.py создаёт тестовые аккаунты)
python seed.py

# Установить секрет в переменной окружения (для PowerShell)
$env:SECRET_KEY = "replace-with-random-secret"

# 1) Быстрый запуск встроенного скрипта (по умолчанию откроется на 127.0.0.1:5000)
.\.venv\Scripts\python.exe app.py

# 2) Альтернатива — использовать "flask run" чтобы указать порт/хост явно
# (нужно экспортировать FLASK_APP, при этом приложение импортирует переменную `app`)
$env:FLASK_APP = "app.py"
$env:FLASK_DEBUG = "1"  # опционально — включает отладочный режим
flask run --port 5001
```

По умолчанию сайт доступен по адресу `http://127.0.0.1:5000` при запуске `app.py`. В ходе тестов/локального прогона иногда используется порт `5001` (см. пример с `flask run --port 5001`).

## Тестовые аккаунты

- admin: `admin@example.com` / `admin123`
- employer: `employer@example.com` / `employer123`
- applicant: `applicant@example.com` / `applicant123`

## Автотесты

Запуск автотестов (в активированном виртуальном окружении):

```powershell
Set-Location "c:\Users\Nikita\Desktop\kadr agents"
.\.venv\Scripts\python.exe -m pytest
```

Покрытие автотестов:

- публичные страницы
- регистрация пользователя
- создание резюме и защита от повторного отклика
- ограничения по ролям
- CRUD вакансий работодателя
- доступ к Flask-Admin только для администратора
- создание пользователей, резюме, вакансий и откликов через Flask-Admin

## E2E (браузерные) тесты

В проект добавлены базовые E2E тесты на Playwright (файлы в `tests/e2e`). По умолчанию они пропущены — чтобы запустить, выполните:

```powershell
# Установите дополнительные зависимости (если ещё не установлены)
python -m pip install -r requirements.txt

# Установите браузерные билды для Playwright
python -m playwright install chromium

# Запустите сервер (пример)
.\.venv\Scripts\python.exe app.py

# В отдельном терминале включите запуск e2e и запустите pytest
$env:RUN_E2E = "1"
$env:E2E_BASE_URL = "http://127.0.0.1:5001"  # при необходимости измените порт
.\.venv\Scripts\python.exe -m pytest -q tests/e2e
```

Примечания:
- Тесты используют фикстуру `page` от `pytest-playwright` и по умолчанию пропускаются (чтобы не мешать локальным unit-тестам).
- Если хотите запускать e2e в CI, включите установку браузеров и экспорт `RUN_E2E=1`.