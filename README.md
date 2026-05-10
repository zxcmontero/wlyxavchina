# Кадровое агентство

Учебный веб-проект на Flask для соискателей, работодателей и администратора.

## Запуск проекта

```powershell
Set-Location "c:\Users\Nikita\Desktop\kadr agents"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe seed.py
$env:SECRET_KEY = "replace-with-random-secret"
.\.venv\Scripts\python.exe app.py
```

Сайт открывается по адресу `http://127.0.0.1:5000`.
Для запуска с отладчиком можно временно задать `FLASK_DEBUG=1`.

## Тестовые аккаунты

- admin: `admin@example.com` / `admin123`
- employer: `employer@example.com` / `employer123`
- applicant: `applicant@example.com` / `applicant123`

## Автотесты

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