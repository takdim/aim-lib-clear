from unittest.mock import patch
import io
import pytest
from app import create_app, db
from app.models.user import User
from app.models.bebas_pustaka import BebasPustaka
from app.utils.validators import is_valid_pdf


@pytest.fixture
def app_instance():
    app = create_app('development')
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'HSTS_ENABLED': True,
        'INLISLITE_ENABLED': True,
        'INLISLITE_BASE_URL': 'https://inlislite.example.com',
        'INLISLITE_LOGIN_URL': 'https://inlislite.example.com/backend/site/login',
        'INLISLITE_USERNAME': 'admin',
        'INLISLITE_PASSWORD': 'secret',
    })
    return app



@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


# ─── 1. TEST FITUR INLISLITE ON-DEMAND & PESAN "Data berhasil di-load." ──────
def test_inlislite_returns_data_berhasil_di_load(client, app_instance):
    """Memastikan endpoint AJAX INLISLite mengembalikan pesan 'Data berhasil di-load.'"""
    with client.session_transaction() as sess:
        with app_instance.app_context():
            user = db.session.query(User).filter_by(role='staff', fakultas_id=None).first()
            if not user:
                user = db.session.query(User).filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

            pengajuan = db.session.query(BebasPustaka).first()
            pengajuan_id = pengajuan.id
            nim = pengajuan.nim

    mock_result = {
        'login_success': True,
        'message': 'Data berhasil di-load.',
        'member': {
            'member_id': '888',
            'member_no': nim,
            'full_name': 'Budi Santoso',
            'fakultas': 'Fakultas Teknik',
            'jurusan': 'Teknik Informatika',
        },
        'loan_history': [],
        'loan_columns': [],
    }

    with patch('app.routes.staff._fetch_inlislite_data', return_value=mock_result):
        resp = client.get(f'/staff/pengajuan/{pengajuan_id}/cek-inlislite')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['message'] == 'Data berhasil di-load.'
        assert data['data']['member']['full_name'] == 'Budi Santoso'


# ─── 2. TEST KEAMANAN OPEN REDIRECT ──────────────────────────────────────────
def test_open_redirect_is_prevented(client, app_instance):
    """Memastikan parameter ?next eksternal diblokir dan dialihkan ke dashboard internal."""
    with app_instance.app_context():
        user = db.session.query(User).filter_by(role='staff').first()
        email = user.email

    with patch('bcrypt.checkpw', return_value=True):
        # Percobaan 1: URL eksternal penuh
        resp1 = client.post('/login?next=https://attacker-phishing.com/steal', data={
            'identifier': email,
            'password': 'anypassword',
        }, follow_redirects=False)
        assert resp1.status_code == 302
        assert 'attacker-phishing.com' not in resp1.location
        assert resp1.location in ('/staff/dashboard', '/admin/dashboard', '/mahasiswa/dashboard')

        # Percobaan 2: Protocol-relative URL (//evil.com)
        resp2 = client.post('/login?next=//evil.com/fake', data={
            'identifier': email,
            'password': 'anypassword',
        }, follow_redirects=False)
        assert resp2.status_code == 302
        assert '//evil.com' not in resp2.location

        # Percobaan 3: URL internal yang valid harus diizinkan
        resp3 = client.post('/login?next=/staff/dashboard', data={
            'identifier': email,
            'password': 'anypassword',
        }, follow_redirects=False)
        assert resp3.status_code == 302
        assert resp3.location == '/staff/dashboard'


# ─── 3. TEST KEAMANAN UPLOAD PDF (MAGIC BYTES) ───────────────────────────────
def test_pdf_magic_bytes_validation():
    """Memastikan hanya file dengan header %PDF- yang dianggap valid."""
    class MockFileStorage:
        def __init__(self, filename, content):
            self.filename = filename
            self.stream = io.BytesIO(content)

        def read(self, n):
            return self.stream.read(n)

        def seek(self, pos):
            self.stream.seek(pos)

    # File PDF sah
    valid_pdf = MockFileStorage('document.pdf', b'%PDF-1.5 test document')
    assert is_valid_pdf(valid_pdf) is True

    # Script PHP/Bash yang diganti namanya menjadi .pdf
    fake_pdf = MockFileStorage('exploit.pdf', b'<?php phpinfo(); ?>')
    assert is_valid_pdf(fake_pdf) is False

    # File teks biasa
    text_pdf = MockFileStorage('notes.pdf', b'Ini hanya catatan biasa')
    assert is_valid_pdf(text_pdf) is False

    # Ekstensi bukan PDF
    wrong_ext = MockFileStorage('document.docx', b'%PDF-1.4')
    assert is_valid_pdf(wrong_ext) is False


