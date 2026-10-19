from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, current_app
from flask_login import current_user

from app.models.bebas_pustaka import BebasPustaka
from app.models.fakultas_setting import FakultasSetting

main_bp = Blueprint('main', __name__)

VERIFIKASI_ATTEMPTS = {}
VERIFIKASI_WINDOW = timedelta(minutes=1)
MAX_VERIFIKASI_PER_MINUTE = 20


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


def check_verifikasi_rate_limit():
    ip = get_client_ip()
    now = datetime.utcnow()
    attempts = VERIFIKASI_ATTEMPTS.setdefault(ip, [])
    attempts[:] = [ts for ts in attempts if now - ts < VERIFIKASI_WINDOW]
    if len(attempts) >= MAX_VERIFIKASI_PER_MINUTE:
        return False
    attempts.append(now)
    return True


def mask_name(name):
    if not name:
        return '-'
    parts = name.split()
    masked = []
    for p in parts:
        if len(p) <= 2:
            masked.append(p[0] + '*')
        else:
            masked.append(p[:2] + '*' * (len(p) - 2))
    return ' '.join(masked)


def mask_nim(nim):
    if not nim or len(nim) <= 4:
        return '****'
    return nim[:2] + '*' * (len(nim) - 4) + nim[-2:]


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/verifikasi/<string:code>')
@main_bp.route('/verifikasi/<int:id>')
def verifikasi_surat(code=None, id=None):
    if not check_verifikasi_rate_limit():
        return render_template('verifikasi_surat.html', pengajuan=None, rate_limited=True), 429

    identifier = code if code is not None else str(id)
    pengajuan, is_signed = BebasPustaka.verify_token(identifier)
    if not pengajuan:
        return render_template('verifikasi_surat.html', pengajuan=None), 404

    # Jika verifikasi tanpa signature QR resmi (misal brute-force / scraping ID numerik),
    # data sensitif mahasiswa disamarkan untuk perlindungan privasi.
    display_nama = pengajuan.nama if is_signed else mask_name(pengajuan.nama)
    display_nim = pengajuan.nim if is_signed else mask_nim(pengajuan.nim)

    if pengajuan.tipe_pengajuan == 'fakultas':
        penerbit = FakultasSetting.get_for_fakultas(pengajuan.fakultas).nama_perpustakaan
    else:
        penerbit = current_app.config.get('NAMA_PERPUSTAKAAN', 'UPT Perpustakaan')

    return render_template(
        'verifikasi_surat.html',
        pengajuan=pengajuan,
        display_nama=display_nama,
        display_nim=display_nim,
        is_signed=is_signed,
        penerbit=penerbit,
    )


@main_bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main_bp.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404
