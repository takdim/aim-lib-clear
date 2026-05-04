from app import db


class SistemSetting(db.Model):
    __tablename__ = 'sistem_setting'

    id = db.Column(db.Integer, primary_key=True)

    # Template nomor surat: {nomor_urut}/{nomor_bagian_tengah}/{nomor_tahun}
    # Contoh: 3861/UN4.1.1.5/TA.01.02/2026
    nomor_urut = db.Column(db.Integer, default=1, nullable=False)
    nomor_bagian_tengah = db.Column(db.String(100), default='UN4.1.1.5/TA.01.02', nullable=False)
    nomor_tahun = db.Column(db.Integer, default=2026, nullable=False)

    # Data pejabat penanda tangan
    pejabat_jabatan = db.Column(
        db.String(200),
        default='Ketua Divisi Pelayanan dan\nPenjaminan Mutu\nPerpustakaan',
        nullable=False
    )
    pejabat_nama = db.Column(db.String(150), default='Dr. Iskandar, S.Sos., M.M.', nullable=False)
    pejabat_nip = db.Column(db.String(50), default='197705192001121001', nullable=False)

    @classmethod
    def get(cls):
        """Ambil baris singleton (id=1). Buat jika belum ada."""
        setting = cls.query.first()
        if not setting:
            setting = cls()
            db.session.add(setting)
            db.session.commit()
        return setting

    def generate_and_increment(self):
        """Generate nomor surat lalu naikkan counter."""
        nomor = f"{self.nomor_urut}/{self.nomor_bagian_tengah}/{self.nomor_tahun}"
        self.nomor_urut += 1
        db.session.commit()
        return nomor