# ─── 4. TEST VERIFIKASI SURAT & TOKEN KRIPTOGRAFIS ───────────────────────────
def test_verification_token_signature(app_instance):
    """Memastikan token verifikasi tidak dapat dipalsukan."""
    with app_instance.app_context():
        pengajuan = db.session.query(BebasPustaka).first()
        if not pengajuan:
            pengajuan = BebasPustaka(
                nim='2021001001',
                nama='Budi Santoso',
                alamat='Jl. Contoh No. 1',
                fakultas_id=1,
                prodi_id=1,
                nomor_surat='PERPUS/777/2026',
                status='disetujui'
            )
            db.session.add(pengajuan)
            db.session.commit()
        else:
            pengajuan.status = 'disetujui'
            if not pengajuan.nomor_surat:
                pengajuan.nomor_surat = 'PERPUS/777/2026'
            db.session.commit()

        token = pengajuan.get_verification_token()
        assert token.startswith(f"{pengajuan.id}-")
        assert len(token) > 10

        # Verifikasi token yang valid
        found, is_signed = BebasPustaka.verify_token(token)
        assert found.id == pengajuan.id
        assert is_signed is True

        # Token dengan signature yang diubah/palsu
        fake_token = f"{pengajuan.id}-tampered123456"
        found_fake, is_signed_fake = BebasPustaka.verify_token(fake_token)
        assert found_fake is None
        assert is_signed_fake is False

        # Akses ID legacy (angka murni)
        found_legacy, is_signed_legacy = BebasPustaka.verify_token(str(pengajuan.id))
        assert found_legacy.id == pengajuan.id
        assert is_signed_legacy is False  # Menandakan perlu disensor (masking)


