from pathlib import Path

import seed
from app import create_app
from models import Application, Resume, User, Vacancy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_CSS_PATH = PROJECT_ROOT / "static" / "css" / "main.css"


def read_main_css():
    return MAIN_CSS_PATH.read_text(encoding="utf-8")


def extract_css_block(css_text, anchor):
    start = css_text.index(anchor)
    brace_start = css_text.index("{", start)
    depth = 0

    for index in range(brace_start, len(css_text)):
        if css_text[index] == "{":
            depth += 1
        elif css_text[index] == "}":
            depth -= 1
            if depth == 0:
                return css_text[start : index + 1]

    raise AssertionError(f"Не удалось извлечь CSS-блок для {anchor!r}")


def test_main_css_keeps_flash_spacing_and_logo_transition():
    css = read_main_css()

    page_content_block = extract_css_block(css, ".page-content {")
    container_block = extract_css_block(css, ".page-content .container {")
    flash_block = extract_css_block(css, ".flash-list {")
    flash_first_child_block = extract_css_block(css, ".page-content .container > .flash-list:first-child {")
    logo_block = extract_css_block(css, ".logo {")

    assert "padding: var(--section-gap) 0 40px;" in page_content_block
    assert "display: flex;" in container_block
    assert "flex-direction: column;" in container_block
    assert "gap: var(--section-gap);" in container_block
    assert "margin: 0;" in flash_block
    assert "margin-top: 14px;" in flash_first_child_block
    assert "transition:" in logo_block
    assert "transform 0.2s ease" in logo_block
    assert "text-shadow 0.2s ease" in logo_block


def test_main_css_stretches_dashboard_cards_and_preserves_mobile_footer():
    css = read_main_css()

    footer_inner_block = extract_css_block(css, ".footer-inner {")
    footer_children_block = extract_css_block(css, ".footer-inner > * {")
    first_banner_stat_block = extract_css_block(css, ".banner-stat:nth-child(1),")
    second_banner_stat_block = extract_css_block(css, ".banner-stat:nth-child(2),")
    third_banner_stat_block = extract_css_block(css, ".banner-stat:nth-child(3),")
    dashboard_alignment_block = extract_css_block(css, ".applications-dashboard,")
    applications_card_block = extract_css_block(css, ".applications-dashboard .application-card {")
    employer_application_card_block = extract_css_block(css, ".employer-application-card {")
    employer_vacancy_card_block = extract_css_block(css, ".employer-vacancies-list .dashboard-card {")
    tablet_media_block = extract_css_block(css, "@media (max-width: 1024px) {")

    assert "display: grid;" in footer_inner_block
    assert "grid-template-columns: minmax(0, 1fr) auto auto;" in footer_inner_block
    assert "flex:" not in footer_children_block
    assert "background: linear-gradient" in first_banner_stat_block
    assert "background: linear-gradient" in second_banner_stat_block
    assert "background: linear-gradient" in third_banner_stat_block
    assert ".footer-inner > :first-child {" not in css
    assert ".footer-inner > :last-child {" not in css
    assert "align-items: stretch;" in dashboard_alignment_block
    assert "width: 100%;" in applications_card_block
    assert "width: 100%;" in employer_application_card_block
    assert "width: 100%;" in employer_vacancy_card_block
    assert ".footer-inner {" in tablet_media_block
    assert "grid-template-columns: 1fr;" in tablet_media_block


def test_main_css_keeps_gradient_lines_full_width():
    css = read_main_css()

    gradients_block = extract_css_block(css, ".banner-stat::before,")
    feature_hover_block = extract_css_block(css, ".feature-card:hover::before,")
    banner_hover_block = extract_css_block(css, ".banner-stat:hover::before,")
    step_hover_block = extract_css_block(css, ".step-card:hover::before,")

    assert "scaleX(" not in gradients_block
    assert "scaleX(" not in feature_hover_block
    assert "scaleX(" not in banner_hover_block
    assert "scaleX(" not in step_hover_block


def test_seed_data_populates_extended_dataset(tmp_path, monkeypatch):
    database_path = tmp_path / "seed-test.db"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "seed-test-secret",
            "WTF_CSRF_ENABLED": False,
            "INIT_DB": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )

    monkeypatch.setattr(seed, "app", test_app)

    seed.seed_data()

    with test_app.app_context():
        assert User.query.filter_by(role="admin").count() == 1
        assert User.query.filter_by(role="employer").count() >= 3
        assert User.query.filter_by(role="applicant").count() >= 5
        assert Resume.query.count() >= 5
        assert Vacancy.query.count() >= 8
        assert Application.query.count() >= 6
        assert Vacancy.query.filter_by(is_active=False).count() >= 1

        application_statuses = {application.status for application in Application.query.all()}
        assert {"new", "review", "accepted", "rejected"}.issubset(application_statuses)
        assert User.query.filter_by(email="admin@example.com").first() is not None
        assert User.query.filter_by(email="employer@example.com").first() is not None
        assert User.query.filter_by(email="applicant@example.com").first() is not None