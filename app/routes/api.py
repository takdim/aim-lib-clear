import io
from flask import Blueprint, jsonify, make_response, abort, current_app, send_file, flash, redirect, url_for, request
from flask_login import login_required, current_user

from app.models.bebas_pustaka import BebasPustaka
from app.utils.pdf_generator import generate_surat_bebas_pustaka

api_bp = Blueprint('api', __name__)


@api_bp.route('/bebas-pustaka/generate-pdf/<int:id>')
@login_required
def generate_pdf(id):
    """Generate PDF Surat Bebas Pustaka."""
    pengajuan = BebasPustaka.query.get_or_404(id)

    # KEAMANAN: Hanya pemilik (mahasiswa ybs) atau Staff/Admin yang boleh cetak
    if current_user.role == 'mahasiswa' and current_user.id != pengajuan.user_id:
        abort(403)

    if pengajuan.status != 'disetujui':
        flash('Surat hanya dapat dicetak jika pengajuan telah disetujui.', 'warning')
        return redirect(url_for('mahasiswa.status'))

    nama_institusi = current_app.config.get('NAMA_INSTITUSI', 'Universitas Contoh')
    nama_perpustakaan = current_app.config.get('NAMA_PERPUSTAKAAN', 'UPT Perpustakaan')

    try:
        pdf_bytes = generate_surat_bebas_pustaka(pengajuan, nama_institusi, nama_perpustakaan)
    except Exception as e:
        current_app.logger.error(f'Gagal generate PDF untuk pengajuan {pengajuan.id}: {e}')
        return jsonify({'error': 'Gagal membuat PDF. Coba lagi nanti.'}), 500

    nim = pengajuan.nim
    filename = f'surat_bebas_pustaka_{nim}.pdf'

    as_attachment = request.args.get('download') == '1'
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=as_attachment,
        download_name=filename
    )


@api_bp.route('/prodi-by-fakultas/<int:fakultas_id>')
def prodi_by_fakultas(fakultas_id):
    """AJAX endpoint untuk dropdown prodi dinamis."""
    from app.models.program_studi import ProgramStudi
    prodi_list = ProgramStudi.query.filter_by(fakultas_id=fakultas_id).order_by(
        ProgramStudi.nama_prodi
    ).all()
    return jsonify([p.to_dict() for p in prodi_list])
