from datetime import datetime

from app import db


class FakultasSetting(db.Model):
    __tablename__ = 'fakultas_setting'

    id = db.Column(db.Integer, primary_key=True)
    fakultas_id = db.Column(db.Integer, db.ForeignKey('fakultas.id'), nullable=False, unique=True)
    nama_perpustakaan = db.Column(db.String(200), nullable=False)
    nomor_urut = db.Column(db.Integer, default=1, nullable=False)
    nomor_bagian_tengah = db.Column(db.String(100), nullable=False)
    nomor_tahun = db.Column(db.Integer, default=lambda: datetime.utcnow().year, nullable=False)
    pejabat_jabatan = db.Column(db.String(200), nullable=False)
    pejabat_nama = db.Column(db.String(150), nullable=False)
    pejabat_nip = db.Column(db.String(50), nullable=False)

    @classmethod
    def get_for_fakultas(cls, fakultas):
        setting = cls.query.filter_by(fakultas_id=fakultas.id).first()
        if setting:
            return setting

        setting = cls(
            fakultas_id=fakultas.id,
            nama_perpustakaan=f'Perpustakaan {fakultas.nama_fakultas}',
            nomor_bagian_tengah=fakultas.kode_fakultas,
            pejabat_jabatan='Kepala Perpustakaan Fakultas',
            pejabat_nama='-',
            pejabat_nip='-',
        )
        db.session.add(setting)
        db.session.flush()
        return setting

    def generate_and_increment(self):
        nomor = f"{self.nomor_urut}/{self.nomor_bagian_tengah}/{self.nomor_tahun}"
        self.nomor_urut += 1
        db.session.commit()
        return nomor