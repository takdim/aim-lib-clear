import os
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app, send_from_directory, abort, jsonify
)
from flask_login import login_required, current_user

from app import db
from app.models.bebas_pustaka import BebasPustaka
from app.models.fakultas import Fakultas
from app.utils.decorators import staff_required

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    from sqlalchemy import func
    today = datetime.utcnow().date()
    bulan_ini = datetime.utcnow().month
    tahun_ini = datetime.utcnow().year

    stats = {
        'masuk_hari_ini': BebasPustaka.query.filter(
            func.date(BebasPustaka.created_at) == today
        ).count(),
        'menunggu_review': BebasPustaka.query.filter_by(status='menunggu_review').count(),
        'disetujui_bulan_ini': BebasPustaka.query.filter(
            BebasPustaka.status == 'disetujui',
            func.month(BebasPustaka.approved_at) == bulan_ini,
            func.year(BebasPustaka.approved_at) == tahun_ini,
        ).count(),
        'ditolak_bulan_ini': BebasPustaka.query.filter(
            BebasPustaka.status == 'ditolak',
            func.month(BebasPustaka.updated_at) == bulan_ini,
            func.year(BebasPustaka.updated_at) == tahun_ini,
        ).count(),
    }

    pengajuan_terbaru = BebasPustaka.query.order_by(
        BebasPustaka.created_at.desc()
    ).limit(10).all()

    return render_template('staff/dashboard.html', stats=stats, pengajuan_terbaru=pengajuan_terbaru)


@staff_bp.route('/pengajuan')
@login_required
@staff_required
def pengajuan_list():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    fakultas_filter = request.args.get('fakultas_id', 0, type=int)
    search = request.args.get('search', '').strip()

    query = BebasPustaka.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if fakultas_filter:
        query = query.filter_by(fakultas_id=fakultas_filter)
    if search:
        query = query.filter(
            (BebasPustaka.nim.contains(search)) |
            (BebasPustaka.nama.ilike(f'%{search}%'))
        )

    pagination = query.order_by(BebasPustaka.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )

    fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()

    return render_template(
        'staff/pengajuan_list.html',
        pagination=pagination,
        fakultas_list=fakultas_list,
        status_filter=status_filter,
        fakultas_filter=fakultas_filter,
        search=search,
    )


@staff_bp.route('/pengajuan/<int:id>', methods=['GET', 'POST'])
@login_required
@staff_required
def pengajuan_detail(id):
    pengajuan = BebasPustaka.query.get_or_404(id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'setujui':
            pengajuan.status = 'disetujui'
            pengajuan.reviewed_by = current_user.id
            pengajuan.approved_at = datetime.utcnow()
            # Generate nomor surat
            pengajuan.nomor_surat = pengajuan.generate_nomor_surat()
            db.session.commit()
            flash(f'Pengajuan atas nama {pengajuan.nama} telah disetujui.', 'success')
            return redirect(url_for('staff.pengajuan_list'))

        elif action == 'tolak':
            catatan = request.form.get('catatan_penolakan', '').strip()
            if not catatan:
                flash('Alasan penolakan wajib diisi.', 'danger')
                return redirect(url_for('staff.pengajuan_detail', id=id))
            pengajuan.status = 'ditolak'
            pengajuan.reviewed_by = current_user.id
            pengajuan.catatan_penolakan = catatan
            pengajuan.delete_files()  # Hapus file untuk menghemat storage
            db.session.commit()
            flash(f'Pengajuan atas nama {pengajuan.nama} telah ditolak. File telah dihapus.', 'warning')
            return redirect(url_for('staff.pengajuan_list'))

        elif action == 'proses':
            pengajuan.status = 'sedang_diproses'
            pengajuan.reviewed_by = current_user.id
            db.session.commit()
            flash('Status pengajuan diubah menjadi Sedang Diproses.', 'info')
            return redirect(url_for('staff.pengajuan_detail', id=id))

        elif action == 'edit':
            pengajuan.nama = request.form.get('nama', pengajuan.nama).strip()
            pengajuan.alamat = request.form.get('alamat', pengajuan.alamat).strip()
            fakultas_id = request.form.get('fakultas_id', type=int)
            prodi_id = request.form.get('prodi_id', type=int)
            if fakultas_id:
                pengajuan.fakultas_id = fakultas_id
            if prodi_id:
                pengajuan.prodi_id = prodi_id
            nomor_surat_baru = request.form.get('nomor_surat', '').strip()
            if nomor_surat_baru:
                pengajuan.nomor_surat = nomor_surat_baru
            db.session.commit()
            flash('Data pengajuan berhasil diperbarui.', 'success')
            return redirect(url_for('staff.pengajuan_detail', id=id))

    fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()
    return render_template(
        'staff/pengajuan_detail.html',
        pengajuan=pengajuan,
        fakultas_list=fakultas_list
    )


@staff_bp.route('/pengajuan/<int:id>/file/<string:jenis>')
@login_required
@staff_required
def view_file(id, jenis):
    """Serve file upload untuk ditinjau staff."""
    pengajuan = BebasPustaka.query.get_or_404(id)

    if pengajuan.file_deleted:
        return jsonify({
            'deleted': True,
            'message': 'File PDF ini telah dihapus dari sistem karena telah melewati masa penyimpanan 1 bulan. '
                       'Surat bebas pustaka mahasiswa yang bersangkutan tetap dapat dicetak ulang oleh mahasiswa.'
        }), 410

    if jenis == 'bebas_pustaka':
        rel_path = pengajuan.file_bebas_pustaka
    elif jenis == 'kartu_mahasiswa':
        rel_path = pengajuan.file_kartu_mahasiswa
    else:
        abort(404)

    if not rel_path:
        abort(404)

    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    full_path = os.path.join(upload_folder, rel_path)
    
    if not os.path.exists(full_path):
        abort(404)
        
    dir_path = os.path.dirname(full_path)
    filename = os.path.basename(full_path)

    return send_from_directory(dir_path, filename, as_attachment=False)
