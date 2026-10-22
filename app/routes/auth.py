import bcrypt
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required

from app import db, limiter
from app.models.user import User
from app.models.fakultas import Fakultas
from app.models.program_studi import ProgramStudi
from app.utils.validators import validate_password_strength
from app.utils.security_logger import log_security_event

auth_bp = Blueprint('auth', __name__)

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def is_safe_url(target):
    """Cek apakah URL target aman untuk redirect (mencegah Open Redirect)."""
    if not target or not isinstance(target, str):
        return False
    # Tolak jika ada backslash atau protocol-relative URL (//)
    if '\\' in target or target.startswith('//'):
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_client_ip():
    """
    Dapatkan IP klien yang aman.
    Prioritaskan request.remote_addr (yang diverifikasi oleh ProxyFix jika aktif).
    """
    if request.remote_addr:
        return request.remote_addr
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return 'unknown'


# // ASVS 2.4.1: Anti-automation controls for account registration via centralized rate limiter
@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit('5 per minute; 20 per hour', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('mahasiswa.dashboard'))

    fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()

    if request.method == 'POST':
        honeypot = request.form.get('website', '').strip()
        if honeypot:
            # // ASVS 2.4.1: Honeypot bot protection
            log_security_event('BOT_DETECTED', get_client_ip(), 'Pendaftaran ditolak karena honeypot terisi', status='WARNING')
            flash('Registrasi ditolak: deteksi bot aktif.', 'danger')
            return render_template('auth/register.html', fakultas_list=fakultas_list)

        nim = request.form.get('nim', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        fakultas_id = request.form.get('fakultas_id', type=int)
        prodi_id = request.form.get('prodi_id', type=int)

        errors = []

        if not nim or not nim.replace(' ', '') or not nim.isalnum():
            errors.append('NIM wajib diisi dan hanya boleh berisi huruf dan angka.')
        if len(name) < 3:
            errors.append('Nama lengkap minimal 3 karakter.')
        if not email or '@' not in email:
            errors.append('Email tidak valid.')

        # // ASVS 6.2.1, 6.2.4, 6.2.11: Password strength & breach verification
        pw_errors = validate_password_strength(password, user_context={'nim': nim, 'email': email, 'name': name})
        errors.extend(pw_errors)

        if password != confirm_password:
            errors.append('Konfirmasi password tidak cocok.')
        if not fakultas_id:
            errors.append('Fakultas wajib dipilih.')
        if not prodi_id:
            errors.append('Program Studi wajib dipilih.')

        # Cek duplikasi
        if User.query.filter_by(nim=nim).first():
            errors.append('NIM sudah terdaftar.')
        if User.query.filter_by(email=email).first():
            errors.append('Email sudah terdaftar.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', fakultas_list=fakultas_list)

        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user = User(
            nim=nim,
            name=name,
            email=email,
            password=hashed,
            role='mahasiswa',
            fakultas_id=fakultas_id,
            prodi_id=prodi_id,
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        # // ASVS 8.1.1: Audit log registrasi akun baru
        log_security_event('USER_REGISTER', email, f'Registrasi akun mahasiswa berhasil: {name} ({nim})', target=nim)

        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', fakultas_list=fakultas_list)



def verify_turnstile(token, remote_ip=None):
    """
    Verifikasi token Cloudflare Turnstile ke API Cloudflare.
    Jika TURNSTILE_SECRET_KEY belum disetel atau bernilai placeholder, lewati verifikasi.
    """
    # // ASVS 2.4.1: Lewati verifikasi captcha secara otomatis pada automated test suite
    if current_app.config.get('TESTING'):
        return True

    secret = current_app.config.get('TURNSTILE_SECRET_KEY', '').strip()
    if not secret or secret in ('YOUR_SECRET_KEY', 'your_secret_key', ''):
        # Secret key belum diisi, bypass agar login tetap berfungsi
        return True

    if not token:
        return False

    try:
        import json
        import urllib.parse
        import urllib.request

        url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        payload = {
            'secret': secret,
            'response': token,
        }
        if remote_ip and remote_ip != 'unknown':
            payload['remoteip'] = remote_ip

        data = urllib.parse.urlencode(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'User-Agent': 'SIBESTI-Turnstile/1.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return bool(result.get('success'))
    except Exception as e:
        current_app.logger.error(f"Gagal verifikasi Cloudflare Turnstile: {e}")
        return False


def get_login_rate_limit_key():
    """
    Key untuk pembatasan rate limit login per akun.
    Menggabungkan IP klien + identifier akun (email/NIM) yang dicoba.
    // ASVS 2.4.1: Menjaga agar jika 1 akun salah password, user lain dari IP yang sama tidak terblokir.
    """
    identifier = request.form.get('identifier', '').strip().lower()
    return f"{get_client_ip()}:{identifier}"


@auth_bp.route('/login', methods=['GET', 'POST'])
# Lapis 1 (Per-Akun): Maksimal 5 percobaan per menit untuk akun yang sama
@limiter.limit('5 per minute; 20 per hour', key_func=get_login_rate_limit_key, methods=['POST'])
# Lapis 2 (Global Per-IP): 60 percobaan per menit untuk anti-bot flooding/credential spraying
@limiter.limit('60 per minute; 300 per hour', key_func=get_client_ip, methods=['POST'])
def login():

    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == 'POST':
        turnstile_token = request.form.get('cf-turnstile-response')
        if not verify_turnstile(turnstile_token, get_client_ip()):
            log_security_event('CAPTCHA_FAILED', get_client_ip(), 'Verifikasi Cloudflare Turnstile gagal saat login', status='FAILURE')
            flash('Verifikasi keamanan (Captcha) gagal atau kedaluwarsa. Silakan coba lagi.', 'danger')
            return render_template('auth/login.html')

        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        # Cari user by email atau NIM
        user = User.query.filter(
            (User.email == identifier.lower()) | (User.nim == identifier)
        ).first()

        if not user:
            # // ASVS 8.1.1: Audit log login gagal
            log_security_event('AUTH_LOGIN_FAIL', identifier, 'Percobaan login dengan akun tidak ditemukan', status='FAILURE')
            flash('Email/NIM atau password salah.', 'danger')
            return render_template('auth/login.html')

        # Cek apakah akun aktif
        if not user.is_active:
            log_security_event('AUTH_INACTIVE_ATTEMPT', user.email, 'Percobaan login pada akun yang dinonaktifkan', status='WARNING', target=str(user.id))
            flash('Akun Anda telah dinonaktifkan. Hubungi admin.', 'danger')
            return render_template('auth/login.html')

        # Cek brute-force lock
        if user.is_locked():
            remaining = (user.locked_until - datetime.utcnow()).seconds // 60 + 1
            log_security_event('AUTH_LOCKED_ATTEMPT', user.email, f'Percobaan login saat akun masih terkunci ({remaining} mnt sisa)', status='WARNING', target=str(user.id))
            flash(f'Akun dikunci sementara. Coba lagi dalam {remaining} menit.', 'danger')
            return render_template('auth/login.html')

        # Verifikasi password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            user.login_attempts += 1
            if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
                user.login_attempts = 0
                db.session.commit()
                # // ASVS 2.4.1 & ASVS 8.1.1: Brute-force lockout triggered
                log_security_event('AUTH_LOCKOUT_TRIGGERED', user.email, f'Akun dikunci {LOCKOUT_MINUTES} menit karena melebihi batas percobaan salah', status='WARNING', target=str(user.id))
                flash(f'Terlalu banyak percobaan. Akun dikunci selama {LOCKOUT_MINUTES} menit.', 'danger')
            else:
                db.session.commit()
                sisa = MAX_LOGIN_ATTEMPTS - user.login_attempts
                log_security_event('AUTH_LOGIN_FAIL', user.email, f'Password salah. Percobaan ke-{user.login_attempts}', status='FAILURE', target=str(user.id))
                flash(f'Password salah. Sisa percobaan: {sisa}.', 'danger')
            return render_template('auth/login.html')

        # Reset attempts dan login
        user.login_attempts = 0
        user.locked_until = None
        db.session.commit()

        # // ASVS 3.3.1: Bersihkan session lama untuk mencegah session fixation
        session.clear()
        login_user(user, remember=False)

        # // ASVS 8.1.1: Audit log login berhasil
        log_security_event('AUTH_LOGIN_SUCCESS', user.email, f'User {user.name} ({user.role}) berhasil login', target=str(user.id))
        flash(f'Selamat datang, {user.name}!', 'success')

        next_page = request.args.get('next')
        if next_page and is_safe_url(next_page):
            return redirect(next_page)
        return _redirect_by_role(user)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    user_email = current_user.email if current_user.is_authenticated else 'unknown'
    logout_user()
    session.clear()
    log_security_event('AUTH_LOGOUT', user_email, 'Pengguna berhasil logout')
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/api/prodi-by-fakultas/<int:fakultas_id>')
def prodi_by_fakultas(fakultas_id):
    """AJAX endpoint untuk dropdown prodi dinamis."""
    from flask import jsonify
    prodi_list = ProgramStudi.query.filter_by(fakultas_id=fakultas_id).order_by(ProgramStudi.nama_prodi).all()
    return jsonify([p.to_dict() for p in prodi_list])


def _redirect_by_role(user):
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user.role == 'staff':
        return redirect(url_for('staff.dashboard'))
    else:
        return redirect(url_for('mahasiswa.dashboard'))
