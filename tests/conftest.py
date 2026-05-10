import pytest

from app import create_app
from models import User, Vacancy, db


def build_user(name, email, role, password):
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    return user


@pytest.fixture
def app_instance(tmp_path):
    database_path = tmp_path / "test.db"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "WTF_CSRF_ENABLED": False,
            "INIT_DB": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )

    with test_app.app_context():
        db.create_all()

        admin_user = build_user("Администратор", "admin@example.com", "admin", "admin123")
        employer_user = build_user("Работодатель", "employer@example.com", "employer", "employer123")
        applicant_user = build_user("Соискатель", "applicant@example.com", "applicant", "applicant123")
        db.session.add_all([admin_user, employer_user, applicant_user])
        db.session.commit()

        vacancy = Vacancy(
            employer_id=employer_user.id,
            title="Менеджер по подбору персонала",
            company_name="ООО Пример",
            description="Поиск кандидатов, проведение первичных собеседований и работа с откликами.",
            requirements="Грамотная речь, ответственность, уверенное владение компьютером.",
            salary="от 60 000 руб.",
            location="Москва",
            is_active=True,
        )
        db.session.add(vacancy)
        db.session.commit()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()