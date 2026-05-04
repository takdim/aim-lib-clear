from app import db


class Fakultas(db.Model):
    __tablename__ = 'fakultas'

    id = db.Column(db.Integer, primary_key=True)
    nama_fakultas = db.Column(db.String(150), nullable=False)
    kode_fakultas = db.Column(db.String(20), unique=True, nullable=False)

    # Relasi
    program_studi = db.relationship('ProgramStudi', backref='fakultas', lazy=True)
    users = db.relationship('User', backref='fakultas', lazy=True)
    pengajuan = db.relationship('BebasPustaka', backref='fakultas', lazy=True)

    def __repr__(self):
        return f'<Fakultas {self.nama_fakultas}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nama_fakultas': self.nama_fakultas,
            'kode_fakultas': self.kode_fakultas,
        }
