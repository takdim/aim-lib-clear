import os
import hashlib
import uuid
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

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file, pengajuan_id, suffix):
    """Simpan file upload dan kembalikan relative path."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    now = datetime.utcnow()
    sub_dir = os.path.join(str(now.year), f'{now.month:02d}', str(pengajuan_id))
    full_dir = os.path.join(upload_folder, sub_dir)
    os.makedirs(full_dir, exist_ok=True)

    unique = hashlib.sha256(f'{uuid.uuid4()}{suffix}'.encode()).hexdigest()[:16]
    filename = f'{unique}_{suffix}.pdf'
    file_path = os.path.join(full_dir, filename)
    file.save(file_path)

    return os.path.join(sub_dir, filename)


def staff_tipe_pengajuan():
    return 'fakultas' if current_user.fakultas_id else 'pusat'


def can_manage_pengajuan(pengajuan):
    if pengajuan.tipe_pengajuan != staff_tipe_pengajuan():
        return False
    return not current_user.fakultas_id or pengajuan.fakultas_id == current_user.fakultas_id


def can_view_pengajuan(pengajuan):
    if can_manage_pengajuan(pengajuan):
        return True
    return (
        current_user.fakultas_id and
        pengajuan.tipe_pengajuan == 'pusat' and
        (pengajuan.created_by == current_user.id or pengajuan.user_id == current_user.id)
    )


@staff_bp.route('/form-bebas-pustaka', methods=['GET', 'POST'])
@login_required
@staff_required
def form_bebas_pustaka():
    tipe_pengajuan = staff_tipe_pengajuan()

    # Scoped staff can only create submissions for their faculty
    if current_user.fakultas_id:
        fakultas_list = Fakultas.query.filter_by(id=current_user.fakultas_id).all()
    else:
        fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()

    if request.method == 'POST':
        nim = request.form.get('nim', '').strip()
        nama = request.form.get('nama', '').strip()
        alamat = request.form.get('alamat', '').strip()
        fakultas_id = request.form.get('fakultas_id', type=int)
        prodi_id = request.form.get('prodi_id', type=int)
        file_bebas = request.files.get('file_bebas_pustaka')
        file_kartu = request.files.get('file_kartu_mahasiswa')

        errors = []
        if not nim:
            errors.append('NIM wajib diisi.')
        if not nama:
            errors.append('Nama Lengkap wajib diisi.')
        if not alamat:
            errors.append('Alamat wajib diisi.')
        if not fakultas_id:
            errors.append('Fakultas wajib dipilih.')
        if not prodi_id:
            errors.append('Program Studi wajib dipilih.')
        if not file_bebas or not allowed_file(file_bebas.filename):
            errors.append('File Bebas Pustaka dari Fakultas wajib diupload (PDF).')
        if not file_kartu or not allowed_file(file_kartu.filename):
            errors.append('File Kartu Tanda Mahasiswa wajib diupload (PDF).')

        if tipe_pengajuan == 'pusat' and not BebasPustaka.query.filter_by(
                nim=nim,
                fakultas_id=fakultas_id,
                tipe_pengajuan='fakultas',
                status='disetujui',
            ).first():
            errors.append('Mahasiswa harus memiliki Bebas Pustaka Fakultas yang disetujui terlebih dahulu.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('staff/form.html', fakultas_list=fakultas_list, is_scoped=bool(current_user.fakultas_id), tipe_pengajuan=tipe_pengajuan)

        pengajuan = BebasPustaka(
            created_by=current_user.id,
            nim=nim,
            nama=nama,
            alamat=alamat,
            fakultas_id=fakultas_id,
            prodi_id=prodi_id,
            tipe_pengajuan=tipe_pengajuan,
            status='menunggu_review',
        )
        db.session.add(pengajuan)
        db.session.flush()

        try:
            path_bebas = save_upload(file_bebas, pengajuan.id, 'bebas_pustaka')
            path_kartu = save_upload(file_kartu, pengajuan.id, 'kartu_mahasiswa')
            pengajuan.file_bebas_pustaka = path_bebas
            pengajuan.file_kartu_mahasiswa = path_kartu
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupload file: {str(e)}', 'danger')
            return render_template('staff/form.html', fakultas_list=fakultas_list, is_scoped=bool(current_user.fakultas_id), tipe_pengajuan=tipe_pengajuan)

        flash('Pengajuan berhasil dibuat. Anda dapat langsung menyetujuinya di halaman detail.', 'success')
        return redirect(url_for('staff.pengajuan_detail', id=pengajuan.id))

    return render_template('staff/form.html', fakultas_list=fakultas_list, is_scoped=bool(current_user.fakultas_id), tipe_pengajuan=tipe_pengajuan)


@staff_bp.route('/pengajuan-saya')
@login_required
@staff_required
def pengajuan_saya():
    riwayat = BebasPustaka.query.filter(
        (BebasPustaka.created_by == current_user.id) |
        (BebasPustaka.user_id == current_user.id)
    ).order_by(
        BebasPustaka.created_at.desc()
    ).all()
    return render_template('staff/pengajuan_saya.html', riwayat=riwayat)


@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    from sqlalchemy import func
    today = datetime.utcnow().date()
    bulan_ini = datetime.utcnow().month
    tahun_ini = datetime.utcnow().year

    # Scoped: filter by faculty if staff has one assigned
    base_q = BebasPustaka.query.filter(
        BebasPustaka.tipe_pengajuan == staff_tipe_pengajuan()
    )
    if current_user.fakultas_id:
        base_q = base_q.filter(BebasPustaka.fakultas_id == current_user.fakultas_id)

    stats = {
        'masuk_hari_ini': base_q.filter(
            func.date(BebasPustaka.created_at) == today
        ).count(),
        'menunggu_review': base_q.filter(BebasPustaka.status == 'menunggu_review').count(),
        'disetujui_bulan_ini': base_q.filter(
            BebasPustaka.status == 'disetujui',
            func.month(BebasPustaka.approved_at) == bulan_ini,
            func.year(BebasPustaka.approved_at) == tahun_ini,
        ).count(),
        'ditolak_bulan_ini': base_q.filter(
            BebasPustaka.status == 'ditolak',
            func.month(BebasPustaka.updated_at) == bulan_ini,
            func.year(BebasPustaka.updated_at) == tahun_ini,
        ).count(),
    }

    pengajuan_terbaru = base_q.order_by(
        BebasPustaka.created_at.desc()
    ).limit(10).all()

    pengajuan_saya = BebasPustaka.query.filter_by(user_id=current_user.id).order_by(
        BebasPustaka.created_at.desc()
    ).all()

    return render_template('staff/dashboard.html', stats=stats, pengajuan_terbaru=pengajuan_terbaru, pengajuan_saya=pengajuan_saya)


@staff_bp.route('/pengajuan')
@login_required
@staff_required
def pengajuan_list():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '').strip()

    # Scoped staff: lock to their faculty, ignore URL param
    if current_user.fakultas_id:
        fakultas_filter = current_user.fakultas_id
    else:
        fakultas_filter = request.args.get('fakultas_id', 0, type=int)

    query = BebasPustaka.query.filter(
        BebasPustaka.tipe_pengajuan == staff_tipe_pengajuan()
    )

    if status_filter:
        query = query.filter(BebasPustaka.status == status_filter)
    if fakultas_filter:
        query = query.filter(BebasPustaka.fakultas_id == fakultas_filter)
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
        is_scoped=bool(current_user.fakultas_id),
    )


@staff_bp.route('/pengajuan/<int:id>', methods=['GET', 'POST'])
@login_required
@staff_required
def pengajuan_detail(id):
    pengajuan = BebasPustaka.query.get_or_404(id)

    if not can_view_pengajuan(pengajuan):
        abort(403)

    if request.method == 'POST':
        if not can_manage_pengajuan(pengajuan):
            abort(403)
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
        fakultas_list=fakultas_list,
        can_process=can_manage_pengajuan(pengajuan),
    )


@staff_bp.route('/pengajuan/<int:id>/file/<string:jenis>')
@login_required
@staff_required
def view_file(id, jenis):
    """Serve file upload untuk ditinjau staff."""
    pengajuan = BebasPustaka.query.get_or_404(id)

    if not can_view_pengajuan(pengajuan):
        abort(403)

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
