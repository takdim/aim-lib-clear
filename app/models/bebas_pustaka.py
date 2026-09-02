import os
from datetime import datetime, timedelta
from flask import current_app
from app import db


class BebasPustaka(db.Model):
    __tablename__ = 'bebas_pustaka'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    nim = db.Column(db.String(20), nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    fakultas_id = db.Column(db.Integer, db.ForeignKey('fakultas.id'), nullable=False)
    prodi_id = db.Column(db.Integer, db.ForeignKey('program_studi.id'), nullable=False)

    file_bebas_pustaka = db.Column(db.String(255), nullable=True)
    file_kartu_mahasiswa = db.Column(db.String(255), nullable=True)
    file_deleted = db.Column(db.Boolean, default=False, nullable=False)
    file_deleted_at = db.Column(db.DateTime, nullable=True)

    tipe_pengajuan = db.Column(
        db.String(20), default='pusat', nullable=False
    )

    status = db.Column(
        db.Enum('menunggu_review', 'sedang_diproses', 'disetujui', 'ditolak', name='status_enum'),
        default='menunggu_review',
        nullable=False
    )
    catatan_penolakan = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    nomor_surat = db.Column(db.String(100), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    berlaku_sampai = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_file_available(self):
        """Cek apakah file upload mahasiswa masih tersedia (belum dihapus & < 30 hari)."""
        if self.file_deleted:
            return False
        if not self.approved_at:
            return True
        retention = current_app.config.get('FILE_RETENTION_DAYS', 30)
        return not self.is_berlaku_expired()

    def is_approved_over_retention(self):
        """Apakah sudah disetujui lebih dari retention period (tombol cetak ulang)."""
        if self.status != 'disetujui' or not self.approved_at:
            return False
        retention = current_app.config.get('FILE_RETENTION_DAYS', 30)
        return self.is_berlaku_expired()

    def is_berlaku_expired(self):
        if self.status != 'disetujui' or not self.approved_at:
            return False
        expires_at = self.berlaku_sampai or self.approved_at + timedelta(days=90)
        return datetime.utcnow() > expires_at

    def get_berlaku_sampai(self):
        if not self.approved_at:
            return None
        return self.berlaku_sampai or self.approved_at + timedelta(days=90)

    def get_status_label(self):
        labels = {
            'menunggu_review': 'Menunggu Review',
            'sedang_diproses': 'Sedang Diproses',
            'disetujui': 'Disetujui',
            'ditolak': 'Ditolak',
        }
        return labels.get(self.status, self.status)

    def get_tipe_label(self):
        labels = {
            'fakultas': 'Bebas Pustaka Fakultas',
            'pusat': 'Bebas Pustaka Pusat',
        }
        return labels.get(self.tipe_pengajuan, self.tipe_pengajuan)

    def get_status_badge_class(self):
        classes = {
            'menunggu_review': 'badge-warning',
            'sedang_diproses': 'badge-info',
            'disetujui': 'badge-success',
            'ditolak': 'badge-danger',
        }
        return classes.get(self.status, 'badge-secondary')

    def generate_nomor_surat(self):
        """Generate nomor surat dari SistemSetting lalu naikkan counter."""
        if self.tipe_pengajuan == 'fakultas':
            from app.models.fakultas_setting import FakultasSetting
            setting = FakultasSetting.get_for_fakultas(self.fakultas)
            return setting.generate_and_increment()

        from app.models.sistem_setting import SistemSetting
        setting = SistemSetting.get()
        return setting.generate_and_increment()

    def delete_files(self):
        """Hapus file fisik dari disk."""
        upload_folder = current_app.config['UPLOAD_FOLDER']
        deleted = False
        for field in ['file_bebas_pustaka', 'file_kartu_mahasiswa']:
            path = getattr(self, field)
            if path:
                full_path = os.path.join(upload_folder, path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    deleted = True
        if deleted:
            self.file_deleted = True
            self.file_deleted_at = datetime.utcnow()
        return deleted

    def __repr__(self):
        return f'<BebasPustaka {self.nim} - {self.status}>'
