import re

from models import Application, Resume, User, Vacancy, db


def login(client, email, password, follow_redirects=True):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=follow_redirects,
    )


def logout(client, follow_redirects=True):
    return client.get("/logout", follow_redirects=follow_redirects)


def test_public_pages_are_available(client):
    for route in ["/", "/about", "/contacts", "/vacancies"]:
        response = client.get(route)
        assert response.status_code == 200


def test_public_pages_render_updated_key_content(client):
    expectations = {
        "/": ["Работа и подбор персонала без скучной бюрократии", "Свежие вакансии"],
        "/about": ["Кадровое агентство без лишней сложности", "Основные сценарии покрыты от входа до отклика"],
        "/contacts": ["Связаться без лишних кругов", "Подготовьте вопрос в одном сообщении"],
        "/vacancies": ["Вакансии, на которые можно откликнуться уже сейчас", "Найдено:"],
    }

    for route, snippets in expectations.items():
        response = client.get(route)
        html = response.get_data(as_text=True)

        assert response.status_code == 200
        for snippet in snippets:
            assert snippet in html


def test_base_layout_renders_accessible_navigation_fallback(client):
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Перейти к содержимому" in html
    assert "data-nav-toggle" in html
    assert "Навигация без JS" in html


def test_register_creates_user_with_selected_role(client, app_instance):
    response = client.post(
        "/register",
        data={
            "name": "Новый пользователь",
            "email": "new-user@example.com",
            "role": "applicant",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert "Регистрация прошла успешно" in response.get_data(as_text=True)

    with app_instance.app_context():
        user = User.query.filter_by(email="new-user@example.com").first()
        assert user is not None
        assert user.role == "applicant"
        assert user.password_hash != "password123"


def test_applicant_can_create_resume_and_apply_only_once(client, app_instance):
    login_response = login(client, "applicant@example.com", "applicant123")
    assert "Вы успешно вошли в систему" in login_response.get_data(as_text=True)

    resume_response = client.post(
        "/resume/create",
        data={
            "title": "Помощник менеджера",
            "about": "Ответственный кандидат, готов учиться и развиваться.",
            "skills": "Коммуникация, Word, Excel",
            "experience": "Учебная практика в кадровом отделе.",
            "contacts": "Телефон: +7 900 111 22 33",
        },
        follow_redirects=True,
    )
    assert "Резюме успешно создано" in resume_response.get_data(as_text=True)

    with app_instance.app_context():
        vacancy = Vacancy.query.filter_by(title="Менеджер по подбору персонала").first()
        assert vacancy is not None
        vacancy_id = vacancy.id

    first_application = client.post(
        f"/vacancies/{vacancy_id}/apply",
        data={"cover_letter": "Готов пройти собеседование."},
        follow_redirects=True,
    )
    assert "Отклик успешно отправлен" in first_application.get_data(as_text=True)

    second_application = client.post(
        f"/vacancies/{vacancy_id}/apply",
        data={"cover_letter": "Повторный отклик."},
        follow_redirects=True,
    )
    assert "Вы уже откликались на эту вакансию" in second_application.get_data(as_text=True)

    with app_instance.app_context():
        applicant = User.query.filter_by(email="applicant@example.com").first()
        assert applicant.resume is not None
        assert Resume.query.count() == 1
        assert Application.query.filter_by(applicant_id=applicant.id).count() == 1


def test_application_pages_render_friendly_status_labels(client, app_instance):
    with app_instance.app_context():
        applicant = User.query.filter_by(email="applicant@example.com").first()
        vacancy = Vacancy.query.filter_by(title="Менеджер по подбору персонала").first()

        resume = Resume(
            user_id=applicant.id,
            title="Тестовое резюме",
            about="Проверка отображения статусов в интерфейсе.",
            skills="Коммуникация, подбор, документооборот",
            experience="Учебный и стажёрский опыт в HR.",
            contacts="status-check@example.com",
        )
        db.session.add(resume)
        db.session.commit()

        application = Application(
            vacancy_id=vacancy.id,
            applicant_id=applicant.id,
            resume_id=resume.id,
            cover_letter="Проверяем дружественное отображение статуса.",
            status="review",
        )
        db.session.add(application)
        db.session.commit()
        vacancy_id = vacancy.id

    login(client, "applicant@example.com", "applicant123")
    applicant_response = client.get("/applications/my", follow_redirects=True)
    applicant_html = applicant_response.get_data(as_text=True)

    assert applicant_response.status_code == 200
    assert "На рассмотрении" in applicant_html
    assert re.search(r">\s*review\s*<", applicant_html) is None

    logout(client)
    login(client, "employer@example.com", "employer123")
    employer_response = client.get(f"/employer/vacancies/{vacancy_id}/applications", follow_redirects=True)
    employer_html = employer_response.get_data(as_text=True)

    assert employer_response.status_code == 200
    assert "На рассмотрении" in employer_html
    assert re.search(r">\s*review\s*<", employer_html) is None


def test_role_protection_blocks_wrong_sections(client):
    login(client, "employer@example.com", "employer123")
    employer_forbidden = client.get("/resume/my")
    assert employer_forbidden.status_code == 403

    logout(client)
    login(client, "applicant@example.com", "applicant123")
    applicant_forbidden = client.get("/employer/vacancies")
    assert applicant_forbidden.status_code == 403


def test_employer_can_create_edit_and_delete_own_vacancy(client, app_instance):
    login(client, "employer@example.com", "employer123")

    create_response = client.post(
        "/employer/vacancies/create",
        data={
            "title": "HR-стажер",
            "company_name": "ООО Пример",
            "description": "Помощь в подборе персонала и работе с откликами.",
            "requirements": "Внимательность, интерес к HR, базовые навыки ПК.",
            "salary": "от 35 000 руб.",
            "location": "Казань",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert "Вакансия успешно создана" in create_response.get_data(as_text=True)

    with app_instance.app_context():
        vacancy = Vacancy.query.filter_by(title="HR-стажер").first()
        assert vacancy is not None
        vacancy_id = vacancy.id

    edit_response = client.post(
        f"/employer/vacancies/{vacancy_id}/edit",
        data={
            "title": "HR-стажер (обновлено)",
            "company_name": "ООО Пример",
            "description": "Обновленное описание вакансии.",
            "requirements": "Обновленные требования для кандидата.",
            "salary": "от 40 000 руб.",
            "location": "Казань",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert "Вакансия обновлена" in edit_response.get_data(as_text=True)

    with app_instance.app_context():
        updated_vacancy = db.session.get(Vacancy, vacancy_id)
        assert updated_vacancy.title == "HR-стажер (обновлено)"
        assert updated_vacancy.salary == "от 40 000 руб."

    delete_response = client.post(f"/employer/vacancies/{vacancy_id}/delete", follow_redirects=True)
    assert "Вакансия удалена" in delete_response.get_data(as_text=True)

    with app_instance.app_context():
        assert db.session.get(Vacancy, vacancy_id) is None


def test_admin_panel_requires_admin_role(client):
    anonymous_response = client.get("/admin/panel/", follow_redirects=False)
    assert anonymous_response.status_code == 302
    assert "/login" in anonymous_response.headers["Location"]

    login(client, "applicant@example.com", "applicant123")
    applicant_response = client.get("/admin/panel/", follow_redirects=False)
    assert applicant_response.status_code == 403

    logout(client)
    login(client, "admin@example.com", "admin123")
    admin_response = client.get("/admin/panel/", follow_redirects=True)
    assert admin_response.status_code == 200
    assert "Пользователи" in admin_response.get_data(as_text=True)


def test_admin_dashboard_requires_admin_role_and_renders_entry_page(client):
    anonymous_response = client.get("/admin", follow_redirects=False)
    assert anonymous_response.status_code == 302
    assert "/login" in anonymous_response.headers["Location"]

    login(client, "applicant@example.com", "applicant123")
    applicant_response = client.get("/admin", follow_redirects=False)
    assert applicant_response.status_code == 403

    logout(client)
    login(client, "admin@example.com", "admin123")
    admin_response = client.get("/admin", follow_redirects=True)
    admin_html = admin_response.get_data(as_text=True)

    assert admin_response.status_code == 200
    assert "Панель администратора" in admin_html
    assert "Открыть Flask-Admin" in admin_html
    assert "Контроль доступа" in admin_html


def test_admin_can_create_user_without_exposing_password_hash(client, app_instance):
    login(client, "admin@example.com", "admin123")

    list_response = client.get("/admin/panel/user/")
    list_html = list_response.get_data(as_text=True)
    assert list_response.status_code == 200
    assert "password_hash" not in list_html
    assert re.search(r">\s*Соискатель\s*<", list_html)
    assert re.search(r">\s*applicant\s*<", list_html) is None

    form_response = client.get("/admin/panel/user/new/?url=/admin/panel/user/")
    form_html = form_response.get_data(as_text=True)
    assert form_response.status_code == 200
    assert "password_hash" not in form_html
    assert "Пароль" in form_html

    create_response = client.post(
        "/admin/panel/user/new/?url=/admin/panel/user/",
        data={
            "name": "Новый администратор",
            "email": "new-admin@example.com",
            "role": "admin",
            "password": "admin456",
        },
        follow_redirects=True,
    )
    assert create_response.status_code == 200

    with app_instance.app_context():
        user = User.query.filter_by(email="new-admin@example.com").first()
        assert user is not None
        assert user.is_admin
        assert user.password_hash != "admin456"
        assert user.check_password("admin456")


def test_admin_can_create_related_records(client, app_instance):
    login(client, "admin@example.com", "admin123")

    with app_instance.app_context():
        employer_id = User.query.filter_by(email="employer@example.com").first().id
        applicant_id = User.query.filter_by(email="applicant@example.com").first().id

    vacancy_form = client.get("/admin/panel/vacancy/new/?url=/admin/panel/vacancy/")
    assert vacancy_form.status_code == 200
    assert "Работодатель" in vacancy_form.get_data(as_text=True)

    vacancy_response = client.post(
        "/admin/panel/vacancy/new/?url=/admin/panel/vacancy/",
        data={
            "employer_id": str(employer_id),
            "title": "Вакансия из админки",
            "company_name": "ООО Админ",
            "description": "Описание вакансии, созданной администратором.",
            "requirements": "Требования для вакансии, созданной администратором.",
            "salary": "от 70 000 руб.",
            "location": "Самара",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert vacancy_response.status_code == 200

    resume_form = client.get("/admin/panel/resume/new/?url=/admin/panel/resume/")
    assert resume_form.status_code == 200
    assert "Соискатель" in resume_form.get_data(as_text=True)

    resume_response = client.post(
        "/admin/panel/resume/new/?url=/admin/panel/resume/",
        data={
            "user_id": str(applicant_id),
            "title": "Резюме из админки",
            "about": "Кандидат создан для проверки формы администратора.",
            "skills": "Коммуникация, документы, подбор персонала",
            "experience": "Есть учебная практика в кадровом отделе.",
            "contacts": "Телефон: +7 900 555 44 33",
        },
        follow_redirects=True,
    )
    assert resume_response.status_code == 200

    with app_instance.app_context():
        vacancy = Vacancy.query.filter_by(title="Вакансия из админки").first()
        resume = Resume.query.filter_by(title="Резюме из админки").first()
        assert vacancy is not None
        assert vacancy.employer_id == employer_id
        assert resume is not None
        assert resume.user_id == applicant_id
        vacancy_id = vacancy.id
        resume_id = resume.id

    application_form = client.get("/admin/panel/application/new/?url=/admin/panel/application/")
    assert application_form.status_code == 200
    assert "Вакансия" in application_form.get_data(as_text=True)
    assert "Соискатель" in application_form.get_data(as_text=True)
    assert "Резюме" in application_form.get_data(as_text=True)

    application_response = client.post(
        "/admin/panel/application/new/?url=/admin/panel/application/",
        data={
            "vacancy_id": str(vacancy_id),
            "applicant_id": str(applicant_id),
            "resume_id": str(resume_id),
            "cover_letter": "Отклик создан администратором.",
            "status": "review",
        },
        follow_redirects=True,
    )
    application_html = application_response.get_data(as_text=True)
    assert application_response.status_code == 200
    assert "На рассмотрении" in application_html
    assert re.search(r">\s*review\s*<", application_html) is None

    with app_instance.app_context():
        application = Application.query.filter_by(vacancy_id=vacancy_id, applicant_id=applicant_id).first()
        assert application is not None
        assert application.resume_id == resume_id
        assert application.status == "review"


def test_admin_rejects_application_with_foreign_resume(client, app_instance):
    login(client, "admin@example.com", "admin123")

    with app_instance.app_context():
        employer = User.query.filter_by(email="employer@example.com").first()
        applicant = User.query.filter_by(email="applicant@example.com").first()

        foreign_applicant = User(name="Другой кандидат", email="foreign@example.com", role="applicant")
        foreign_applicant.set_password("foreign123")
        db.session.add(foreign_applicant)
        db.session.commit()

        foreign_resume = Resume(
            user_id=foreign_applicant.id,
            title="Чужое резюме",
            about="Резюме для негативного сценария проверки.",
            skills="Коммуникация, документы",
            experience="Небольшой опыт административной работы.",
            contacts="foreign@example.com",
        )
        vacancy = Vacancy(
            employer_id=employer.id,
            title="Негативная вакансия",
            company_name="ООО Негативный тест",
            description="Вакансия для проверки некорректной связки резюме.",
            requirements="Внимательность и аккуратность.",
            salary="от 30 000 руб.",
            location="Киров",
            is_active=True,
        )
        db.session.add_all([foreign_resume, vacancy])
        db.session.commit()

        foreign_resume_id = foreign_resume.id
        applicant_id = applicant.id
        vacancy_id = vacancy.id

    resumes_response = client.get(f"/admin/panel/api/applicants/{applicant_id}/resumes")
    resumes_payload = resumes_response.get_json()
    assert resumes_response.status_code == 200
    assert all(item["id"] != foreign_resume_id for item in resumes_payload)

    invalid_response = client.post(
        "/admin/panel/application/new/?url=/admin/panel/application/",
        data={
            "vacancy_id": str(vacancy_id),
            "applicant_id": str(applicant_id),
            "resume_id": str(foreign_resume_id),
            "cover_letter": "Пробуем отправить чужое резюме.",
            "status": "new",
        },
        follow_redirects=True,
    )
    invalid_html = invalid_response.get_data(as_text=True)

    assert invalid_response.status_code == 200
    assert "Резюме должно принадлежать выбранному соискателю." in invalid_html

    with app_instance.app_context():
        invalid_application = Application.query.filter_by(vacancy_id=vacancy_id, applicant_id=applicant_id).first()
        assert invalid_application is None