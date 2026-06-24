"""
Test fitur admin: dashboard, kelola user, referensi, settings.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestAdminDashboard:
    def test_dashboard_redirect_jika_belum_login(self, driver, base_url):
        """Akses /admin/dashboard tanpa login harus redirect ke login."""
        driver.get(f"{base_url}/admin/dashboard")
        assert "/login" in driver.current_url

    def test_dashboard_admin_tampil(self, admin_driver, base_url):
        """Dashboard admin harus berhasil dimuat."""
        driver = admin_driver
        driver.get(f"{base_url}/admin/dashboard")
        assert "403" not in driver.title
        assert "/admin/dashboard" in driver.current_url

    def test_dashboard_menampilkan_statistik(self, admin_driver, base_url):
        """Dashboard admin harus menampilkan statistik sistem."""
        driver = admin_driver
        driver.get(f"{base_url}/admin/dashboard")
        page = driver.page_source.lower()
        assert any(word in page for word in ["mahasiswa", "pengajuan", "staff", "total"])

    def test_mahasiswa_tidak_bisa_akses_admin(self, mahasiswa_driver, base_url):
        """Mahasiswa yang akses halaman admin harus mendapat 403."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/admin/dashboard")
        assert "403" in driver.page_source or "403" in driver.title

    def test_staff_tidak_bisa_akses_admin(self, staff_driver, base_url):
        """Staff yang akses halaman admin harus mendapat 403."""
        driver = staff_driver
        driver.get(f"{base_url}/admin/dashboard")
        assert "403" in driver.page_source or "403" in driver.title


class TestAdminUsers:
    def test_halaman_users_tampil(self, admin_driver, base_url):
        """Halaman kelola user harus dapat diakses oleh admin."""
        driver = admin_driver
        driver.get(f"{base_url}/admin/users")
        assert "403" not in driver.title
        assert "/admin/users" in driver.current_url

    def test_halaman_users_menampilkan_daftar(self, admin_driver, base_url):
        """Halaman users harus menampilkan daftar akun yang ada."""
        driver = admin_driver
        driver.get(f"{base_url}/admin/users")
        page = driver.page_source.lower()
        # Salah satu user seed harus muncul
        assert "budi" in page or "staff" in page or "admin" in page

    def test_mahasiswa_tidak_bisa_akses_users(self, mahasiswa_driver, base_url):
        """Mahasiswa tidak boleh mengakses halaman kelola user."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/admin/users")
        assert "403" in driver.page_source or "403" in driver.title


class TestAdminPengajuan:
    def test_halaman_pengajuan_admin_tampil(self, admin_driver, base_url):
        """Halaman daftar semua pengajuan (admin view) harus dapat diakses."""
        driver = admin_driver
        driver.get(f"{base_url}/admin/pengajuan")
        assert "403" not in driver.title

    def test_mahasiswa_tidak_bisa_akses_pengajuan_admin(self, mahasiswa_driver, base_url):
        """Mahasiswa tidak boleh mengakses halaman pengajuan admin."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/admin/pengajuan")
        assert "403" in driver.page_source or "403" in driver.title


class TestAdminSettings:
    def test_halaman_settings_tampil(self, admin_driver, base_url):
        """Halaman settings sistem harus dapat diakses oleh admin."""
        driver = admin_driver
        driver.get(f"{base_url}/admin/settings")
        assert "403" not in driver.title

    def test_mahasiswa_tidak_bisa_akses_settings(self, mahasiswa_driver, base_url):
        """Mahasiswa tidak boleh mengakses halaman settings."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/admin/settings")
        assert "403" in driver.page_source or "403" in driver.title
