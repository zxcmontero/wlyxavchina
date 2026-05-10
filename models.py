from datetime import UTC, datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


def utc_now():
    return datetime.now(UTC)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    resume = db.relationship("Resume", back_populates="user", uselist=False)
    vacancies = db.relationship(
        "Vacancy",
        back_populates="employer",
        foreign_keys="Vacancy.employer_id",
        lazy=True,
    )
    applications = db.relationship(
        "Application",
        back_populates="applicant",
        foreign_keys="Application.applicant_id",
        lazy=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def is_applicant(self):
        return self.role == "applicant"

    @property
    def is_employer(self):
        return self.role == "employer"

    @property
    def is_admin(self):
        return self.role == "admin"


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    about = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)
    contacts = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = db.relationship("User", back_populates="resume")
    applications = db.relationship("Application", back_populates="resume", lazy=True)

    def __str__(self):
        user_name = self.user.name if self.user else "без пользователя"
        return f"{self.title} - {user_name}"


class Vacancy(db.Model):
    __tablename__ = "vacancies"

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    employer = db.relationship("User", back_populates="vacancies", foreign_keys=[employer_id])
    applications = db.relationship("Application", back_populates="vacancy", lazy=True)

    def __str__(self):
        return f"{self.title} - {self.company_name}"


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("vacancy_id", "applicant_id", name="uq_vacancy_applicant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    vacancy_id = db.Column(db.Integer, db.ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="new", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    vacancy = db.relationship("Vacancy", back_populates="applications")
    applicant = db.relationship("User", back_populates="applications", foreign_keys=[applicant_id])
    resume = db.relationship("Resume", back_populates="applications")

    def __str__(self):
        applicant_name = self.applicant.name if self.applicant else "соискатель"
        vacancy_title = self.vacancy.title if self.vacancy else "вакансия"
        return f"{applicant_name} -> {vacancy_title}"
