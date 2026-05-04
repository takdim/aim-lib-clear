"""
Script untuk mengisi data awal (seed) database.
Jalankan setelah flask db upgrade:
    python seed.py
"""
import bcrypt
from app import create_app, db
from app.models.user import User
from app.models.fakultas import Fakultas
from app.models.program_studi import ProgramStudi


def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Mulai seed data...")

        # ─── FAKULTAS ────────────────────────────────────────
        fakultas_data = [
            {"kode": "FK",    "nama": "Fakultas Kedokteran"},
            {"kode": "FKG",   "nama": "Fakultas Kedokteran Gigi"},
            {"kode": "FKM",   "nama": "Fakultas Kesehatan Masyarakat"},
            {"kode": "FKEP",  "nama": "Fakultas Keperawatan"},
            {"kode": "FF",    "nama": "Fakultas Farmasi"},
            {"kode": "FT",    "nama": "Fakultas Teknik"},
            {"kode": "FMIPA", "nama": "Fakultas Matematika dan Ilmu Pengetahuan Alam"},
            {"kode": "FEB",   "nama": "Fakultas Ekonomi dan Bisnis"},
            {"kode": "FH",    "nama": "Fakultas Hukum"},
            {"kode": "FISIP", "nama": "Fakultas Ilmu Sosial dan Ilmu Politik"},
            {"kode": "FIB",   "nama": "Fakultas Ilmu Budaya"},
            {"kode": "FPER",  "nama": "Fakultas Pertanian"},
            {"kode": "FIKP",  "nama": "Fakultas Ilmu Kelautan dan Perikanan"},
            {"kode": "FPET",  "nama": "Fakultas Peternakan"},
            {"kode": "FHUT",  "nama": "Fakultas Kehutanan"},
        ]

        fakultas_objs = {}
        for f in fakultas_data:
            existing = Fakultas.query.filter_by(kode_fakultas=f["kode"]).first()
            if not existing:
                obj = Fakultas(nama_fakultas=f["nama"], kode_fakultas=f["kode"])
                db.session.add(obj)
                db.session.flush()
                fakultas_objs[f["kode"]] = obj
                print(f"  ✅ Fakultas: {f['nama']}")
            else:
                fakultas_objs[f["kode"]] = existing
                print(f"  ⏩ Fakultas sudah ada: {f['nama']}")

        # ─── PROGRAM STUDI ────────────────────────────────────
        prodi_data = [
            # FK
            {"kode": "PD",     "nama": "S1 Pendidikan Dokter", "fak": "FK"},
            {"kode": "PSI",    "nama": "S1 Psikologi", "fak": "FK"},
            {"kode": "KH",     "nama": "S1 Kedokteran Hewan", "fak": "FK"},
            # FKG
            {"kode": "PDG",    "nama": "S1 Pendidikan Dokter Gigi", "fak": "FKG"},
            # FKM
            {"kode": "KM",     "nama": "S1 Kesehatan Masyarakat", "fak": "FKM"},
            {"kode": "GZ",     "nama": "S1 Gizi", "fak": "FKM"},
            # FKEP
            {"kode": "IK",     "nama": "S1 Ilmu Keperawatan", "fak": "FKEP"},
            {"kode": "KB",     "nama": "S1 Kebidanan", "fak": "FKEP"},
            # FF
            {"kode": "FR",     "nama": "S1 Farmasi", "fak": "FF"},
            # FT
            {"kode": "TS",     "nama": "Teknik Sipil", "fak": "FT"},
            {"kode": "TM",     "nama": "Teknik Mesin", "fak": "FT"},
            {"kode": "TI",     "nama": "Teknik Industri", "fak": "FT"},
            {"kode": "TL",     "nama": "Teknik Kelautan", "fak": "FT"},
            {"kode": "TSP",    "nama": "Teknik Sistem Perkapalan", "fak": "FT"},
            {"kode": "TP",     "nama": "Teknik Pertambangan", "fak": "FT"},
            {"kode": "TINF",   "nama": "Teknik Informatika", "fak": "FT"},
            {"kode": "TLIN",   "nama": "Teknik Lingkungan", "fak": "FT"},
            {"kode": "TMM",    "nama": "Teknik Metalurgi dan Material", "fak": "FT"},
            {"kode": "TG",     "nama": "Teknik Geodesi", "fak": "FT"},
            {"kode": "PWK",    "nama": "Perencanaan Wilayah dan Kota", "fak": "FT"},
            {"kode": "TKA",    "nama": "S1 Perkeretaapian", "fak": "FT"},
            {"kode": "TKB",    "nama": "S1 Kecerdasan Buatan", "fak": "FT"},
            # FMIPA
            {"kode": "MTK",    "nama": "Matematika", "fak": "FMIPA"},
            {"kode": "FIS",    "nama": "Fisika", "fak": "FMIPA"},
            {"kode": "KIM",    "nama": "Kimia", "fak": "FMIPA"},
            {"kode": "BIO",    "nama": "Biologi", "fak": "FMIPA"},
            {"kode": "STA",    "nama": "Statistika", "fak": "FMIPA"},
            {"kode": "GFI",    "nama": "Geofisika", "fak": "FMIPA"},
            {"kode": "AKT",    "nama": "Aktuaria", "fak": "FMIPA"},
            {"kode": "TKIM",   "nama": "S1 Teknik Kimia", "fak": "FMIPA"},
            # FEB
            {"kode": "EP",     "nama": "S1 Ekonomi Pembangunan", "fak": "FEB"},
            {"kode": "MNJ",    "nama": "S1 Manajemen", "fak": "FEB"},
            {"kode": "AKN",    "nama": "S1 Akuntansi", "fak": "FEB"},
            {"kode": "EBI",    "nama": "S1 Ekonomi dan Bisnis Islam", "fak": "FEB"},
            {"kode": "KBD",    "nama": "Kewirausahaan dan Bisnis Digital", "fak": "FEB"},
            # FH
            {"kode": "IH",     "nama": "S1 Ilmu Hukum", "fak": "FH"},
            {"kode": "HAN",    "nama": "S1 Hukum Administrasi Negara", "fak": "FH"},
            # FISIP
            {"kode": "IP",     "nama": "S1 Ilmu Politik", "fak": "FISIP"},
            {"kode": "IPEM",   "nama": "S1 Ilmu Pemerintahan", "fak": "FISIP"},
            {"kode": "IHI",    "nama": "S1 Ilmu Hubungan Internasional", "fak": "FISIP"},
            {"kode": "IKOM",   "nama": "S1 Ilmu Komunikasi", "fak": "FISIP"},
            {"kode": "SOS",    "nama": "S1 Sosiologi", "fak": "FISIP"},
            {"kode": "ANT",    "nama": "S1 Antropologi", "fak": "FISIP"},
            {"kode": "AP",     "nama": "S1 Administrasi Publik", "fak": "FISIP"},
            {"kode": "KD",     "nama": "S1 Komunikasi Digital", "fak": "FISIP"},
            # FIB
            {"kode": "SI",     "nama": "Sastra Indonesia", "fak": "FIB"},
            {"kode": "SS",     "nama": "Sastra Inggris", "fak": "FIB"},
            {"kode": "SD",     "nama": "Sastra Daerah", "fak": "FIB"},
            {"kode": "SA",     "nama": "Sastra Arab", "fak": "FIB"},
            {"kode": "SJ",     "nama": "Sastra Jepang", "fak": "FIB"},
            {"kode": "SF",     "nama": "Sastra Perancis", "fak": "FIB"},
            {"kode": "IS",     "nama": "Ilmu Sejarah", "fak": "FIB"},
            {"kode": "ARK",    "nama": "Arkeologi", "fak": "FIB"},
            # FPER
            {"kode": "AGT",    "nama": "Agroteknologi", "fak": "FPER"},
            {"kode": "AGB",    "nama": "Agribisnis", "fak": "FPER"},
            {"kode": "ITP",    "nama": "Ilmu dan Teknologi Pangan", "fak": "FPER"},
            {"kode": "KTP",    "nama": "Keteknikan Pertanian", "fak": "FPER"},
            {"kode": "PBT",    "nama": "S1 Pemuliaan dan Bioteknologi Tanaman", "fak": "FPER"},
            {"kode": "PP",     "nama": "S1 Pembangunan Pertanian", "fak": "FPER"},
            # FIKP
            {"kode": "IKL",    "nama": "Ilmu Kelautan", "fak": "FIKP"},
            {"kode": "MSL",    "nama": "Manajemen Sumberdaya Perairan", "fak": "FIKP"},
            {"kode": "BP",     "nama": "Budidaya Perairan", "fak": "FIKP"},
            {"kode": "PSP",    "nama": "Pemanfaatan Sumberdaya Perikanan", "fak": "FIKP"},
            # FPET
            {"kode": "PTR",    "nama": "S1 Peternakan", "fak": "FPET"},
            # FHUT
            {"kode": "HUT",    "nama": "S1 Kehutanan", "fak": "FHUT"},
        ]

        for p in prodi_data:
            fak_obj = fakultas_objs.get(p["fak"])
            if not fak_obj:
                continue
            existing = ProgramStudi.query.filter_by(kode_prodi=p["kode"]).first()
            if not existing:
                obj = ProgramStudi(
                    nama_prodi=p["nama"],
                    kode_prodi=p["kode"],
                    fakultas_id=fak_obj.id
                )
                db.session.add(obj)
                print(f"  ✅ Prodi: {p['nama']}")
            else:
                print(f"  ⏩ Prodi sudah ada: {p['nama']}")

        db.session.commit()

        # ─── USERS ───────────────────────────────────────────
        users_data = [
            {
                "name": "Administrator",
                "email": "admin@perpus.ac.id",
                "password": "Admin@123",
                "role": "admin",
                "nim": None,
            },
            {
                "name": "Staff Perpustakaan",
                "email": "staff@perpus.ac.id",
                "password": "Staff@123",
                "role": "staff",
                "nim": None,
            },
            {
                "name": "Budi Santoso",
                "email": "budi@mahasiswa.ac.id",
                "password": "Mahasiswa@123",
                "role": "mahasiswa",
                "nim": "2021001001",
                "fakultas_kode": "FT",
                "prodi_kode": "TI",
            },
        ]

        for u in users_data:
            existing = User.query.filter_by(email=u["email"]).first()
            if existing:
                print(f"  ⏩ User sudah ada: {u['email']}")
                continue

            hashed = bcrypt.hashpw(u["password"].encode(), bcrypt.gensalt()).decode()

            fakultas_id = None
            prodi_id = None
            if u.get("fakultas_kode"):
                fak = fakultas_objs.get(u["fakultas_kode"])
                if fak:
                    fakultas_id = fak.id
            if u.get("prodi_kode"):
                prodi = ProgramStudi.query.filter_by(kode_prodi=u["prodi_kode"]).first()
                if prodi:
                    prodi_id = prodi.id

            user_obj = User(
                name=u["name"],
                email=u["email"],
                password=hashed,
                role=u["role"],
                nim=u.get("nim"),
                fakultas_id=fakultas_id,
                prodi_id=prodi_id,
                is_active=True,
            )
            db.session.add(user_obj)
            print(f"  ✅ User: {u['email']} [{u['role']}]")

        db.session.commit()

        print("\n🎉 Seed selesai!")
        print("\n📋 Akun default:")
        print("   Admin  : admin@perpus.ac.id   | Admin@123")
        print("   Staff  : staff@perpus.ac.id   | Staff@123")
        print("   Mahasiswa: budi@mahasiswa.ac.id | Mahasiswa@123")


if __name__ == "__main__":
    seed()
