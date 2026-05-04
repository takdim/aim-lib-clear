import bcrypt
import csv
import io
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app, Response, jsonify
)
from flask_login import login_required, current_user

from app import db
from app.models.user import User
from app.models.bebas_pustaka import BebasPustaka
from app.models.fakultas import Fakultas
from app.models.program_studi import ProgramStudi
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    from sqlalchemy import func
    bulan_ini = datetime.utcnow().month
    tahun_ini = datetime.utcnow().year

    stats = {
        'total_mahasiswa': User.query.filter_by(role='mahasiswa').count(),
        'total_staff': User.query.filter_by(role='staff').count(),
        'total_pengajuan': BebasPustaka.query.count(),
        'menunggu': BebasPustaka.query.filter_by(status='menunggu_review').count(),
        'disetujui': BebasPustaka.query.filter_by(status='disetujui').count(),
        'ditolak': BebasPustaka.query.filter_by(status='ditolak').count(),
    }

    # Data grafik: pengajuan per bulan (12 bulan terakhir)
    monthly_data = []
    for i in range(11, -1, -1):
        from dateutil.relativedelta import relativedelta
        target = datetime.utcnow() - relativedelta(months=i)
        count = BebasPustaka.query.filter(
            func.year(BebasPustaka.created_at) == target.year,
            func.month(BebasPustaka.created_at) == target.month,
        ).count()
        monthly_data.append({
            'label': target.strftime('%b %Y'),
            'count': count,
        })

    pengajuan_terbaru = BebasPustaka.query.order_by(
        BebasPustaka.created_at.desc()
    ).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        monthly_data=monthly_data,
        pengajuan_terbaru=pengajuan_terbaru,
    )


# ─── MANAJEMEN PENGGUNA ───────────────────────────────────────
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '').strip()

    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.nim.ilike(f'%{search}%'))
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()

    return render_template(
        'admin/users.html',
        pagination=pagination,
        role_filter=role_filter,
        search=search,
        fakultas_list=fakultas_list,
    )


