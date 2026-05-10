from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, RadioField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from models import User


class RegisterForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    role = RadioField(
        "Роль",
        choices=[("applicant", "Соискатель"), ("employer", "Работодатель")],
        validators=[DataRequired()],
    )
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6, max=64)])
    confirm_password = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password", message="Пароли должны совпадать")],
    )
    submit = SubmitField("Зарегистрироваться")

    def validate_email(self, field):
        existing_user = User.query.filter_by(email=field.data.lower()).first()
        if existing_user:
            raise ValidationError("Пользователь с таким email уже существует")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class ResumeForm(FlaskForm):
    title = StringField("Желаемая должность", validators=[DataRequired(), Length(min=2, max=150)])
    about = TextAreaField("О себе", validators=[DataRequired(), Length(min=10, max=2000)])
    skills = TextAreaField("Навыки", validators=[DataRequired(), Length(min=5, max=2000)])
    experience = TextAreaField("Опыт работы", validators=[DataRequired(), Length(min=5, max=3000)])
    contacts = TextAreaField("Контакты", validators=[DataRequired(), Length(min=5, max=1000)])
    submit = SubmitField("Сохранить резюме")


class VacancyForm(FlaskForm):
    title = StringField("Название вакансии", validators=[DataRequired(), Length(min=2, max=150)])
    company_name = StringField("Название компании", validators=[DataRequired(), Length(min=2, max=150)])
    description = TextAreaField("Описание", validators=[DataRequired(), Length(min=10, max=5000)])
    requirements = TextAreaField("Требования", validators=[DataRequired(), Length(min=10, max=3000)])
    salary = StringField("Зарплата", validators=[DataRequired(), Length(min=2, max=100)])
    location = StringField("Город", validators=[DataRequired(), Length(min=2, max=100)])
    is_active = BooleanField("Вакансия активна", default=True)
    submit = SubmitField("Сохранить вакансию")


class ApplicationForm(FlaskForm):
    cover_letter = TextAreaField("Сопроводительное письмо", validators=[Length(max=1500)])
    submit = SubmitField("Откликнуться")
