from datetime import datetime
from functools import wraps
from os import environ
from pathlib import Path
from secrets import token_hex

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.validators import Unique
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import event
from sqlalchemy.engine import Engine
from wtforms import PasswordField, SelectField
from wtforms.validators import Length, Optional, ValidationError

from forms import ApplicationForm, LoginForm, RegisterForm, ResumeForm, VacancyForm
from models import Application, Resume, User, Vacancy, db


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


BASE_DIR = Path(__file__).resolve().parent
ROLE_CHOICES = [
    ("applicant", "Соискатель"),
    ("employer", "Работодатель"),
    ("admin", "Администратор"),
]
ROLE_LABELS = dict(ROLE_CHOICES)
APPLICATION_STATUS_CHOICES = [
    ("new", "Новый"),
    ("review", "На рассмотрении"),
    ("accepted", "Принят"),
    ("rejected", "Отклонён"),
]
APPLICATION_STATUS_LABELS = dict(APPLICATION_STATUS_CHOICES)

# Flask-Admin 1.6 keeps this flag in the WTForms 2.x tuple format.
Unique.field_flags = {"unique": True}

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Сначала войдите в систему"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login", next=request.url))
        abort(403)


class SecureModelView(ModelView):
    can_view_details = True
    page_size = 25

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login", next=request.url))
        abort(403)


class UserAdminView(SecureModelView):
    column_list = ("id", "name", "email", "role", "created_at")
    column_searchable_list = ("name", "email")
    column_filters = ("role", "created_at")
    form_columns = ("name", "email", "role", "password")
    form_choices = {"role": ROLE_CHOICES}
    form_extra_fields = {
        "password": PasswordField("Пароль", validators=[Optional(), Length(min=6, max=64)])
    }
    column_formatters = {
        "role": lambda view, context, model, name: ROLE_LABELS.get(model.role, model.role)
    }
    column_formatters_detail = column_formatters
    column_labels = {
        "id": "ID",
        "name": "Имя",
        "email": "Email",
        "role": "Роль",
        "created_at": "Создан",
    }
    form_args = {
        "name": {"label": "Имя"},
        "email": {"label": "Email"},
        "role": {"label": "Роль"},
    }

    def on_model_change(self, form, model, is_created):
        password = (form.password.data or "").strip()
        if is_created and not password:
            raise ValidationError("Укажите пароль для нового пользователя")
        if password:
            model.set_password(password)
        model.name = model.name.strip()
        model.email = model.email.strip().lower()


class ResumeAdminView(SecureModelView):
    column_list = ("id", "user", "title", "contacts", "created_at", "updated_at")
    column_searchable_list = ("title", "contacts")
    column_filters = ("created_at", "updated_at")
    form_columns = ("user_id", "title", "about", "skills", "experience", "contacts")
    column_labels = {
        "id": "ID",
        "user": "Соискатель",
        "user_id": "Соискатель",
        "title": "Должность",
        "about": "О себе",
        "skills": "Навыки",
        "experience": "Опыт",
        "contacts": "Контакты",
        "created_at": "Создано",
        "updated_at": "Обновлено",
    }
    form_args = {
        "title": {"label": "Должность"},
        "about": {"label": "О себе"},
        "skills": {"label": "Навыки"},
        "experience": {"label": "Опыт"},
        "contacts": {"label": "Контакты"},
    }

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.user_id = SelectField("Соискатель", coerce=int)
        return form_class

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.user_id.choices = [
            (u.id, str(u))
            for u in User.query.filter_by(role="applicant")
            .filter(~User.resume.has())
            .order_by(User.name)
            .all()
        ]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.user_id.choices = [
            (u.id, str(u))
            for u in User.query.filter_by(role="applicant")
            .order_by(User.name)
            .all()
        ]
        if obj is not None:
            form.user_id.data = obj.user_id
        return form

    def on_model_change(self, form, model, is_created):
        model.title = model.title.strip()
        model.about = model.about.strip()
        model.skills = model.skills.strip()
        model.experience = model.experience.strip()
        model.contacts = model.contacts.strip()


