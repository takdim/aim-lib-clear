from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(20), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('admin', 'staff', 'mahasiswa', name='user_roles'),
        nullable=False,
        default='mahasiswa'
    )
    fakultas_id = db.Column(db.Integer, db.ForeignKey('fakultas.id'), nullable=True)
    prodi_id = db.Column(db.Integer, db.ForeignKey('program_studi.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi pengajuan sebagai mahasiswa
    submissions = db.relationship(
        'BebasPustaka',
        foreign_keys='BebasPustaka.user_id',
        backref='mahasiswa',
        lazy=True
    )

    # Relasi pengajuan yang diproses sebagai staff/admin
    reviewed_submissions = db.relationship(
        'BebasPustaka',
        foreign_keys='BebasPustaka.reviewed_by',
        backref='reviewer',
        lazy=True
    )

    created_submissions = db.relationship(
        'BebasPustaka',
        foreign_keys='BebasPustaka.created_by',
        backref='creator',
        lazy=True
    )

    def is_locked(self):
        """Cek apakah akun sedang dikunci karena brute-force."""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False

    def get_active_submission(self):
        """Ambil pengajuan aktif mahasiswa (menunggu/diproses/disetujui)."""
        from app.models.bebas_pustaka import BebasPustaka
        return BebasPustaka.query.filter(
            BebasPustaka.user_id == self.id,
            BebasPustaka.status.in_(['menunggu_review', 'sedang_diproses', 'disetujui'])
        ).order_by(BebasPustaka.created_at.desc()).first()

    def can_submit(self):
        """Apakah mahasiswa boleh mengajukan baru."""
        active = self.get_active_submission()
        return active is None

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
