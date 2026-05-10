from app import app
from models import Application, Resume, User, Vacancy, db


def create_user(name, email, role, password):
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    return user


def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin_user = create_user("Администратор", "admin@example.com", "admin", "admin123")
        employer_user = create_user("ООО Пример", "employer@example.com", "employer", "employer123")
        applicant_user = create_user("Иван Петров", "applicant@example.com", "applicant", "applicant123")

        db.session.add_all([admin_user, employer_user, applicant_user])
        db.session.commit()

        resume = Resume(
            user_id=applicant_user.id,
            title="Помощник менеджера",
            about="Ответственный и внимательный соискатель, готов учиться и развиваться.",
            skills="Работа с документами, MS Office, деловое общение",
            experience="Проходил учебную практику в отделе кадров, помогал с оформлением документов.",
            contacts="Телефон: +7 (900) 111-22-33\nEmail: applicant@example.com",
        )

        vacancy_one = Vacancy(
            employer_id=employer_user.id,
            title="Менеджер по подбору персонала",
            company_name="ООО Пример",
            description="Поиск кандидатов, проведение первичных собеседований и работа с откликами.",
            requirements="Грамотная речь, ответственность, уверенное владение компьютером.",
            salary="от 60 000 руб.",
            location="Москва",
            is_active=True,
        )

        vacancy_two = Vacancy(
            employer_id=employer_user.id,
            title="Офис-менеджер",
            company_name="ООО Пример",
            description="Работа с документами, помощь руководителю и организация офисных процессов.",
            requirements="Организованность, внимательность, умение работать в команде.",
            salary="от 45 000 руб.",
            location="Москва",
            is_active=True,
        )

        db.session.add_all([resume, vacancy_one, vacancy_two])
        db.session.commit()

        application = Application(
            vacancy_id=vacancy_one.id,
            applicant_id=applicant_user.id,
            resume_id=resume.id,
            cover_letter="Здравствуйте. Меня заинтересовала вакансия, готов пройти собеседование.",
            status="new",
        )

        db.session.add(application)
        db.session.commit()

        print("Тестовые данные успешно добавлены.")
        print("admin: admin@example.com / admin123")
        print("employer: employer@example.com / employer123")
        print("applicant: applicant@example.com / applicant123")


if __name__ == "__main__":
    seed_data()