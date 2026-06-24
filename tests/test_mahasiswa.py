"""
Test fitur mahasiswa: dashboard, form pengajuan, status.
"""
import os
import tempfile
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def buat_dummy_pdf(suffix="test"):
    """Buat file PDF minimal untuk keperluan upload test."""
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
        b"xref\n0 4\n0000000000 65535 f\n"
        b"0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n"
        b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF\n"
    )
    tmp = tempfile.NamedTemporaryFile(
        suffix=f"_{suffix}.pdf", delete=False, mode="wb"
    )
    tmp.write(pdf_content)
    tmp.close()
    return tmp.name


class TestMahasiswaDashboard:
    def test_dashboard_redirect_jika_belum_login(self, driver, base_url):
        """Akses /mahasiswa/dashboard tanpa login harus redirect ke login."""
        driver.get(f"{base_url}/mahasiswa/dashboard")
        assert "/login" in driver.current_url

    def test_dashboard_mahasiswa_tampil(self, mahasiswa_driver, base_url):
        """Dashboard mahasiswa harus berhasil dimuat setelah login."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/mahasiswa/dashboard")
        assert "403" not in driver.title
        assert "dashboard" in driver.current_url.lower() or "Dashboard" in driver.page_source

    def test_dashboard_menampilkan_nama_mahasiswa(self, mahasiswa_driver, base_url):
        """Dashboard harus menampilkan nama mahasiswa yang login."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/mahasiswa/dashboard")
        assert "Budi Santoso" in driver.page_source

    def test_staff_tidak_bisa_akses_dashboard_mahasiswa(self, staff_driver, base_url):
        """Staff yang mengakses /mahasiswa/dashboard harus mendapat 403."""
        driver = staff_driver
        driver.get(f"{base_url}/mahasiswa/dashboard")
        assert "403" in driver.page_source or "403" in driver.title


class TestMahasiswaFormPengajuan:
    def test_form_redirect_jika_belum_login(self, driver, base_url):
        """Akses form tanpa login harus redirect ke login."""
        driver.get(f"{base_url}/mahasiswa/form-bebas-pustaka")
        assert "/login" in driver.current_url

    def test_form_pengajuan_tampil(self, mahasiswa_driver, base_url):
        """Halaman form pengajuan harus berhasil dimuat."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/mahasiswa/form-bebas-pustaka")
        # Cek bisa ada redirect ke /status jika sudah punya pengajuan aktif
        if "/form-bebas-pustaka" in driver.current_url:
            assert driver.find_element(By.ID, "alamat").is_displayed()
            assert driver.find_element(By.ID, "file_bebas_pustaka") is not None
            assert driver.find_element(By.ID, "file_kartu_mahasiswa") is not None

    def test_form_validasi_alamat_kosong(self, mahasiswa_driver, base_url):
        """Submit form tanpa alamat harus menampilkan error validasi."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/mahasiswa/form-bebas-pustaka")

        # Skip jika tidak bisa submit (pengajuan aktif sudah ada)
        if "/form-bebas-pustaka" not in driver.current_url:
            pytest.skip("Mahasiswa sudah memiliki pengajuan aktif")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "alamat"))
        )

        # Kosongkan alamat, submit tanpa file
        alamat = driver.find_element(By.ID, "alamat")
        alamat.clear()

        # Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        assert "wajib" in driver.page_source.lower() or "danger" in driver.page_source.lower()

    def test_form_pengajuan_dengan_file_valid(self, mahasiswa_driver, base_url):
        """Submit form dengan data lengkap dan file PDF valid harus berhasil."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/mahasiswa/form-bebas-pustaka")

        if "/form-bebas-pustaka" not in driver.current_url:
            pytest.skip("Mahasiswa sudah memiliki pengajuan aktif")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "alamat"))
        )

        pdf1 = buat_dummy_pdf("bebas_pustaka")
        pdf2 = buat_dummy_pdf("kartu_mahasiswa")

        try:
            driver.find_element(By.ID, "alamat").send_keys(
                "Jl. Perintis Kemerdekaan No. 1, Makassar"
            )
            driver.find_element(By.ID, "file_bebas_pustaka").send_keys(pdf1)
            driver.find_element(By.ID, "file_kartu_mahasiswa").send_keys(pdf2)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            WebDriverWait(driver, 15).until(
                lambda d: "/form-bebas-pustaka" not in d.current_url
                or "success" in d.page_source.lower()
                or "berhasil" in d.page_source.lower()
            )

            assert "berhasil" in driver.page_source.lower() or \
                   "/status" in driver.current_url or \
                   "/dashboard" in driver.current_url
        finally:
            os.unlink(pdf1)
            os.unlink(pdf2)


class TestMahasiswaStatus:
    def test_halaman_status_tampil(self, mahasiswa_driver, base_url):
        """Halaman status pengajuan harus dapat diakses."""
        driver = mahasiswa_driver
        driver.get(f"{base_url}/mahasiswa/status")
        assert "403" not in driver.title
        assert "Status" in driver.page_source or "Pengajuan" in driver.page_source

    def test_status_redirect_jika_belum_login(self, driver, base_url):
        """Akses halaman status tanpa login harus redirect ke login."""
        driver.get(f"{base_url}/mahasiswa/status")
        assert "/login" in driver.current_url
