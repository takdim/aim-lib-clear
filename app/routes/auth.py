import bcrypt
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required

from app import db
from app.models.user import User
from app.models.fakultas import Fakultas
from app.models.program_studi import ProgramStudi

auth_bp = Blueprint('auth', __name__)

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('mahasiswa.dashboard'))

    fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()

    if request.method == 'POST':
        nim = request.form.get('nim', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        fakultas_id = request.form.get('fakultas_id', type=int)
        prodi_id = request.form.get('prodi_id', type=int)

        errors = []

        if not nim or not nim.isdigit():
            errors.append('NIM wajib diisi dan hanya boleh berisi angka.')
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

        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', fakultas_list=fakultas_list)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == 'POST':
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
        if next_page:
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
