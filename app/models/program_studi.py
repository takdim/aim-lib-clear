from app import db


class ProgramStudi(db.Model):
    __tablename__ = 'program_studi'

    id = db.Column(db.Integer, primary_key=True)
    nama_prodi = db.Column(db.String(150), nullable=False)
    kode_prodi = db.Column(db.String(20), nullable=False)
    fakultas_id = db.Column(db.Integer, db.ForeignKey('fakultas.id'), nullable=False)

    # Relasi
    users = db.relationship('User', backref='program_studi', lazy=True)
    pengajuan = db.relationship('BebasPustaka', backref='program_studi', lazy=True)

    def __repr__(self):
        return f'<ProgramStudi {self.nama_prodi}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nama_prodi': self.nama_prodi,
            'kode_prodi': self.kode_prodi,
            'fakultas_id': self.fakultas_id,
        }