class VacancyAdminView(SecureModelView):
    column_list = (
        "id",
        "title",
        "company_name",
        "employer",
        "location",
        "salary",
        "is_active",
        "created_at",
        "updated_at",
    )
    column_searchable_list = ("title", "company_name", "location")
    column_filters = ("is_active", "location", "created_at")
    form_columns = (
        "employer_id",
        "title",
        "company_name",
        "description",
        "requirements",
        "salary",
        "location",
        "is_active",
    )
    column_labels = {
        "id": "ID",
        "title": "Вакансия",
        "company_name": "Компания",
        "employer": "Работодатель",
        "employer_id": "Работодатель",
        "description": "Описание",
        "requirements": "Требования",
        "salary": "Зарплата",
        "location": "Город",
        "is_active": "Активна",
        "created_at": "Создана",
        "updated_at": "Обновлена",
    }
    form_args = {
        "title": {"label": "Вакансия"},
        "company_name": {"label": "Компания"},
        "description": {"label": "Описание"},
        "requirements": {"label": "Требования"},
        "salary": {"label": "Зарплата"},
        "location": {"label": "Город"},
        "is_active": {"label": "Активна"},
    }

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.employer_id = SelectField("Работодатель", coerce=int)
        return form_class

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.employer_id.choices = [
            (u.id, str(u)) for u in User.query.filter_by(role="employer").order_by(User.name).all()
        ]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.employer_id.choices = [
            (u.id, str(u)) for u in User.query.filter_by(role="employer").order_by(User.name).all()
        ]
        if obj is not None:
            form.employer_id.data = obj.employer_id
        return form

    def on_model_change(self, form, model, is_created):
        model.title = model.title.strip()
        model.company_name = model.company_name.strip()
        model.description = model.description.strip()
        model.requirements = model.requirements.strip()
        model.salary = model.salary.strip()
        model.location = model.location.strip()


class ApplicationAdminView(SecureModelView):
    extra_js = ["/static/js/admin_application_form.js"]
    column_list = ("id", "vacancy", "applicant", "resume", "status", "created_at")
    column_filters = ("status", "created_at")
    form_columns = ("vacancy_id", "applicant_id", "resume_id", "cover_letter", "status")
    form_choices = {"status": APPLICATION_STATUS_CHOICES}
    column_formatters = {
        "status": lambda view, context, model, name: APPLICATION_STATUS_LABELS.get(model.status, model.status)
    }
    column_formatters_detail = column_formatters
    column_labels = {
        "id": "ID",
        "vacancy": "Вакансия",
        "applicant": "Соискатель",
        "resume": "Резюме",
        "vacancy_id": "Вакансия",
        "applicant_id": "Соискатель",
        "resume_id": "Резюме",
        "cover_letter": "Письмо",
        "status": "Статус",
        "created_at": "Создан",
    }
    form_args = {
        "cover_letter": {"label": "Сопроводительное письмо"},
        "status": {"label": "Статус"},
    }

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.vacancy_id = SelectField("Вакансия", coerce=int)
        form_class.applicant_id = SelectField("Соискатель", coerce=int)
        form_class.resume_id = SelectField("Резюме", coerce=int)
        return form_class

    def _resume_choices(self, applicant_id=None, current_resume_id=None):
        query = Resume.query.order_by(Resume.title)
        if applicant_id:
            query = query.filter_by(user_id=applicant_id)

        choices = [(resume.id, str(resume)) for resume in query.all()]

        if current_resume_id and current_resume_id not in {resume_id for resume_id, _ in choices}:
            resume = db.session.get(Resume, current_resume_id)
            if resume is not None:
                choices.append((resume.id, str(resume)))

        return choices

    def _populate_choice_fields(self, form, current_resume_id=None):
        form.vacancy_id.choices = [(vacancy.id, str(vacancy)) for vacancy in Vacancy.query.order_by(Vacancy.title).all()]
        form.applicant_id.choices = [
            (user.id, str(user))
            for user in User.query.filter_by(role="applicant").order_by(User.name).all()
        ]

        selected_applicant_id = form.applicant_id.data
        if selected_applicant_id is None and form.applicant_id.choices:
            selected_applicant_id = form.applicant_id.choices[0][0]
            form.applicant_id.data = selected_applicant_id

        selected_resume_id = current_resume_id or form.resume_id.data
        form.resume_id.choices = self._resume_choices(
            applicant_id=selected_applicant_id,
            current_resume_id=selected_resume_id,
        )

        if form.resume_id.data is None and len(form.resume_id.choices) == 1:
            form.resume_id.data = form.resume_id.choices[0][0]

    def create_form(self, obj=None):
        form = super().create_form(obj)
        self._populate_choice_fields(form)
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        if obj is not None:
            form.vacancy_id.data = obj.vacancy_id
            form.applicant_id.data = obj.applicant_id
            form.resume_id.data = obj.resume_id
        self._populate_choice_fields(form, current_resume_id=obj.resume_id if obj is not None else None)
        return form

    def validate_form(self, form):
        is_valid = super().validate_form(form)
        applicant_id = form.applicant_id.data
        resume = db.session.get(Resume, form.resume_id.data) if form.resume_id.data else None

        if resume is None:
            form.resume_id.errors.append("Выберите резюме для отклика.")
            return False

        if applicant_id is None:
            form.applicant_id.errors.append("Выберите соискателя.")
            return False

        if resume.user_id != applicant_id:
            form.resume_id.errors.append("Резюме должно принадлежать выбранному соискателю.")
            return False

        return is_valid

    def on_model_change(self, form, model, is_created):
        model.cover_letter = (model.cover_letter or "").strip()


