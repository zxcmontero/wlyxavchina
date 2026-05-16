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
        employer_users = [
            create_user("БайкалТранс Групп", "employer@example.com", "employer", "employer123"),
            create_user("БурятТех", "north@example.com", "employer", "north123"),
            create_user("Агентство БайкалКадр", "bridge@example.com", "employer", "bridge123"),
        ]
        applicant_users = [
            create_user("Иван Петров", "applicant@example.com", "applicant", "applicant123"),
            create_user("Анна Смирнова", "anna.smirnova@example.com", "applicant", "anna1234"),
            create_user("Мария Орлова", "maria.orlova@example.com", "applicant", "maria1234"),
            create_user("Денис Ковалев", "denis.kovalev@example.com", "applicant", "denis1234"),
            create_user("Екатерина Волкова", "ekaterina.volkova@example.com", "applicant", "ekaterina1234"),
        ]

        db.session.add_all([admin_user, *employer_users, *applicant_users])
        db.session.commit()

        resumes = [
            Resume(
                user_id=applicant_users[0].id,
                title="Помощник менеджера",
                about="Ответственный и внимательный соискатель, готов учиться и развиваться.",
                skills="Работа с документами, MS Office, деловое общение",
                experience="Проходил учебную практику в отделе кадров, помогал с оформлением документов.",
                contacts="Телефон: +7 (900) 111-22-33\nEmail: applicant@example.com",
            ),
            Resume(
                user_id=applicant_users[1].id,
                title="HR-ассистент",
                about="Люблю структурировать процессы, быстро вхожу в новые задачи и держу сроки.",
                skills="Подбор персонала, Excel, коммуникация, интервью по скрипту",
                experience="Помогала команде рекрутмента с поиском кандидатов и координацией собеседований.",
                contacts="Телефон: +7 (901) 222-33-44\nEmail: anna.smirnova@example.com",
            ),
            Resume(
                user_id=applicant_users[2].id,
                title="Специалист по документообороту",
                about="Сильная в аккуратной работе с документами и внутренними регламентами.",
                skills="1С, архивирование, деловая переписка, документооборот",
                experience="Два года сопровождала кадровое делопроизводство и внутреннюю отчётность.",
                contacts="Телефон: +7 (902) 333-44-55\nEmail: maria.orlova@example.com",
            ),
            Resume(
                user_id=applicant_users[3].id,
                title="Координатор подбора",
                about="Умею вести несколько вакансий одновременно и поддерживать порядок в воронке найма.",
                skills="ATS, скрининг резюме, телефонные интервью, аналитика",
                experience="Работал координатором в агентстве: вёл воронку кандидатов и взаимодействовал с нанимающими менеджерами.",
                contacts="Телефон: +7 (903) 444-55-66\nEmail: denis.kovalev@example.com",
            ),
            Resume(
                user_id=applicant_users[4].id,
                title="Офис-менеджер",
                about="Люблю, когда в офисе всё работает без сбоев, а у команды есть понятная поддержка.",
                skills="Администрирование офиса, закупки, календарное планирование, сервис",
                experience="Организовывала офисные процессы, координировала поставщиков и помогала руководителю отдела.",
                contacts="Телефон: +7 (904) 555-66-77\nEmail: ekaterina.volkova@example.com",
            ),
        ]

        vacancies = [
            Vacancy(
                employer_id=employer_users[0].id,
                title="Менеджер по подбору персонала",
                company_name="БайкалТранс Групп",
                description="Поиск кандидатов, проведение первичных собеседований и работа с откликами.",
                requirements="Грамотная речь, ответственность, уверенное владение компьютером.",
                salary="от 60 000 руб.",
                location="Улан-Удэ",
                is_active=True,
            ),
            Vacancy(
                employer_id=employer_users[0].id,
                title="Офис-менеджер",
                company_name="БайкалТранс Групп",
                description="Работа с документами, помощь руководителю и организация офисных процессов.",
                requirements="Организованность, внимательность, умение работать в команде.",
                salary="от 45 000 руб.",
                location="Улан-Удэ",
                is_active=True,
            ),
            Vacancy(
                employer_id=employer_users[0].id,
                title="Координатор интервью",
                company_name="БайкалТранс Групп",
                description="Координация интервью, подтверждение слотов, коммуникация с кандидатами и командой.",
                requirements="Внимательность к деталям, хорошая письменная коммуникация, аккуратность.",
                salary="от 55 000 руб.",
                location="Улан-Удэ",
                is_active=True,
            ),
            Vacancy(
                employer_id=employer_users[1].id,
                title="Специалист по кадровому документообороту",
                company_name="БурятТех",
                description="Подготовка и проверка кадровых документов, поддержка внутренних HR-процессов.",
                requirements="Опыт работы с документами, системность, уверенное владение офисными инструментами.",
                salary="от 58 000 руб.",
                location="Улан-Удэ",
                is_active=True,
            ),
            Vacancy(
                employer_id=employer_users[1].id,
                title="Junior Recruiter",
                company_name="БурятТех",
                description="Помощь в закрытии стартовых вакансий, работа с откликами и холодным поиском.",
                requirements="Интерес к HR, проактивность, желание учиться рекрутингу.",
                salary="от 50 000 руб.",
                location="Улан-Удэ",
                is_active=True,
            ),
            Vacancy(
                employer_id=employer_users[1].id,
                title="Onboarding Coordinator",
                company_name="БурятТех",
                description="Сопровождение кандидатов после оффера, помощь в адаптации и подготовке выхода.",
                requirements="Организованность, эмпатия, умение работать по чек-листам.",
                salary="от 57 000 руб.",
                location="Гусиноозёрск",
                is_active=False,
            ),
            Vacancy(
                employer_id=employer_users[2].id,
                title="Ассистент HR-отдела",
                company_name="БайкалКадр",
                description="Поддержка команды подбора, сбор обратной связи и ведение базы кандидатов.",
                requirements="Коммуникабельность, ответственность, базовая аналитика.",
                salary="от 52 000 руб.",
                location="Улан-Удэ",
                is_active=True,
            ),
            Vacancy(
                employer_id=employer_users[2].id,
                title="Координатор клиентской поддержки",
                company_name="БайкалКадр",
                description="Поддержка заказчиков и кандидатов, контроль сроков и статусов по обращениям.",
                requirements="Клиентоориентированность, многозадачность, письменная коммуникация.",
                salary="от 54 000 руб.",
                location="Улан-Удэ",
                is_active=True,
            ),
        ]

        db.session.add_all([*resumes, *vacancies])
        db.session.commit()

        applications = [
            Application(
                vacancy_id=vacancies[0].id,
                applicant_id=applicant_users[0].id,
                resume_id=resumes[0].id,
                cover_letter="Здравствуйте. Меня заинтересовала вакансия, готов пройти собеседование.",
                status="new",
            ),
            Application(
                vacancy_id=vacancies[2].id,
                applicant_id=applicant_users[1].id,
                resume_id=resumes[1].id,
                cover_letter="Умею аккуратно координировать интервью и быстро отвечать кандидатам.",
                status="review",
            ),
            Application(
                vacancy_id=vacancies[3].id,
                applicant_id=applicant_users[2].id,
                resume_id=resumes[2].id,
                cover_letter="Есть опыт работы с кадровыми документами и внутренними регламентами.",
                status="accepted",
            ),
            Application(
                vacancy_id=vacancies[4].id,
                applicant_id=applicant_users[3].id,
                resume_id=resumes[3].id,
                cover_letter="Хочу развиваться в подборе и умею системно работать с воронкой кандидатов.",
                status="new",
            ),
            Application(
                vacancy_id=vacancies[6].id,
                applicant_id=applicant_users[4].id,
                resume_id=resumes[4].id,
                cover_letter="Поддерживаю порядок в процессах и люблю помогать команде в ежедневных задачах.",
                status="review",
            ),
            Application(
                vacancy_id=vacancies[7].id,
                applicant_id=applicant_users[1].id,
                resume_id=resumes[1].id,
                cover_letter="У меня сильные навыки коммуникации и сопровождения пользователей.",
                status="rejected",
            ),
        ]

        db.session.add_all(applications)
        db.session.commit()

        print("Тестовые данные успешно добавлены.")
        print(f"Работодатели: {len(employer_users)}")
        print(f"Соискатели: {len(applicant_users)}")
        print(f"Резюме: {len(resumes)}")
        print(f"Вакансии: {len(vacancies)}")
        print(f"Отклики: {len(applications)}")
        print("admin: admin@example.com / admin123")
        print("employer: employer@example.com / employer123")
        print("applicant: applicant@example.com / applicant123")


if __name__ == "__main__":
    seed_data()