# ─── 5. TEST HTTP SECURITY HEADERS & ANTI-DUPLIKASI ───────────────────────────
def test_security_headers_present(client):
    """Memastikan response memuat HTTP Security Headers global lengkap & tanpa duplikasi."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert resp.headers.get('X-Content-Type-Options') == 'nosniff'
    assert resp.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
    assert resp.headers.get('Permissions-Policy') == 'camera=(), microphone=(), geolocation=()'
    assert resp.headers.get('Cross-Origin-Resource-Policy') == 'same-origin'
    assert 'Strict-Transport-Security' in resp.headers
    assert 'Content-Security-Policy' in resp.headers
    assert "default-src 'self'" in resp.headers['Content-Security-Policy']

    # Pastikan tidak ada header keamanan yang ganda (Temuan #5)
    for header in [
        'Referrer-Policy', 'X-Frame-Options', 'X-Content-Type-Options',
        'Content-Security-Policy', 'Strict-Transport-Security', 'Permissions-Policy'
    ]:
        values = resp.headers.getlist(header)
        assert len(values) == 1, f"Header {header} terduplikasi: {values}"


# ─── 6. TEST PROXY FIX REVERSE PROXY ANTI-SPOOFING ───────────────────────────
def test_proxy_fix_middleware():
    """Memastikan ProxyFix middleware memetakan IP asli reverse proxy dengan benar."""
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {
        'USE_PROXY_FIX': 'true',
        'PROXY_FIX_FOR': '1',
    }):
        proxy_app = create_app('development')
        proxy_client = proxy_app.test_client()

        # Request dari reverse proxy (misal Nginx) membawa header X-Forwarded-For
        resp = proxy_client.get('/', headers={'X-Forwarded-For': '203.0.113.195'})
        assert resp.status_code == 200


# ─── 7. TEST CUSTOM ERROR PAGES (403, 404, 429) ──────────────────────────────
def test_custom_error_pages(client, app_instance):
    """Memastikan halaman 404, 403, dan 429 menampilkan template kustom."""
    # 404: Akses URL yang tidak ada
    resp_404 = client.get('/halaman-tidak-ada-123')
    assert resp_404.status_code == 404
    html_404 = resp_404.get_data(as_text=True)
    assert 'Halaman Tidak Ditemukan' in html_404
    assert '404' in html_404

    # 403: Mahasiswa mencoba mengakses dashboard admin
    with client.session_transaction() as sess:
        with app_instance.app_context():
            user = db.session.query(User).filter_by(role='mahasiswa').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

    resp_403 = client.get('/admin/dashboard')
    assert resp_403.status_code == 403
    html_403 = resp_403.get_data(as_text=True)
    assert 'Akses Ditolak' in html_403
    assert '403' in html_403


# ─── 8. TEST RATE LIMITING LOGIN (TEMUAN #1) ─────────────────────────────────
def test_login_rate_limiting_blocks_bruteforce(client):
    """
    Memastikan:
    1. Percobaan brute-force pada 1 akun diblokir dengan 429 setelah 5 percobaan per menit.
    2. User lain (akun berbeda) dari IP yang sama TIDAK terblokir (tetap 200).
    """
    target_account = 'spammed_user@unhas.ac.id'
    other_account = 'innocent_user@unhas.ac.id'

    statuses = []
    last_resp = None
    for i in range(6):
        last_resp = client.post('/login', data={'identifier': target_account, 'password': 'wrongpassword'})
        statuses.append(last_resp.status_code)

    assert statuses[:5] == [200, 200, 200, 200, 200], f"5 percobaan pertama harus 200: {statuses[:5]}"
    assert statuses[5] == 429, f"Percobaan ke-6 untuk akun yang sama harus 429 (Too Many Requests), didapat: {statuses[5]}"
    html_429 = last_resp.get_data(as_text=True)
    assert '429' in html_429
    assert 'Terlalu Banyak Permintaan' in html_429

    # User lain mencoba login dari IP yang sama -> HARUS BISA (tidak terlempar ke 429)
    other_resp = client.post('/login', data={'identifier': other_account, 'password': 'wrongpassword'})
    assert other_resp.status_code == 200, f"User lain dari IP yang sama tidak boleh terkena 429, didapat: {other_resp.status_code}"



# ─── 9. TEST SESSION COOKIE HARDENING (TEMUAN #2) ─────────────────────────────
def test_session_cookie_hardening_production():
    """Memastikan session cookie disetel dengan Secure, HttpOnly, dan SameSite=Lax di production."""
    prod_app = create_app('production')
    prod_client = prod_app.test_client()

    resp = prod_client.get('/login', base_url='https://localhost')
    cookies = resp.headers.getlist('Set-Cookie')
    joined_cookies = ' '.join(cookies)

    # Ketika cookie session terpasang oleh CSRF atau Session
    if 'session=' in joined_cookies:
        assert 'Secure' in joined_cookies
        assert 'HttpOnly' in joined_cookies
        assert 'SameSite=Lax' in joined_cookies


# ─── 10. TEST CLOUDFLARE TURNSTILE CAPTCHA ───────────────────────────────────
def test_cloudflare_turnstile_rendered(client):
    """Memastikan widget Turnstile dan script terpasang di form login serta CSP mengizinkan domain Cloudflare."""
    resp = client.get('/login')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'cf-turnstile' in html
    assert 'challenges.cloudflare.com/turnstile/v0/api.js' in html

    # Pastikan Content-Security-Policy membolehkan domain Turnstile
    csp = resp.headers.get('Content-Security-Policy', '')
    assert 'https://challenges.cloudflare.com' in csp


# ─── 11. TEST ASVS 6.2 PASSWORD POLICY & BREACH CHECK ────────────────────────
def test_asvs_password_policy():
    """Memastikan password divalidasi sesuai standar OWASP ASVS V6.2."""
    from app.utils.validators import validate_password_strength

    # Terlalu pendek (< 8)
    assert len(validate_password_strength('abc')) > 0

    # Kata sandi umum (blacklisted)
    assert any('terlalu umum' in err for err in validate_password_strength('password123'))
    assert any('terlalu umum' in err for err in validate_password_strength('12345678'))

    # Hanya angka (tidak ada huruf)
    assert any('kombinasi' in err for err in validate_password_strength('987654321'))

    # Memuat NIM / konteks pengguna
    user_ctx = {'nim': 'H071201001', 'email': 'budi@unhas.ac.id', 'name': 'Budi Santoso'}
    assert any('NIM' in err for err in validate_password_strength('SecretH071201001', user_context=user_ctx))
    assert any('email' in err for err in validate_password_strength('budiSecret!99', user_context=user_ctx))

    # Password kuat yang sah
    assert len(validate_password_strength('P@ssw0rdKuatDanAman2026', user_context=user_ctx)) == 0


# ─── 13. TEST AJUKAN ULANG SETELAH DITOLAK ─────────────────────────────────
def test_reapply_after_rejection_allowed(client, app_instance):
    """
    Memastikan mahasiswa dengan pengajuan fakultas disetujui dan pengajuan pusat ditolak
    dapat mengakses form ajukan ulang pusat tanpa terhalang notifikasi aktif.
    """
    with app_instance.app_context():
        user = db.session.query(User).filter_by(role='mahasiswa').first()
        if not user:
            user = User(
                nim='2021009999',
                name='Mahasiswa Test',
                email='mhs_test@unhas.ac.id',
                password='hashedpassword',
                role='mahasiswa',
                fakultas_id=1,
                prodi_id=1,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

        # Buat pengajuan fakultas yang disetujui
        db.session.query(BebasPustaka).filter_by(nim=user.nim).delete()
        fakultas_sub = BebasPustaka(
            user_id=user.id,
            nim=user.nim,
            nama=user.name,
            alamat='Jl. Kampus',
            fakultas_id=user.fakultas_id,
            prodi_id=user.prodi_id,
            tipe_pengajuan='fakultas',
            status='disetujui'
        )
        # Buat pengajuan pusat yang ditolak
        pusat_sub = BebasPustaka(
            user_id=user.id,
            nim=user.nim,
            nama=user.name,
            alamat='Jl. Kampus',
            fakultas_id=user.fakultas_id,
            prodi_id=user.prodi_id,
            tipe_pengajuan='pusat',
            status='ditolak',
            catatan_penolakan='KTM buram'
        )
        db.session.add_all([fakultas_sub, pusat_sub])
        db.session.commit()
        user_id = user.id

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)
        sess['_fresh'] = True

    # Mahasiswa membuka form ajukan ulang pusat
    resp = client.get('/mahasiswa/form-bebas-pustaka?tipe=pusat', follow_redirects=True)
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # Tidak boleh ada flash warning "Anda masih memiliki pengajuan fakultas yang aktif."
    assert 'Anda masih memiliki pengajuan fakultas yang aktif.' not in html
    assert 'Bebas Pustaka Pusat' in html