def add_admin_panel(app):
    admin = Admin(
        app,
        name="Кадровое агентство",
        base_template="admin/custom_base.html",
        template_mode="bootstrap4",
        index_view=SecureAdminIndexView(name="Админка", endpoint="admin_panel", url="/admin/panel"),
    )
    admin.add_view(UserAdminView(User, db.session, name="Пользователи"))
    admin.add_view(ResumeAdminView(Resume, db.session, name="Резюме"))
    admin.add_view(VacancyAdminView(Vacancy, db.session, name="Вакансии"))
    admin.add_view(ApplicationAdminView(Application, db.session, name="Отклики"))
    return admin


def register_routes(app):
    @app.context_processor
    def inject_now():
        def status_label(code):
            return APPLICATION_STATUS_LABELS.get(code, code)

        return {"current_year": datetime.now().year, "status_label": status_label}

    @app.route("/")
    def index():
        latest_vacancies = Vacancy.query.filter_by(is_active=True).order_by(Vacancy.created_at.desc()).limit(6).all()
        return render_template("index.html", vacancies=latest_vacancies)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/contacts")
    def contacts():
        return render_template("contacts.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        form = RegisterForm()
        if form.validate_on_submit():
            user = User(
                name=form.name.data.strip(),
                email=form.email.data.strip().lower(),
                role=form.role.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Регистрация прошла успешно. Теперь войдите в систему.", "success")
            return redirect(url_for("login"))

        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.strip().lower()).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                flash("Вы успешно вошли в систему.", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("index"))

            flash("Неверный email или пароль.", "danger")

        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Вы вышли из системы.", "info")
        return redirect(url_for("index"))

    @app.route("/vacancies")
    def vacancies():
        vacancy_list = Vacancy.query.filter_by(is_active=True).order_by(Vacancy.created_at.desc()).all()
        return render_template("vacancies.html", vacancies=vacancy_list)

    @app.route("/vacancies/<int:vacancy_id>")
    def vacancy_detail(vacancy_id):
        vacancy = db.get_or_404(Vacancy, vacancy_id)
        if not vacancy.is_active:
            can_view_inactive = current_user.is_authenticated and (
                current_user.is_admin or vacancy.employer_id == current_user.id
            )
            if not can_view_inactive:
                abort(404)

        already_applied = False
        application_form = None

        if current_user.is_authenticated and current_user.is_applicant:
            existing_application = Application.query.filter_by(
                vacancy_id=vacancy.id,
                applicant_id=current_user.id,
            ).first()
            already_applied = existing_application is not None
            if current_user.resume and not already_applied:
                application_form = ApplicationForm()

        return render_template(
            "vacancy_detail.html",
            vacancy=vacancy,
            application_form=application_form,
            already_applied=already_applied,
        )

    @app.route("/resume/create", methods=["GET", "POST"])
    @login_required
    @role_required("applicant")
    def create_resume():
        if current_user.resume:
            flash("У вас уже есть резюме. Вы можете его отредактировать.", "info")
            return redirect(url_for("edit_resume"))

        form = ResumeForm()
        if form.validate_on_submit():
            resume = Resume(
                user_id=current_user.id,
                title=form.title.data.strip(),
                about=form.about.data.strip(),
                skills=form.skills.data.strip(),
                experience=form.experience.data.strip(),
                contacts=form.contacts.data.strip(),
            )
            db.session.add(resume)
            db.session.commit()
            flash("Резюме успешно создано.", "success")
            return redirect(url_for("my_resume"))

        return render_template("resume_form.html", form=form, form_title="Создать резюме")

    @app.route("/resume/edit", methods=["GET", "POST"])
    @login_required
    @role_required("applicant")
    def edit_resume():
        resume = Resume.query.filter_by(user_id=current_user.id).first()
        if not resume:
            flash("Сначала создайте резюме.", "warning")
            return redirect(url_for("create_resume"))

        form = ResumeForm(obj=resume)
        if form.validate_on_submit():
            resume.title = form.title.data.strip()
            resume.about = form.about.data.strip()
            resume.skills = form.skills.data.strip()
            resume.experience = form.experience.data.strip()
            resume.contacts = form.contacts.data.strip()
            db.session.commit()
            flash("Резюме обновлено.", "success")
            return redirect(url_for("my_resume"))

        return render_template("resume_form.html", form=form, form_title="Редактировать резюме")

    @app.route("/resume/my")
    @login_required
    @role_required("applicant")
    def my_resume():
        resume = Resume.query.filter_by(user_id=current_user.id).first()
        if not resume:
            flash("У вас пока нет резюме.", "warning")
            return redirect(url_for("create_resume"))
        return render_template("my_resume.html", resume=resume)

    @app.route("/vacancies/<int:vacancy_id>/apply", methods=["POST"])
    @login_required
    @role_required("applicant")
    def apply_to_vacancy(vacancy_id):
        vacancy = Vacancy.query.filter_by(id=vacancy_id, is_active=True).first_or_404()
        if not current_user.resume:
            flash("Перед откликом нужно создать резюме.", "warning")
            return redirect(url_for("create_resume"))

        existing_application = Application.query.filter_by(
            vacancy_id=vacancy.id,
            applicant_id=current_user.id,
        ).first()
        if existing_application:
            flash("Вы уже откликались на эту вакансию.", "info")
            return redirect(url_for("vacancy_detail", vacancy_id=vacancy.id))

        form = ApplicationForm()
        if not form.validate_on_submit():
            flash("Не удалось отправить отклик. Проверьте форму.", "danger")
            return redirect(url_for("vacancy_detail", vacancy_id=vacancy.id))

        application = Application()
        application.vacancy_id = vacancy.id
        application.applicant_id = current_user.id
        application.resume_id = current_user.resume.id
        application.cover_letter = (form.cover_letter.data or "").strip()
        application.status = "new"
        db.session.add(application)
        db.session.commit()
        flash("Отклик успешно отправлен.", "success")
        return redirect(url_for("my_applications"))

    @app.route("/applications/my")
    @login_required
    @role_required("applicant")
    def my_applications():
        applications = (
            Application.query.filter_by(applicant_id=current_user.id)
            .order_by(Application.created_at.desc())
            .all()
        )
        return render_template("my_applications.html", applications=applications)

    @app.route("/employer/vacancies")
    @login_required
    @role_required("employer")
    def employer_vacancies():
        vacancies_list = (
            Vacancy.query.filter_by(employer_id=current_user.id)
            .order_by(Vacancy.created_at.desc())
            .all()
        )
        return render_template("employer_vacancies.html", vacancies=vacancies_list)

    @app.route("/employer/vacancies/create", methods=["GET", "POST"])
    @login_required
    @role_required("employer")
    def create_vacancy():
        form = VacancyForm()
        if form.validate_on_submit():
            vacancy = Vacancy(
                employer_id=current_user.id,
                title=form.title.data.strip(),
                company_name=form.company_name.data.strip(),
                description=form.description.data.strip(),
                requirements=form.requirements.data.strip(),
                salary=form.salary.data.strip(),
                location=form.location.data.strip(),
                is_active=form.is_active.data,
            )
            db.session.add(vacancy)
            db.session.commit()
            flash("Вакансия успешно создана.", "success")
            return redirect(url_for("employer_vacancies"))

        return render_template("vacancy_form.html", form=form, form_title="Создать вакансию")

    @app.route("/employer/vacancies/<int:vacancy_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("employer")
    def edit_vacancy(vacancy_id):
        vacancy = Vacancy.query.filter_by(id=vacancy_id, employer_id=current_user.id).first_or_404()
        form = VacancyForm(obj=vacancy)
        if form.validate_on_submit():
            vacancy.title = form.title.data.strip()
            vacancy.company_name = form.company_name.data.strip()
            vacancy.description = form.description.data.strip()
            vacancy.requirements = form.requirements.data.strip()
            vacancy.salary = form.salary.data.strip()
            vacancy.location = form.location.data.strip()
            vacancy.is_active = form.is_active.data
            db.session.commit()
            flash("Вакансия обновлена.", "success")
            return redirect(url_for("employer_vacancies"))

        return render_template("vacancy_form.html", form=form, form_title="Редактировать вакансию")

    @app.route("/employer/vacancies/<int:vacancy_id>/delete", methods=["POST"])
    @login_required
    @role_required("employer")
    def delete_vacancy(vacancy_id):
        vacancy = Vacancy.query.filter_by(id=vacancy_id, employer_id=current_user.id).first_or_404()
        db.session.delete(vacancy)
        db.session.commit()
        flash("Вакансия удалена.", "info")
        return redirect(url_for("employer_vacancies"))

    @app.route("/employer/vacancies/<int:vacancy_id>/applications")
    @login_required
    @role_required("employer")
    def vacancy_applications(vacancy_id):
        vacancy = Vacancy.query.filter_by(id=vacancy_id, employer_id=current_user.id).first_or_404()
        applications = Application.query.filter_by(vacancy_id=vacancy.id).order_by(Application.created_at.desc()).all()
        return render_template("vacancy_applications.html", vacancy=vacancy, applications=applications)

    @app.route("/admin")
    @login_required
    @role_required("admin")
    def admin_dashboard():
        return render_template("admin.html")

    @app.route("/admin/panel/api/applicants/<int:applicant_id>/resumes")
    @login_required
    @role_required("admin")
    def admin_applicant_resumes(applicant_id):
        applicant = db.get_or_404(User, applicant_id)
        if not applicant.is_applicant:
            return jsonify([])

        resumes = Resume.query.filter_by(user_id=applicant_id).order_by(Resume.title).all()
        return jsonify([
            {"id": resume.id, "label": str(resume)}
            for resume in resumes
        ])

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("error_403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("error_404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("error_500.html"), 500


def create_app(test_config=None):
    default_secret_key = environ.get("SECRET_KEY") or token_hex(32)

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=default_secret_key,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{BASE_DIR / 'instance' / 'site.db'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True,
        INIT_DB=True,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    add_admin_panel(app)
    register_routes(app)

    if app.config.get("INIT_DB", True):
        with app.app_context():
            db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=environ.get("FLASK_DEBUG") == "1")