"""
Test fitur staff: dashboard, daftar pengajuan, detail & aksi pengajuan.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestStaffDashboard:
    def test_dashboard_redirect_jika_belum_login(self, driver, base_url):
        """Akses /staff/dashboard tanpa login harus redirect ke login."""
        driver.get(f"{base_url}/staff/dashboard")
        assert "/login" in driver.current_url

    def test_dashboard_staff_tampil(self, staff_driver, base_url):
        """Dashboard staff harus berhasil dimuat."""
        driver = staff_driver
        driver.get(f"{base_url}/staff/dashboard")
        assert "403" not in driver.title
        assert "/staff/dashboard" in driver.current_url

    def test_dashboard_menampilkan_statistik(self, staff_driver, base_url):
        """Dashboard staff harus menampilkan statistik pengajuan."""
        driver = staff_driver
        driver.get(f"{base_url}/staff/dashboard")
        page = driver.page_source.lower()
        # Salah satu kata statistik harus muncul
        assert any(word in page for word in ["masuk", "menunggu", "disetujui", "ditolak"])

    def test_mahasiswa_tidak_bisa_akses_staff_dashboard(self, mahasiswa_driver, base_url):
        """Mahasiswa yang akses halaman staff harus mendapat 403."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/staff/dashboard")
        assert "403" in driver.page_source or "403" in driver.title


class TestStaffPengajuanList:
    def test_halaman_list_pengajuan_tampil(self, staff_driver, base_url):
        """Halaman daftar pengajuan harus dapat diakses."""
        driver = staff_driver
        driver.get(f"{base_url}/staff/pengajuan")
        assert "403" not in driver.title
        assert "/staff/pengajuan" in driver.current_url

    def test_filter_status_menunggu(self, staff_driver, base_url):
        """Filter pengajuan berdasarkan status 'menunggu_review' harus berjalan."""
        driver = staff_driver
        driver.get(f"{base_url}/staff/pengajuan?status=menunggu_review")
        assert "403" not in driver.title
        # Halaman harus tetap bisa diakses
        assert "/staff/pengajuan" in driver.current_url

    def test_filter_pencarian(self, staff_driver, base_url):
        """Pencarian berdasarkan NIM atau nama harus berjalan."""
        driver = staff_driver
        driver.get(f"{base_url}/staff/pengajuan?search=Budi")
        assert "403" not in driver.title
        assert "/staff/pengajuan" in driver.current_url

    def test_mahasiswa_tidak_bisa_akses_list_pengajuan(self, mahasiswa_driver, base_url):
        """Mahasiswa tidak boleh mengakses daftar pengajuan staff."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/staff/pengajuan")
        assert "403" in driver.page_source or "403" in driver.title


class TestAdminBisaAksesStaff:
    def test_admin_bisa_akses_staff_dashboard(self, admin_driver, base_url):
        """Admin juga harus bisa mengakses dashboard staff."""
        driver = admin_driver
        driver.get(f"{base_url}/staff/dashboard")
        assert "403" not in driver.title
        assert "/staff/dashboard" in driver.current_url

    def test_admin_bisa_akses_list_pengajuan(self, admin_driver, base_url):
        """Admin harus bisa mengakses daftar pengajuan staff."""
        driver = admin_driver
        driver.get(f"{base_url}/staff/pengajuan")
        assert "403" not in driver.title
