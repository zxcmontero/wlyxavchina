import os
import uuid
import pytest


# By default these tests are skipped. Set environment variable RUN_E2E=1 to run them.
pytestmark = pytest.mark.skipif(os.getenv("RUN_E2E") != "1", reason="E2E tests disabled by default")


def test_public_pages(page, base_url):
    page.goto(base_url)
    assert "БайкалКадр" in page.title()

    page.goto(f"{base_url}/vacancies")
    # ensure vacancies page loads (look for heading)
    h1 = page.locator("h1").first
    assert h1.text_content() is not None


def test_register_and_login(page, base_url):
    unique = uuid.uuid4().hex[:8]
    name = f"E2E{unique}"
    email = f"e2e.{unique}@example.com"
    password = "StrongPass123"

    # Register
    page.goto(f"{base_url}/register")
    page.fill("input[name='name']", name)
    page.fill("input[name='email']", email)
    # select applicant role
    page.check("input[name='role'][value='applicant']")
    page.fill("input[name='password']", password)
    page.fill("input[name='confirm_password']", password)
    page.click("button[type='submit']")

    # After register, app redirects to login page
    page.wait_for_load_state("networkidle")
    assert page.url.endswith("/login") or "/login" in page.url

    # Login
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")

    # After login, nav should contain 'Выход'
    page.wait_for_load_state("networkidle")
    assert page.locator("text=Выход").count() >= 1
