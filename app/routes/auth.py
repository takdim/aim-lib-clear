import bcrypt
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required

REGISTRATION_ATTEMPTS = {}
REGISTRATION_BLOCKED = {}
MAX_REGISTRATION_ATTEMPTS = 5
REGISTRATION_WINDOW = timedelta(minutes=10)
REGISTRATION_BLOCK_DURATION = timedelta(minutes=15)

from app import db, limiter
from app.models.user import User
from app.models.fakultas import Fakultas
from app.models.program_studi import ProgramStudi

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


def check_registration_rate_limit():
    ip = get_client_ip()
    now = datetime.utcnow()

    if REGISTRATION_BLOCKED.get(ip) and REGISTRATION_BLOCKED[ip] > now:
        remaining = int((REGISTRATION_BLOCKED[ip] - now).total_seconds() // 60) + 1
        flash(f'Registrasi dibatasi sementara. Coba lagi dalam {remaining} menit.', 'danger')
        return False

    attempts = REGISTRATION_ATTEMPTS.setdefault(ip, [])
    attempts[:] = [ts for ts in attempts if now - ts < REGISTRATION_WINDOW]

    if len(attempts) >= MAX_REGISTRATION_ATTEMPTS:
        REGISTRATION_BLOCKED[ip] = now + REGISTRATION_BLOCK_DURATION
        flash('Terlalu sering mencoba mendaftar. Silakan tunggu beberapa menit lalu coba lagi.', 'danger')
        return False

    attempts.append(now)
    return True


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('mahasiswa.dashboard'))

    fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()

    if request.method == 'POST':
        honeypot = request.form.get('website', '').strip()
        if honeypot:
            flash('Registrasi ditolak: deteksi bot aktif.', 'danger')
            return render_template('auth/register.html', fakultas_list=fakultas_list)

        if not check_registration_rate_limit():
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
        if len(password) < 8:
            errors.append('Password minimal 8 karakter.')
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

        REGISTRATION_ATTEMPTS.pop(get_client_ip(), None)
        REGISTRATION_BLOCKED.pop(get_client_ip(), None)

        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', fakultas_list=fakultas_list)


def verify_turnstile(token, remote_ip=None):
    """
    Verifikasi token Cloudflare Turnstile ke API Cloudflare.
    Jika TURNSTILE_SECRET_KEY belum disetel atau bernilai placeholder, lewati verifikasi.
    """
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


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute; 30 per hour', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == 'POST':
        turnstile_token = request.form.get('cf-turnstile-response')
        if not verify_turnstile(turnstile_token, get_client_ip()):
            flash('Verifikasi keamanan (Captcha) gagal atau kedaluwarsa. Silakan coba lagi.', 'danger')
            return render_template('auth/login.html')

        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        # Cari user by email atau NIM
        user = User.query.filter(
            (User.email == identifier.lower()) | (User.nim == identifier)
        ).first()

        if not user:
            flash('Email/NIM atau password salah.', 'danger')
            return render_template('auth/login.html')

        # Cek apakah akun aktif
        if not user.is_active:
            flash('Akun Anda telah dinonaktifkan. Hubungi admin.', 'danger')
            return render_template('auth/login.html')

        # Cek brute-force lock
        if user.is_locked():
            remaining = (user.locked_until - datetime.utcnow()).seconds // 60 + 1
            flash(f'Akun dikunci sementara. Coba lagi dalam {remaining} menit.', 'danger')
            return render_template('auth/login.html')

        # Verifikasi password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            user.login_attempts += 1
            if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
                user.login_attempts = 0
                db.session.commit()
                flash(f'Terlalu banyak percobaan. Akun dikunci selama {LOCKOUT_MINUTES} menit.', 'danger')
            else:
                db.session.commit()
                sisa = MAX_LOGIN_ATTEMPTS - user.login_attempts
                flash(f'Password salah. Sisa percobaan: {sisa}.', 'danger')
            return render_template('auth/login.html')

        # Reset attempts dan login
        user.login_attempts = 0
        user.locked_until = None
        db.session.commit()

        login_user(user, remember=False)
        flash(f'Selamat datang, {user.name}!', 'success')

        next_page = request.args.get('next')
        if next_page and is_safe_url(next_page):
            return redirect(next_page)
        return _redirect_by_role(user)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
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