@admin_bp.route('/users/tambah', methods=['POST'])
@login_required
@admin_required
def tambah_user():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    nim = request.form.get('nim', '').strip() or None
    password = request.form.get('password', '')
    role = request.form.get('role', 'mahasiswa')
    fakultas_id = request.form.get('fakultas_id', type=int)
    prodi_id = request.form.get('prodi_id', type=int)

    if User.query.filter_by(email=email).first():
        flash('Email sudah terdaftar.', 'danger')
        return redirect(url_for('admin.users'))
    if nim and User.query.filter_by(nim=nim).first():
        flash('NIM sudah terdaftar.', 'danger')
        return redirect(url_for('admin.users'))

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(
        name=name, email=email, nim=nim,
        password=hashed, role=role,
        fakultas_id=fakultas_id, prodi_id=prodi_id,
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    flash(f'Pengguna {name} berhasil ditambahkan.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    user.name = request.form.get('name', user.name).strip()
    user.email = request.form.get('email', user.email).strip().lower()
    user.role = request.form.get('role', user.role)

    new_password = request.form.get('password', '').strip()
    if new_password:
        user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db.session.commit()
    flash(f'Data pengguna {user.name} berhasil diperbarui.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:id>/toggle-aktif', methods=['POST'])
@login_required
@admin_required
def toggle_aktif(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Anda tidak bisa menonaktifkan akun sendiri.', 'danger')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'diaktifkan' if user.is_active else 'dinonaktifkan'
    flash(f'Akun {user.name} berhasil {status}.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:id>/hapus', methods=['POST'])
@login_required
@admin_required
def hapus_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Anda tidak bisa menghapus akun sendiri.', 'danger')
        return redirect(url_for('admin.users'))
    if BebasPustaka.query.filter_by(user_id=user.id).first():
        flash('Pengguna memiliki data pengajuan dan tidak dapat dihapus.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'Pengguna {user.name} berhasil dihapus.', 'success')
    return redirect(url_for('admin.users'))


# ─── PEMANTAUAN PENGAJUAN ─────────────────────────────────────
@admin_bp.route('/pengajuan')
@login_required
@admin_required
def pengajuan():
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
        page=page, per_page=20, error_out=False
    )
    fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()

    return render_template(
        'admin/pengajuan.html',
        pagination=pagination,
        fakultas_list=fakultas_list,
        status_filter=status_filter,
        fakultas_filter=fakultas_filter,
        search=search,
    )


@admin_bp.route('/pengajuan/export-csv')
@login_required
@admin_required
def export_csv():
    semua = BebasPustaka.query.order_by(BebasPustaka.created_at.desc()).all()

    def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'NIM', 'Nama', 'Fakultas', 'Prodi', 'Status', 'Tgl Pengajuan', 'Tgl Disetujui'])
        for p in semua:
            writer.writerow([
                p.id, p.nim, p.nama,
                p.fakultas.nama_fakultas if p.fakultas else '-',
                p.program_studi.nama_prodi if p.program_studi else '-',
                p.get_status_label(),
                p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else '-',
                p.approved_at.strftime('%Y-%m-%d %H:%M') if p.approved_at else '-',
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    filename = f'pengajuan_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(
        generate(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


# ─── MANAJEMEN REFERENSI ──────────────────────────────────────
@admin_bp.route('/referensi')
@login_required
@admin_required
def referensi():
    fakultas_list = Fakultas.query.order_by(Fakultas.nama_fakultas).all()
    prodi_list = ProgramStudi.query.join(Fakultas).order_by(
        Fakultas.nama_fakultas, ProgramStudi.nama_prodi
    ).all()
    return render_template('admin/referensi.html', fakultas_list=fakultas_list, prodi_list=prodi_list)


@admin_bp.route('/referensi/fakultas/tambah', methods=['POST'])
@login_required
@admin_required
def tambah_fakultas():
    nama = request.form.get('nama_fakultas', '').strip()
    kode = request.form.get('kode_fakultas', '').strip().upper()
    if Fakultas.query.filter_by(kode_fakultas=kode).first():
        flash('Kode fakultas sudah ada.', 'danger')
    else:
        db.session.add(Fakultas(nama_fakultas=nama, kode_fakultas=kode))
        db.session.commit()
        flash(f'Fakultas {nama} berhasil ditambahkan.', 'success')
    return redirect(url_for('admin.referensi'))


@admin_bp.route('/referensi/fakultas/<int:id>/hapus', methods=['POST'])
@login_required
@admin_required
def hapus_fakultas(id):
    fakultas = Fakultas.query.get_or_404(id)
    if ProgramStudi.query.filter_by(fakultas_id=id).count() > 0:
        flash('Fakultas masih memiliki Program Studi dan tidak dapat dihapus.', 'danger')
    else:
        db.session.delete(fakultas)
        db.session.commit()
        flash('Fakultas berhasil dihapus.', 'success')
    return redirect(url_for('admin.referensi'))


@admin_bp.route('/referensi/prodi/tambah', methods=['POST'])
@login_required
@admin_required
def tambah_prodi():
    nama = request.form.get('nama_prodi', '').strip()
    kode = request.form.get('kode_prodi', '').strip().upper()
    fakultas_id = request.form.get('fakultas_id', type=int)
    db.session.add(ProgramStudi(nama_prodi=nama, kode_prodi=kode, fakultas_id=fakultas_id))
    db.session.commit()
    flash(f'Program Studi {nama} berhasil ditambahkan.', 'success')
    return redirect(url_for('admin.referensi'))


@admin_bp.route('/referensi/prodi/<int:id>/hapus', methods=['POST'])
@login_required
@admin_required
def hapus_prodi(id):
    prodi = ProgramStudi.query.get_or_404(id)
    db.session.delete(prodi)
    db.session.commit()
    flash('Program Studi berhasil dihapus.', 'success')
    return redirect(url_for('admin.referensi'))


# ─── PENGATURAN SISTEM ────────────────────────────────────────
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    if request.method == 'POST':
        flash('Pengaturan sistem hanya dapat diubah melalui file .env.', 'info')
    return render_template('admin/settings.html')
