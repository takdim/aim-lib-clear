import os
import hashlib
import uuid
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app
)
from flask_login import login_required, current_user

from app import db
from app.models.bebas_pustaka import BebasPustaka
from app.utils.decorators import mahasiswa_required

mahasiswa_bp = Blueprint('mahasiswa', __name__)

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

    # Hash nama file untuk keamanan
    unique = hashlib.sha256(f'{uuid.uuid4()}{suffix}'.encode()).hexdigest()[:16]
    filename = f'{unique}_{suffix}.pdf'
    file_path = os.path.join(full_dir, filename)
    file.save(file_path)

    return os.path.join(sub_dir, filename)


@mahasiswa_bp.route('/dashboard')
@login_required
@mahasiswa_required
def dashboard():
    pengajuan_terbaru = BebasPustaka.query.filter_by(user_id=current_user.id).order_by(
        BebasPustaka.created_at.desc()
    ).first()
    riwayat = BebasPustaka.query.filter_by(user_id=current_user.id).order_by(
        BebasPustaka.created_at.desc()
    ).all()
    return render_template(
        'mahasiswa/dashboard.html',
        pengajuan_terbaru=pengajuan_terbaru,
        riwayat=riwayat
    )


@mahasiswa_bp.route('/form-bebas-pustaka', methods=['GET', 'POST'])
@login_required
@mahasiswa_required
def form_bebas_pustaka():
    # Cek apakah boleh mengajukan
    if not current_user.can_submit():
        flash('Anda masih memiliki pengajuan yang aktif.', 'warning')
        return redirect(url_for('mahasiswa.status'))

    if request.method == 'POST':
        alamat = request.form.get('alamat', '').strip()
        file_bebas = request.files.get('file_bebas_pustaka')
        file_kartu = request.files.get('file_kartu_mahasiswa')

        errors = []
        if not alamat:
            errors.append('Alamat wajib diisi.')
        if not file_bebas or not allowed_file(file_bebas.filename):
            errors.append('File Bebas Pustaka dari Fakultas wajib diupload (PDF).')
        if not file_kartu or not allowed_file(file_kartu.filename):
            errors.append('File Kartu Mahasiswa wajib diupload (PDF).')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('mahasiswa/form.html')

        # Simpan pengajuan ke DB dulu untuk dapat ID
        pengajuan = BebasPustaka(
            user_id=current_user.id,
            nim=current_user.nim,
            nama=current_user.name,
            alamat=alamat,
            fakultas_id=current_user.fakultas_id,
            prodi_id=current_user.prodi_id,
            status='menunggu_review',
        )
        db.session.add(pengajuan)
        db.session.flush()  # Dapat ID tanpa commit

        # Simpan file
        try:
            path_bebas = save_upload(file_bebas, pengajuan.id, 'bebas_pustaka')
            path_kartu = save_upload(file_kartu, pengajuan.id, 'kartu_mahasiswa')
            pengajuan.file_bebas_pustaka = path_bebas
            pengajuan.file_kartu_mahasiswa = path_kartu
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupload file: {str(e)}', 'danger')
            return render_template('mahasiswa/form.html')

        flash('Pengajuan berhasil dikirim! Tunggu review dari staff.', 'success')
        return redirect(url_for('mahasiswa.status'))

    return render_template('mahasiswa/form.html')


@mahasiswa_bp.route('/status')
@login_required
@mahasiswa_required
def status():
    pengajuan = BebasPustaka.query.filter_by(user_id=current_user.id).order_by(
        BebasPustaka.created_at.desc()
    ).first()
    return render_template('mahasiswa/status.html', pengajuan=pengajuan)
