"""
Konfigurasi pytest dan fixtures Selenium.

Jalankan test:
    # Lokal (default)
    pytest tests/

    # Server deployed
    pytest tests/ --base-url http://161.118.230.226:8005

    # Tampilkan browser (tidak headless)
    pytest tests/ --no-headless
"""
import os
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

DEFAULT_BASE_URL = "http://127.0.0.1:5000"

# ─── Kredensial dari environment variable (.env) ─────────────────────────────
CREDENTIALS = {
    "admin": {
        "email": os.environ.get("TEST_ADMIN_EMAIL", "admin@perpus.ac.id"),
        "password": os.environ.get("TEST_ADMIN_PASSWORD", ""),
        "dashboard_url": "/admin/dashboard",
    },
    "staff": {
        "email": os.environ.get("TEST_STAFF_EMAIL", "staff@perpus.ac.id"),
        "password": os.environ.get("TEST_STAFF_PASSWORD", ""),
        "dashboard_url": "/staff/dashboard",
    },
    "mahasiswa": {
        "email": os.environ.get("TEST_MAHASISWA_EMAIL", "budi@mahasiswa.ac.id"),
        "password": os.environ.get("TEST_MAHASISWA_PASSWORD", ""),
        "dashboard_url": "/mahasiswa/dashboard",
    },
}


# ─── Opsi command-line ────────────────────────────────────────────────────────
def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default=DEFAULT_BASE_URL,
        help="Base URL aplikasi yang akan ditest (default: http://127.0.0.1:5000)",
    )
    parser.addoption(
        "--no-headless",
        action="store_true",
        default=False,
        help="Jalankan browser dengan tampilan (tidak headless)",
    )


# ─── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url").rstrip("/")


@pytest.fixture(scope="function")
def driver(request):
    """Fixture WebDriver Chrome. Bersih per-test."""
    options = Options()
    if not request.config.getoption("--no-headless"):
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


def do_login(driver, base_url, role):
    """Helper: login ke sistem dengan role tertentu."""
    cred = CREDENTIALS[role]
    driver.get(f"{base_url}/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "identifier"))
    )
    driver.find_element(By.ID, "identifier").send_keys(cred["email"])
    driver.find_element(By.ID, "password").send_keys(cred["password"])
    driver.find_element(By.ID, "btnLogin").click()
    # Tunggu redirect selesai
    WebDriverWait(driver, 10).until(
        lambda d: d.current_url != f"{base_url}/login"
    )
    return driver


@pytest.fixture(scope="function")
def mahasiswa_driver(driver, base_url):
    """Driver yang sudah login sebagai mahasiswa."""
    return do_login(driver, base_url, "mahasiswa")


@pytest.fixture(scope="function")
def staff_driver(driver, base_url):
    """Driver yang sudah login sebagai staff."""
    return do_login(driver, base_url, "staff")


@pytest.fixture(scope="function")
def admin_driver(driver, base_url):
    """Driver yang sudah login sebagai admin."""
    return do_login(driver, base_url, "admin")
