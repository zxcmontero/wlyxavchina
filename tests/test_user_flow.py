import time

from models import Vacancy


def test_register_login_create_resume_apply(client, app_instance):
    unique = str(int(time.time()))
    email = f"test.user.{unique}@example.com"

    # Register
    rv = client.post(
        "/register",
        data={
            "name": "Test User",
            "email": email,
            "role": "applicant",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert "Регистрация прошла успешно" in rv.get_data(as_text=True) or "Войдите в систему" in rv.get_data(as_text=True)

    # Login
    rv = client.post(
        "/login",
        data={"email": email, "password": "Password1"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert "Вы успешно вошли" in rv.get_data(as_text=True) or "Вы успешно вошли в систему." in rv.get_data(as_text=True)

    # Create resume
    rv = client.post(
        "/resume/create",
        data={
            "title": "QA Specialist",
            "about": "Experienced QA",
            "skills": "testing, communication",
            "experience": "2 years",
            "contacts": "phone: +7",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert "Резюме успешно создано" in rv.get_data(as_text=True)

    # Apply to first vacancy
    with app_instance.app_context():
        vac = Vacancy.query.first()
        assert vac is not None
        vac_id = vac.id

    rv = client.post(f"/vacancies/{vac_id}/apply", data={"cover_letter": "I am interested"}, follow_redirects=True)
    assert rv.status_code == 200
    assert "Отклик успешно отправлен" in rv.get_data(as_text=True)
