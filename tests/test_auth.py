"""
Test autentikasi: login dan register.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.conftest import do_login, CREDENTIALS


class TestLoginPage:
    def test_halaman_login_dapat_diakses(self, driver, base_url):
        """Halaman login harus berhasil dimuat."""
        driver.get(f"{base_url}/login")
        assert "Login" in driver.title or "Masuk" in driver.page_source

    def test_form_login_tampil(self, driver, base_url):
        """Form login harus memiliki field identifier, password, dan tombol submit."""
        driver.get(f"{base_url}/login")
        assert driver.find_element(By.ID, "identifier").is_displayed()
        assert driver.find_element(By.ID, "password").is_displayed()
        assert driver.find_element(By.ID, "btnLogin").is_displayed()

    def test_login_berhasil_mahasiswa(self, driver, base_url):
        """Login dengan kredensial mahasiswa harus redirect ke dashboard mahasiswa."""
        do_login(driver, base_url, "mahasiswa")
        assert "/dashboard" in driver.current_url
        assert "403" not in driver.title

    def test_login_berhasil_staff(self, driver, base_url):
        """Login dengan kredensial staff harus redirect ke dashboard staff."""
        do_login(driver, base_url, "staff")
        assert "/staff/dashboard" in driver.current_url

    def test_login_berhasil_admin(self, driver, base_url):
        """Login dengan kredensial admin harus redirect ke dashboard admin."""
        do_login(driver, base_url, "admin")
        assert "/admin/dashboard" in driver.current_url

    def test_login_password_salah(self, driver, base_url):
        """Login dengan password salah harus menampilkan pesan error."""
        driver.get(f"{base_url}/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifier"))
        )
        driver.find_element(By.ID, "identifier").send_keys(CREDENTIALS["mahasiswa"]["email"])
        driver.find_element(By.ID, "password").send_keys("PasswordSalah999")
        driver.find_element(By.ID, "btnLogin").click()

        # Tunggu halaman reload setelah POST
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        # Harus tetap di halaman login
        assert "/login" in driver.current_url or "login" in driver.current_url.lower()
        assert "salah" in driver.page_source.lower() or "danger" in driver.page_source.lower()

    def test_login_akun_tidak_ditemukan(self, driver, base_url):
        """Login dengan email yang tidak terdaftar harus menampilkan error."""
        driver.get(f"{base_url}/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifier"))
        )
        driver.find_element(By.ID, "identifier").send_keys("tidakada@email.com")
        driver.find_element(By.ID, "password").send_keys("Password123")
        driver.find_element(By.ID, "btnLogin").click()

        assert "/login" in driver.current_url or "login" in driver.current_url.lower()
        assert "salah" in driver.page_source.lower() or "danger" in driver.page_source.lower()

    def test_redirect_jika_sudah_login(self, driver, base_url):
        """User yang sudah login tidak boleh membuka halaman login."""
        do_login(driver, base_url, "mahasiswa")
        driver.get(f"{base_url}/login")
        # Harus di-redirect ke dashboard mahasiswa, bukan tetap di login
        assert "/login" not in driver.current_url
        assert "/mahasiswa/dashboard" in driver.current_url


class TestLogout:
    def test_logout_berhasil(self, mahasiswa_driver, base_url):
        """Setelah logout, akses ke dashboard harus redirect ke login."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/logout")
        WebDriverWait(driver, 10).until(
            lambda d: "/login" in d.current_url
        )
        # Setelah logout, akses dashboard harus diarahkan ke login
        driver.get(f"{base_url}/mahasiswa/dashboard")
        assert "/login" in driver.current_url


class TestRegisterPage:
    def test_halaman_register_dapat_diakses(self, driver, base_url):
        """Halaman register harus dapat diakses."""
        driver.get(f"{base_url}/register")
        assert "Daftar" in driver.page_source or "Register" in driver.page_source

    def test_form_register_tampil(self, driver, base_url):
        """Form register harus memiliki semua field yang diperlukan."""
        driver.get(f"{base_url}/register")
        for field_id in ["nim", "name", "email", "password", "confirm_password", "fakultas_id"]:
            assert driver.find_element(By.ID, field_id).is_displayed(), \
                f"Field '{field_id}' tidak ditemukan"

    def test_register_validasi_password_tidak_cocok(self, driver, base_url):
        """Submit dengan password tidak cocok harus menampilkan error."""
        driver.get(f"{base_url}/register")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nim"))
        )
        driver.find_element(By.ID, "nim").send_keys("2021999999")
        driver.find_element(By.ID, "name").send_keys("Test User")
        driver.find_element(By.ID, "email").send_keys("testuser@email.com")
        driver.find_element(By.ID, "password").send_keys("Password123")
        driver.find_element(By.ID, "confirm_password").send_keys("BedaPassword")

        # Pilih fakultas dan prodi dilewati — hanya cek validasi password
        driver.find_element(By.ID, "btnRegister").click()

        assert "cocok" in driver.page_source.lower() or "danger" in driver.page_source.lower()

    def test_register_validasi_nim_duplikat(self, driver, base_url):
        """Submit dengan NIM yang sudah terdaftar harus menampilkan error."""
        driver.get(f"{base_url}/register")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nim"))
        )
        # NIM mahasiswa seed yang sudah ada
        driver.find_element(By.ID, "nim").send_keys("2021001001")
        driver.find_element(By.ID, "name").send_keys("Duplikat User")
        driver.find_element(By.ID, "email").send_keys("duplikat_baru@email.com")
        driver.find_element(By.ID, "password").send_keys("Password123")
        driver.find_element(By.ID, "confirm_password").send_keys("Password123")
        driver.find_element(By.ID, "btnRegister").click()

        assert "nim" in driver.page_source.lower() and (
            "sudah" in driver.page_source.lower() or "danger" in driver.page_source.lower()
        )

    def test_link_ke_halaman_login(self, driver, base_url):
        """Halaman register harus ada link ke halaman login."""
        driver.get(f"{base_url}/register")
        link = driver.find_element(By.LINK_TEXT, "Masuk di sini")
        assert link is not None
        link.click()
        assert "/login" in driver.current_url
