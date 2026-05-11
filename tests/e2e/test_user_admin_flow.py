import os
import time
import pytest


RUN_E2E = bool(os.getenv("RUN_E2E"))


@pytest.mark.skipif(not RUN_E2E, reason="E2E disabled - set RUN_E2E=1 to enable")
def test_register_and_admin_sees_user(page):
    base = os.getenv("E2E_BASE_URL", "http://127.0.0.1:5000")
    ts = int(time.time())
    user_email = f"e2e.user.{ts}@example.com"
    user_name = "E2E User"

    # Register new applicant
    page.goto(base + "/register")
    page.fill('input[name="name"]', user_name)
    page.fill('input[name="email"]', user_email)
    page.click('input[type="radio"][value="applicant"]')
    page.fill('input[name="password"]', 'E2ePass123')
    page.fill('input[name="confirm_password"]', 'E2ePass123')
    page.click('input[type="submit"]')
    page.wait_for_selector('text=Регистрация прошла успешно', timeout=5000)

    # Login as admin and confirm user exists in admin list
    page.goto(base + "/login")
    page.fill('input[name="email"]', 'admin@example.com')
    page.fill('input[name="password"]', 'admin123')
    page.click('input[type="submit"]')
    page.wait_for_selector('text=Вы успешно вошли', timeout=5000)

    page.goto(base + "/admin/panel/user/")
    page.wait_for_selector('table', timeout=5000)
    assert user_email in page.content()
