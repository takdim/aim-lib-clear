from flask import Blueprint, render_template
from flask_login import current_user

from app.models.bebas_pustaka import BebasPustaka
from app.models.fakultas_setting import FakultasSetting

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/verifikasi/<int:id>')
def verifikasi_surat(id):
    pengajuan = BebasPustaka.query.get_or_404(id)
    if pengajuan.status != 'disetujui' or not pengajuan.nomor_surat:
        return render_template('verifikasi_surat.html', pengajuan=None), 404

    if pengajuan.tipe_pengajuan == 'fakultas':
        penerbit = FakultasSetting.get_for_fakultas(pengajuan.fakultas).nama_perpustakaan
    else:
        penerbit = 'Perpustakaan Universitas Hasanuddin'

    return render_template(
        'verifikasi_surat.html',
        pengajuan=pengajuan,
        penerbit=penerbit,
    )


@main_bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main_bp.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404
