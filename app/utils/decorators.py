from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def role_required(*roles):
    """Decorator untuk membatasi akses berdasarkan role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Silakan login terlebih dahulu.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            if not current_user.is_active:
                flash('Akun Anda telah dinonaktifkan. Hubungi admin.', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def mahasiswa_required(f):
    return role_required('mahasiswa')(f)


def staff_required(f):
    return role_required('staff', 'admin')(f)


def admin_required(f):
    return role_required('admin')(f)
