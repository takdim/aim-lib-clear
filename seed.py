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
            {"kode": "FTP",   "nama": "Fakultas Teknologi Pertanian"},
            {"kode": "SPS",   "nama": "Sekolah Pascasarjana"},
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

            # ─── FK S2/S3 ───────────────────────────────────────
            {"kode": "S2.FK.IPKK",  "nama": "S2 Ilmu Pendidikan Kedokteran dan Kesehatan", "fak": "FK"},
            {"kode": "S3.FK.IK",    "nama": "S3 Ilmu Kedokteran", "fak": "FK"},

            # ─── FKG S2/S3 ──────────────────────────────────────
            {"kode": "S2.FKG.KG",   "nama": "S2 Kedokteran Gigi", "fak": "FKG"},
            {"kode": "S3.FKG.IKG",  "nama": "S3 Ilmu Kedokteran Gigi", "fak": "FKG"},

            # ─── FKM S2/S3 ──────────────────────────────────────
            {"kode": "S2.FKM.IKM",  "nama": "S2 Ilmu Kesehatan Masyarakat", "fak": "FKM"},
            {"kode": "S2.FKM.ARS",  "nama": "S2 Administrasi Rumah Sakit", "fak": "FKM"},
            {"kode": "S2.FKM.K3",   "nama": "S2 Keselamatan dan Kesehatan Kerja", "fak": "FKM"},
            {"kode": "S2.FKM.AKK",  "nama": "S2 Administrasi dan Kebijakan Kesehatan", "fak": "FKM"},
            {"kode": "S2.FKM.GZ",   "nama": "S2 Ilmu Gizi", "fak": "FKM"},
            {"kode": "S2.FKM.KL",   "nama": "S2 Kesehatan Lingkungan", "fak": "FKM"},
            {"kode": "S3.FKM.KM",   "nama": "S3 Kesehatan Masyarakat", "fak": "FKM"},

            # ─── FKEP S1 missing + S2 ───────────────────────────
            {"kode": "FISIO",        "nama": "S1 Fisioterapi", "fak": "FKEP"},
            {"kode": "S2.FKEP.IK",  "nama": "S2 Ilmu Keperawatan", "fak": "FKEP"},

            # ─── FF S2/S3 ───────────────────────────────────────
            {"kode": "S2.FF.FR",    "nama": "S2 Farmasi", "fak": "FF"},
            {"kode": "S3.FF.IFR",   "nama": "S3 Ilmu Farmasi", "fak": "FF"},

            # ─── FT S1 missing ──────────────────────────────────
            {"kode": "TPKP",        "nama": "S1 Teknik Perkapalan", "fak": "FT"},
            {"kode": "TE",          "nama": "S1 Teknik Elektro", "fak": "FT"},
            {"kode": "ARS",         "nama": "S1 Arsitektur", "fak": "FT"},
            {"kode": "TGEO",        "nama": "S1 Teknik Geologi", "fak": "FT"},
            # FT S2
            {"kode": "S2.FT.TM",    "nama": "S2 Teknik Mesin", "fak": "FT"},
            {"kode": "S2.FT.TS",    "nama": "S2 Teknik Sipil", "fak": "FT"},
            {"kode": "S2.FT.TE",    "nama": "S2 Teknik Elektro", "fak": "FT"},
            {"kode": "S2.FT.TGEO",  "nama": "S2 Teknik Geologi", "fak": "FT"},
            {"kode": "S2.FT.TPKP",  "nama": "S2 Teknik Perkapalan", "fak": "FT"},
            {"kode": "S2.FT.ARS",   "nama": "S2 Arsitektur", "fak": "FT"},
            {"kode": "S2.FT.TI",    "nama": "S2 Teknik Industri", "fak": "FT"},
            {"kode": "S2.FT.TINF",  "nama": "S2 Teknik Informatika", "fak": "FT"},
            {"kode": "S2.FT.TLIN",  "nama": "S2 Teknik Lingkungan", "fak": "FT"},
            {"kode": "S2.FT.PWK",   "nama": "S2 Teknik Perencanaan Wilayah dan Kota", "fak": "FT"},
            {"kode": "S2.FT.TP",    "nama": "S2 Teknik Pertambangan", "fak": "FT"},
            {"kode": "S2.FT.TKL",   "nama": "S2 Teknik Kelautan", "fak": "FT"},
            # FT S3
            {"kode": "S3.FT.TS",    "nama": "S3 Teknik Sipil", "fak": "FT"},
            {"kode": "S3.FT.ARS",   "nama": "S3 Ilmu Arsitektur", "fak": "FT"},
            {"kode": "S3.FT.TBL",   "nama": "S3 Teknologi Kebumian dan Lingkungan", "fak": "FT"},
            {"kode": "S3.FT.TE",    "nama": "S3 Teknik Elektro", "fak": "FT"},
            {"kode": "S3.FT.TM",    "nama": "S3 Teknik Mesin", "fak": "FT"},
            {"kode": "S3.FT.INF",   "nama": "S3 Informatika", "fak": "FT"},

            # ─── FMIPA S1 missing + S2/S3 ───────────────────────
            {"kode": "SINFO",           "nama": "S1 Sistem Informasi", "fak": "FMIPA"},
            {"kode": "S2.FMIPA.KIM",    "nama": "S2 Kimia", "fak": "FMIPA"},
            {"kode": "S2.FMIPA.MTK",    "nama": "S2 Matematika", "fak": "FMIPA"},
            {"kode": "S2.FMIPA.GFI",    "nama": "S2 Geofisika", "fak": "FMIPA"},
            {"kode": "S2.FMIPA.FIS",    "nama": "S2 Fisika", "fak": "FMIPA"},
            {"kode": "S2.FMIPA.BIO",    "nama": "S2 Biologi", "fak": "FMIPA"},
            {"kode": "S2.FMIPA.STA",    "nama": "S2 Statistika", "fak": "FMIPA"},
            {"kode": "S2.FMIPA.SD",     "nama": "S2 Sains Data", "fak": "FMIPA"},
            {"kode": "S3.FMIPA.KIM",    "nama": "S3 Kimia", "fak": "FMIPA"},
            {"kode": "S3.FMIPA.MTK",    "nama": "S3 Matematika", "fak": "FMIPA"},
            {"kode": "S3.FMIPA.FIS",    "nama": "S3 Fisika", "fak": "FMIPA"},
            {"kode": "S3.FMIPA.BIO",    "nama": "S3 Biologi", "fak": "FMIPA"},

            # ─── FEB S2/S3 ──────────────────────────────────────
            {"kode": "S2.FEB.ESD",  "nama": "S2 Ekonomi Sumber Daya", "fak": "FEB"},
            {"kode": "S2.FEB.EPP",  "nama": "S2 Ekonomi Pembangunan dan Perencanaan", "fak": "FEB"},
            {"kode": "S2.FEB.SM",   "nama": "S2 Sains Manajemen", "fak": "FEB"},
            {"kode": "S2.FEB.MNJ",  "nama": "S2 Manajemen", "fak": "FEB"},
            {"kode": "S2.FEB.KD",   "nama": "S2 Keuangan Daerah", "fak": "FEB"},
            {"kode": "S2.FEB.AKN",  "nama": "S2 Akuntansi", "fak": "FEB"},
            {"kode": "S2.FEB.KMI",  "nama": "S2 Keuangan Mikro", "fak": "FEB"},
            {"kode": "S3.FEB.IE",   "nama": "S3 Ilmu Ekonomi", "fak": "FEB"},
            {"kode": "S3.FEB.IAKN", "nama": "S3 Ilmu Akuntansi", "fak": "FEB"},
            {"kode": "S3.FEB.MNJ",  "nama": "S3 Manajemen", "fak": "FEB"},

            # ─── FH S2/S3 ───────────────────────────────────────
            {"kode": "S2.FH.IH",    "nama": "S2 Ilmu Hukum", "fak": "FH"},
            {"kode": "S2.FH.KN",    "nama": "S2 Kenotariatan", "fak": "FH"},
            {"kode": "S3.FH.IH",    "nama": "S3 Ilmu Hukum", "fak": "FH"},

            # ─── FISIP S1 missing + S2/S3 ───────────────────────
            {"kode": "ILPSI",           "nama": "S1 Ilmu Perpustakaan dan Sains Informasi", "fak": "FISIP"},
            {"kode": "S2.FISIP.IKOM",   "nama": "S2 Ilmu Komunikasi", "fak": "FISIP"},
            {"kode": "S2.FISIP.SOS",    "nama": "S2 Sosiologi", "fak": "FISIP"},
            {"kode": "S2.FISIP.ANT",    "nama": "S2 Antropologi", "fak": "FISIP"},
            {"kode": "S2.FISIP.IP",     "nama": "S2 Ilmu Politik", "fak": "FISIP"},
            {"kode": "S2.FISIP.IPEM",   "nama": "S2 Ilmu Pemerintahan", "fak": "FISIP"},
            {"kode": "S2.FISIP.AP",     "nama": "S2 Administrasi Publik", "fak": "FISIP"},
            {"kode": "S2.FISIP.HI",     "nama": "S2 Hubungan Internasional", "fak": "FISIP"},
            {"kode": "S3.FISIP.AP",     "nama": "S3 Administrasi Publik", "fak": "FISIP"},
            {"kode": "S3.FISIP.ANT",    "nama": "S3 Ilmu Antropologi", "fak": "FISIP"},
            {"kode": "S3.FISIP.IKOM",   "nama": "S3 Ilmu Komunikasi", "fak": "FISIP"},
            {"kode": "S3.FISIP.SOS",    "nama": "S3 Sosiologi", "fak": "FISIP"},
            {"kode": "S3.FISIP.IP",     "nama": "S3 Ilmu Politik", "fak": "FISIP"},

            # ─── FIB S1 missing + S2/S3 ─────────────────────────
            {"kode": "BMT",         "nama": "S1 Bahasa Mandarin dan Kebudayaan Tiongkok", "fak": "FIB"},
            {"kode": "PAR",         "nama": "S1 Pariwisata", "fak": "FIB"},
            {"kode": "S2.FIB.LNG",  "nama": "S2 Linguistik", "fak": "FIB"},
            {"kode": "S2.FIB.BE",   "nama": "S2 Bahasa Inggris", "fak": "FIB"},
            {"kode": "S2.FIB.BI",   "nama": "S2 Bahasa Indonesia", "fak": "FIB"},
            {"kode": "S2.FIB.ARK",  "nama": "S2 Arkeologi", "fak": "FIB"},
            {"kode": "S2.FIB.SEJ",  "nama": "S2 Sejarah", "fak": "FIB"},
            {"kode": "S2.FIB.KB",   "nama": "S2 Kajian Budaya", "fak": "FIB"},
            {"kode": "S3.FIB.LNG",  "nama": "S3 Linguistik", "fak": "FIB"},
            {"kode": "S3.FIB.BE",   "nama": "S3 Bahasa Inggris", "fak": "FIB"},
            {"kode": "S3.FIB.SI",   "nama": "S3 Sastra Indonesia", "fak": "FIB"},

            # ─── FPER S1 missing + S2 ───────────────────────────
            {"kode": "ITAN",            "nama": "S1 Ilmu Tanah", "fak": "FPER"},
            {"kode": "PTAN",            "nama": "S1 Proteksi Tanaman", "fak": "FPER"},
            {"kode": "S2.FPER.HPT",     "nama": "S2 Ilmu Hama dan Penyakit Tumbuhan", "fak": "FPER"},
            {"kode": "S2.FPER.AGT",     "nama": "S2 Agroteknologi", "fak": "FPER"},

            # ─── FIKP S1 missing + S2/S3 ────────────────────────
            {"kode": "AGBP",            "nama": "S1 Agrobisnis Perikanan", "fak": "FIKP"},
            {"kode": "THP",             "nama": "S1 Teknologi Hasil Perikanan", "fak": "FIKP"},
            {"kode": "S2.FIKP.IPER",    "nama": "S2 Ilmu Perikanan", "fak": "FIKP"},
            {"kode": "S2.FIKP.IKL",     "nama": "S2 Ilmu Kelautan", "fak": "FIKP"},
            {"kode": "S3.FIKP.IPER",    "nama": "S3 Ilmu Perikanan", "fak": "FIKP"},

            # ─── FPET S2/S3 ─────────────────────────────────────
            {"kode": "S2.FPET.ITP",     "nama": "S2 Ilmu dan Teknologi Peternakan", "fak": "FPET"},
            {"kode": "S3.FPET.PTR",     "nama": "S3 Peternakan", "fak": "FPET"},

            # ─── FHUT S1 missing + S2/S3 ────────────────────────
            {"kode": "RKHUT",           "nama": "S1 Rekayasa Kehutanan", "fak": "FHUT"},
            {"kode": "KHUT",            "nama": "S1 Konservasi Hutan", "fak": "FHUT"},
            {"kode": "S2.FHUT.HUT",     "nama": "S2 Kehutanan", "fak": "FHUT"},
            {"kode": "S3.FHUT.HUT",     "nama": "S3 Kehutanan", "fak": "FHUT"},

            # ─── FTP (Fakultas Teknologi Pertanian) ─────────────
            {"kode": "FTP.ITP",         "nama": "S1 Ilmu dan Teknologi Pangan", "fak": "FTP"},
            {"kode": "FTP.TPRT",        "nama": "S1 Teknik Pertanian", "fak": "FTP"},
            {"kode": "FTP.TIP",         "nama": "S1 Teknologi Industri Pertanian", "fak": "FTP"},
            {"kode": "S2.FTP.ITP",      "nama": "S2 Ilmu dan Teknologi Pangan", "fak": "FTP"},
            {"kode": "S2.FTP.KTP",      "nama": "S2 Keteknikan Pertanian", "fak": "FTP"},
            {"kode": "S2.FTP.TAI",      "nama": "S2 Teknik Agroindustri", "fak": "FTP"},

            # ─── SPS (Sekolah Pascasarjana) ──────────────────────
            {"kode": "SPS.SSP",         "nama": "S2 Sistem-Sistem Pertanian", "fak": "SPS"},
            {"kode": "SPS.PPW",         "nama": "S2 Perencanaan dan Pengembangan Wilayah", "fak": "SPS"},
            {"kode": "SPS.PLH",         "nama": "S2 Pengelolaan Lingkungan Hidup", "fak": "SPS"},
            {"kode": "SPS.AGB",         "nama": "S2 Agribisnis", "fak": "SPS"},
            {"kode": "SPS.MPK",         "nama": "S2 Manajemen Perkotaan", "fak": "SPS"},
            {"kode": "SPS.IBM",         "nama": "S2 Ilmu Biomedik", "fak": "SPS"},
            {"kode": "SPS.GND",         "nama": "S2 Jender dan Pembangunan", "fak": "SPS"},
            {"kode": "SPS.TPP",         "nama": "S2 Teknik Perencanaan Prasarana", "fak": "SPS"},
            {"kode": "SPS.TTR",         "nama": "S2 Teknik Transportasi", "fak": "SPS"},
            {"kode": "SPS.PST",         "nama": "S2 Pengelolaan Sumberdaya Pesisir Terpadu", "fak": "SPS"},
            {"kode": "SPS.IBD",         "nama": "S2 Ilmu Kebidanan", "fak": "SPS"},
            {"kode": "SPS.MB",          "nama": "S2 Manajemen Bencana", "fak": "SPS"},
            {"kode": "SPS.KRM",         "nama": "S2 Kriminologi", "fak": "SPS"},
            {"kode": "SPS.TBM",         "nama": "S2 Teknik Biomedik", "fak": "SPS"},
            {"kode": "S3.SPS.IPT",      "nama": "S3 Ilmu Pertanian", "fak": "SPS"},
            {"kode": "S3.SPS.SPB",      "nama": "S3 Studi Pembangunan", "fak": "SPS"},
            {"kode": "S3.SPS.ILH",      "nama": "S3 Ilmu Lingkungan", "fak": "SPS"},
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
