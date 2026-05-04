# Product Requirements Document (PRD)
# Website Bebas Pustaka — Sistem Manajemen Surat Keterangan Bebas Pustaka

---

## 1. Informasi Dokumen

| Atribut | Detail |
|---|---|
| **Nama Produk** | Website Bebas Pustaka |
| **Versi** | 1.0.0 |
| **Status** | Draft |
| **Tanggal** | Mei 2026 |
| **Tipe** | Web Application |

---

## 2. Latar Belakang & Tujuan

Sistem Bebas Pustaka adalah aplikasi web yang memfasilitasi proses pengurusan surat keterangan bebas pustaka secara digital. Mahasiswa dapat mengajukan permohonan secara online, staff perpustakaan dapat meninjau dan memproses permohonan, serta admin dapat mengelola seluruh sistem.

### 2.1 Tujuan Utama

- Mendigitalisasi proses pengajuan dan penerbitan surat bebas pustaka
- Mempercepat proses verifikasi oleh staff
- Menyediakan surat bebas pustaka digital yang aman dan tidak dapat dimanipulasi
- Mengurangi penggunaan kertas dan kunjungan fisik ke perpustakaan

### 2.2 Ruang Lingkup

Sistem mencakup tiga jenis pengguna: **Mahasiswa**, **Staff**, dan **Admin**, masing-masing dengan hak akses dan fitur yang berbeda.

---

## 3. Halaman & Struktur Umum

### 3.1 Halaman Publik (Tanpa Login)

#### 3.1.1 Halaman Utama (`/`)

**Deskripsi:** Landing page yang menampilkan informasi umum tentang layanan bebas pustaka.

**Konten:**
- Header dengan logo institusi dan nama perpustakaan
- Hero section berisi deskripsi layanan bebas pustaka
- Tombol CTA: **"Ajukan Bebas Pustaka"** (redirect ke login jika belum login)
- Informasi persyaratan pengajuan (panduan singkat)
- Alur proses pengajuan (step-by-step visual)
- Informasi kontak perpustakaan
- Footer

**Fungsionalitas:**
- Tombol navigasi ke halaman Login dan Register
- Jika user sudah login, tombol CTA langsung mengarah ke dashboard sesuai peran

---

#### 3.1.2 Halaman Register (`/register`)

**Deskripsi:** Halaman pendaftaran akun baru khusus untuk Mahasiswa.

**Form Fields:**
| Field | Tipe | Validasi |
|---|---|---|
| NIM | Text | Wajib, unik, format numerik |
| Nama Lengkap | Text | Wajib, min 3 karakter |
| Email | Email | Wajib, format email valid, unik |
| Password | Password | Wajib, min 8 karakter |
| Konfirmasi Password | Password | Wajib, harus sama dengan password |
| Fakultas | Dropdown | Wajib |
| Program Studi | Dropdown | Wajib, dinamis berdasarkan fakultas |

**Fungsionalitas:**
- Validasi real-time pada setiap field
- Dropdown Program Studi otomatis berubah sesuai Fakultas yang dipilih
- Setelah register berhasil, akun berstatus aktif dan diarahkan ke halaman login
- Akun yang dibuat melalui register secara default berperan sebagai **Mahasiswa**
- Staff dan Admin hanya dapat dibuat oleh Admin

---

#### 3.1.3 Halaman Login (`/login`)

**Deskripsi:** Halaman autentikasi untuk semua jenis pengguna.

**Form Fields:**
| Field | Tipe | Validasi |
|---|---|---|
| Email / NIM | Text | Wajib |
| Password | Password | Wajib |

**Fungsionalitas:**
- Login menggunakan Email atau NIM
- Setelah login berhasil, sistem mengarahkan pengguna ke dashboard sesuai peran:
  - Mahasiswa → `/mahasiswa/dashboard`
  - Staff → `/staff/dashboard`
  - Admin → `/admin/dashboard`
- Fitur "Lupa Password" dengan verifikasi melalui email
- Proteksi terhadap brute force (maksimal 5 percobaan login, lalu dikunci sementara 15 menit)

---

## 4. Dashboard & Fitur per Peran Pengguna

---

### 4.1 Mahasiswa

#### 4.1.1 Dashboard Mahasiswa (`/mahasiswa/dashboard`)

**Tampilan:**
- Informasi profil mahasiswa (NIM, Nama, Fakultas, Prodi)
- Status pengajuan bebas pustaka terkini
- Riwayat pengajuan
- Tombol **"Ajukan Bebas Pustaka"** (hanya aktif jika belum ada pengajuan yang sedang diproses atau sudah disetujui dan masih aktif)

---

#### 4.1.2 Form Pengajuan Bebas Pustaka (`/mahasiswa/form-bebas-pustaka`)

**Deskripsi:** Form pengisian data untuk pengajuan surat bebas pustaka.

**Form Fields:**

| Field | Tipe | Keterangan |
|---|---|---|
| NIM | Text (auto-fill) | Diisi otomatis dari data akun, tidak dapat diubah |
| Nama Lengkap | Text (auto-fill) | Diisi otomatis dari data akun, tidak dapat diubah |
| Alamat | Textarea | Wajib diisi mahasiswa |
| Fakultas | Dropdown (auto-fill) | Diisi otomatis dari data akun |
| Program Studi | Dropdown (auto-fill) | Diisi otomatis dari data akun |
| File PDF Bebas Pustaka dari Fakultas | File Upload | Wajib, format PDF, maks 5MB |
| File PDF Kartu Mahasiswa | File Upload | Wajib, format PDF, maks 5MB |

**Validasi:**
- Semua field wajib diisi
- File hanya menerima format PDF
- Ukuran file masing-masing maksimal 5MB
- Mahasiswa hanya dapat mengajukan jika tidak ada pengajuan aktif yang sedang diproses

**Perilaku Setelah Submit:**
- Pengajuan masuk dengan status **"Menunggu Review"**
- Mahasiswa mendapat notifikasi bahwa pengajuan berhasil dikirim
- Mahasiswa diarahkan ke halaman status pengajuan

---

#### 4.1.3 Halaman Status Pengajuan (`/mahasiswa/status`)

**Tampilan:**
- Status terkini pengajuan (badge berwarna):
  - 🟡 **Menunggu Review** — pengajuan baru masuk
  - 🔵 **Sedang Diproses** — staff sedang memeriksa
  - ✅ **Disetujui** — pengajuan diterima
  - ❌ **Ditolak** — pengajuan ditolak beserta alasan
- Detail data yang diajukan
- Tanggal pengajuan

**Kondisi Tombol Cetak PDF:**

> **Aturan Kritis Keamanan:** Tombol cetak PDF hanya muncul apabila status pengajuan adalah **"Disetujui"**. Validasi dilakukan **sepenuhnya di sisi server**. Token satu kali pakai (signed token) diterbitkan dari server sebelum file PDF digenerate. Tidak ada data PDF yang disimpan di sisi klien. Manipulasi melalui browser inspect element tidak dapat menghasilkan PDF yang valid karena server memverifikasi token dan status dari database sebelum menerbitkan dokumen.

| Kondisi | Tampilan Tombol |
|---|---|
| Status bukan "Disetujui" | Tombol tidak ada / tersembunyi |
| Status "Disetujui", file masih dalam masa aktif (≤ 1 bulan) | Tombol **"Cetak Surat Bebas Pustaka"** aktif |
| Status "Disetujui", file sudah melewati 1 bulan | Tombol **"Cetak Ulang Surat Bebas Pustaka"** aktif |

**Alur Cetak PDF (Aman dari Manipulasi):**
1. Mahasiswa klik tombol cetak
2. Frontend mengirim request ke endpoint server: `POST /api/generate-pdf`
3. Server memverifikasi:
   - Session/token login valid
   - Status pengajuan di database = "Disetujui"
   - Mahasiswa yang request adalah pemilik pengajuan tersebut
4. Jika semua valid, server meng-generate PDF secara dinamis dan mengirimkan file ke browser
5. PDF dibuat on-demand dari data di database — tidak disimpan permanen di server

---

#### 4.1.4 Spesifikasi PDF Surat Bebas Pustaka

**Konten PDF:**

| Elemen | Sumber Data |
|---|---|
| Kop surat institusi / logo | Konfigurasi sistem |
| Nomor surat | Auto-generate dari server |
| Nama mahasiswa | Database |
| NIM | Database |
| Fakultas | Database |
| Program Studi | Database |
| Alamat | Database |
| Keterangan bebas pustaka | Template tetap |
| **Tanggal Diterbitkan** | **Tanggal staff menyetujui pengajuan (dari database)** |
| Tanda tangan digital / stempel (opsional) | Konfigurasi admin |

**Catatan Penting — Kebijakan File PDF Upload Mahasiswa:**

> File PDF yang diupload mahasiswa (bebas pustaka dari fakultas dan kartu mahasiswa) **hanya disimpan selama 1 bulan** sejak tanggal persetujuan. Setelah 1 bulan, file tersebut otomatis dihapus dari server untuk efisiensi penyimpanan.

> Namun, **surat bebas pustaka digital** yang dicetak mahasiswa **dapat digenerate ulang kapan saja** karena dibangun dari data di database (bukan dari file yang diupload). Mahasiswa yang kembali setelah lebih dari 1 bulan tetap dapat mencetak ulang suratnya.

---

### 4.2 Staff

#### 4.2.1 Dashboard Staff (`/staff/dashboard`)

**Tampilan:**
- Ringkasan statistik:
  - Jumlah pengajuan masuk hari ini
  - Jumlah pengajuan menunggu review
  - Jumlah pengajuan disetujui bulan ini
  - Jumlah pengajuan ditolak bulan ini
- Tabel daftar pengajuan terbaru

---

#### 4.2.2 Daftar Pengajuan Bebas Pustaka (`/staff/pengajuan`)

**Tampilan:**
- Tabel list semua pengajuan dengan kolom:
  - No.
  - NIM
  - Nama Mahasiswa
  - Fakultas
  - Program Studi
  - Tanggal Pengajuan
  - Status (badge berwarna)
  - Aksi (Lihat Detail)
- Filter berdasarkan: Status, Fakultas, Tanggal
- Search berdasarkan NIM atau Nama
- Pagination

---

#### 4.2.3 Detail Pengajuan (`/staff/pengajuan/:id`)

**Tampilan:**
- Data lengkap mahasiswa pemohon
- Data form yang diajukan
- **Preview / Download File PDF yang diupload mahasiswa:**

  > **Penanganan File yang Sudah Dihapus (>1 Bulan):**
  > Jika file PDF sudah melewati masa simpan 1 bulan dan telah dihapus dari server, ketika staff mengklik tombol lihat PDF, sistem **tidak akan error**. Sistem akan menampilkan **modal/pop-up** dengan pesan:
  >
  > *"File PDF ini telah dihapus dari sistem karena telah melewati masa penyimpanan 1 bulan. Surat bebas pustaka mahasiswa yang bersangkutan tetap dapat dicetak ulang oleh mahasiswa."*

- Tombol aksi:
  - ✅ **Setujui** — mengubah status menjadi "Disetujui", mencatat tanggal persetujuan di database
  - ❌ **Tolak** — menampilkan form untuk mengisi alasan penolakan, mengubah status menjadi "Ditolak"
  - ✏️ **Edit** — mengedit data pengajuan (NIM, Nama, Alamat, Fakultas, Prodi) jika ada kesalahan data; file PDF tidak dapat diedit oleh staff

**Alur Persetujuan:**
1. Staff klik **"Setujui"**
2. Muncul konfirmasi: *"Apakah Anda yakin ingin menyetujui pengajuan bebas pustaka atas nama [Nama Mahasiswa]?"*
3. Jika dikonfirmasi, sistem:
   - Mengubah status menjadi **"Disetujui"**
   - Mencatat `approved_at` = timestamp saat ini di database
   - Mengirim notifikasi ke mahasiswa
4. Mahasiswa sekarang dapat mencetak surat bebas pustakanya

**Alur Penolakan:**
1. Staff klik **"Tolak"**
2. Muncul modal berisi textarea untuk mengisi alasan penolakan (wajib diisi)
3. Jika dikonfirmasi, status berubah menjadi **"Ditolak"**
4. Alasan penolakan tercatat dan tampil di status mahasiswa

---

### 4.3 Admin

#### 4.3.1 Dashboard Admin (`/admin/dashboard`)

**Tampilan:**
- Statistik keseluruhan sistem:
  - Total pengguna (Mahasiswa, Staff)
  - Total pengajuan (per status)
  - Grafik pengajuan per bulan
  - Pengajuan terbaru

---

#### 4.3.2 Manajemen Pengguna (`/admin/users`)

**Fungsionalitas CRUD:**

**a. Daftar Pengguna:**
- Tabel semua pengguna dengan kolom: No., Nama, Email/NIM, Peran, Status Akun, Tanggal Dibuat, Aksi
- Filter berdasarkan peran (Mahasiswa / Staff / Admin)
- Search berdasarkan nama atau email/NIM

**b. Tambah Pengguna:**
- Admin dapat menambahkan pengguna baru dengan peran apa pun (Mahasiswa, Staff, Admin)
- Form: Nama, Email, NIM (untuk Mahasiswa), Password sementara, Peran, Fakultas (untuk Mahasiswa), Prodi (untuk Mahasiswa)

**c. Edit Pengguna:**
- Admin dapat mengubah data pengguna: Nama, Email, Peran, Status Akun
- Password dapat di-reset oleh admin

**d. Nonaktifkan / Aktifkan Akun:**
- Admin dapat menonaktifkan akun (soft delete) tanpa menghapus data
- Pengguna yang dinonaktifkan tidak dapat login

**e. Hapus Pengguna:**
- Hard delete dengan konfirmasi
- Hanya dapat dilakukan jika pengguna tidak memiliki data pengajuan aktif

---

#### 4.3.3 Pemantauan Pengajuan (`/admin/pengajuan`)

- Melihat semua pengajuan dari semua mahasiswa (read-only dengan filter lengkap)
- Export data ke format Excel/CSV

---

#### 4.3.4 Manajemen Referensi (`/admin/referensi`)

- CRUD data Fakultas
- CRUD data Program Studi (relasi ke Fakultas)

---

#### 4.3.5 Pengaturan Sistem (`/admin/settings`)

- Konfigurasi nama institusi
- Konfigurasi logo yang tampil di PDF surat
- Konfigurasi durasi masa simpan file upload (default: 1 bulan)
- Konfigurasi template nomor surat

---

## 5. Logika Bisnis & Aturan Sistem

### 5.1 Siklus Hidup Pengajuan

```
[Mahasiswa Submit] 
      ↓
[Status: Menunggu Review]
      ↓
[Staff Tinjau]
      ↓
   ┌──────────────────────┐
   ↓                      ↓
[Disetujui]           [Ditolak]
   ↓                      ↓
[Mahasiswa bisa      [Mahasiswa bisa
 cetak PDF]           ajukan ulang]
```

### 5.2 Aturan Pengajuan Ulang

| Kondisi | Boleh Ajukan Ulang? |
|---|---|
| Status: Menunggu Review | ❌ Tidak |
| Status: Sedang Diproses | ❌ Tidak |
| Status: Disetujui (aktif) | ❌ Tidak |
| Status: Ditolak | ✅ Ya |
| Status: Disetujui + lebih dari 1 bulan (file terhapus) | ✅ Ya, dan **dapat cetak ulang** tanpa ajukan ulang |

### 5.3 Manajemen File Upload Mahasiswa

**Penyimpanan:**
- File PDF yang diupload mahasiswa disimpan di server dengan path terstruktur: `/uploads/{tahun}/{bulan}/{pengajuan_id}/`
- Nama file di-hash untuk keamanan

**Penghapusan Otomatis:**
- Scheduler (cron job) berjalan setiap hari pada pukul 02.00
- File dihapus jika: `(tanggal_sekarang - approved_at) > 30 hari`
- Status file di database diupdate menjadi `file_deleted = true`
- File surat bebas pustaka (PDF yang digenerate) **tidak pernah disimpan** — selalu dibuat on-demand

**Penanganan Akses File yang Sudah Dihapus:**
- Database menyimpan kolom `file_deleted` (boolean) dan `file_deleted_at` (timestamp)
- Ketika staff membuka detail pengajuan dan file sudah dihapus:
  - Sistem mengecek kolom `file_deleted` sebelum mencoba membuka file
  - Jika `file_deleted = true`, tampilkan modal: *"File PDF telah dihapus dari sistem karena telah melewati masa penyimpanan 1 bulan."*
  - **Tidak ada error 404 atau crash** — sistem gracefully menangani kondisi ini

### 5.4 Keamanan Cetak PDF Surat Bebas Pustaka

**Mekanisme Server-Side Only:**

1. Frontend hanya menampilkan tombol cetak — tidak menyimpan data PDF
2. Klik tombol → request ke `POST /api/bebas-pustaka/generate-pdf`
3. Server melakukan validasi:
   ```
   - Apakah user sudah login? (cek session/JWT)
   - Apakah user adalah pemilik pengajuan? (cek user_id vs pengajuan.mahasiswa_id)
   - Apakah status pengajuan di database = "Disetujui"? (bukan dari request body)
   ```
4. Jika lolos validasi → server generate PDF dari template + data database → kirim sebagai response binary
5. Jika gagal validasi → server return 403 Forbidden

**Mengapa Tidak Bisa Dimanipulasi via Inspect Element:**
- PDF tidak dihasilkan oleh JavaScript di browser
- Tidak ada URL publik yang bisa langsung diakses untuk mendapatkan PDF
- Endpoint generate-pdf memerlukan autentikasi aktif dan validasi dari database
- Mengubah HTML/JS di browser tidak bisa mengubah data di database

---

## 6. Struktur Database (Ringkasan)

### Tabel Utama

**users**
- id, nim, nama, email, password_hash, peran (mahasiswa/staff/admin), fakultas_id, prodi_id, status_akun, created_at, updated_at

**fakultas**
- id, nama_fakultas, kode_fakultas

**program_studi**
- id, nama_prodi, kode_prodi, fakultas_id

**pengajuan_bebas_pustaka**
- id, mahasiswa_id (FK users), nim, nama, alamat, fakultas_id, prodi_id
- file_bebas_pustaka_path, file_kartu_mahasiswa_path
- file_deleted (boolean, default false), file_deleted_at
- status (menunggu_review / sedang_diproses / disetujui / ditolak)
- catatan_penolakan (nullable)
- reviewed_by (FK users, staff yang memproses)
- approved_at (nullable, timestamp saat disetujui — digunakan sebagai tanggal terbit di PDF)
- created_at, updated_at

---

## 7. Spesifikasi Teknis

| Komponen | Teknologi yang Digunakan |
|---|---|
| **Frontend** | HTML, CSS, JavaScript, Jinja2 (Flask Templating Engine) |
| **Backend** | Python — Flask |
| **ORM** | Flask-SQLAlchemy |
| **Database** | MySQL |
| **File Storage** | Local server (`/uploads/`) |
| **PDF Generator** | WeasyPrint / ReportLab / xhtml2pdf |
| **Autentikasi** | Flask-Login + Flask-Bcrypt (session-based) |
| **Scheduler** | APScheduler / Flask-APScheduler |
| **Notifikasi** | Email via SMTP menggunakan Flask-Mail |
| **Migrasi Database** | Flask-Migrate (Alembic) |
| **Form Handling** | Flask-WTF (WTForms) |

---

## 8. Alur Penggunaan (User Flow)

### 8.1 Alur Mahasiswa (Pertama Kali)

```
Register → Login → Dashboard → Klik "Ajukan" → Isi Form → 
Submit → Menunggu Review → Staff Setujui → 
Notifikasi Email → Login → Status = Disetujui → 
Klik "Cetak Surat" → PDF terdownload
```

### 8.2 Alur Mahasiswa (Lebih dari 1 Bulan Kemudian)

```
Login → Dashboard → Status = Disetujui (file lama terhapus) → 
Klik "Cetak Ulang Surat" → Server generate PDF dari database → 
PDF terdownload (tanggal terbit = tanggal disetujui dulu)
```

### 8.3 Alur Staff Menyetujui

```
Login → Dashboard → Daftar Pengajuan → Klik Detail → 
Review Data & PDF Upload → Klik "Setujui" → 
Konfirmasi → Status diupdate → Mahasiswa dinotifikasi
```

### 8.4 Alur Staff Melihat File yang Sudah Dihapus

```
Login → Daftar Pengajuan → Klik Detail → 
Klik "Lihat PDF Bebas Pustaka dari Fakultas" → 
[File sudah dihapus] → Muncul pop-up: 
"File PDF telah dihapus dari sistem karena telah melewati 
masa penyimpanan 1 bulan."
```

---

## 9. Kebutuhan Non-Fungsional

| Aspek | Kebutuhan |
|---|---|
| **Keamanan** | HTTPS wajib, validasi server-side untuk semua aksi sensitif, proteksi CSRF, sanitasi input |
| **Performa** | Halaman utama load < 3 detik, generate PDF < 5 detik |
| **Ketersediaan** | Uptime 99% pada jam kerja (07.00–17.00) |
| **Responsif** | Tampilan optimal di desktop dan mobile |
| **Aksesibilitas** | Mendukung pembaca layar dasar |
| **Audit Log** | Semua aksi staff dan admin tercatat (siapa, kapan, apa) |

---

## 10. Batasan & Asumsi

- Satu mahasiswa hanya dapat memiliki satu pengajuan aktif dalam satu waktu
- Mahasiswa mendaftar sendiri; staff dan admin dibuat oleh admin
- Nomor surat bebas pustaka di-generate otomatis oleh sistem
- Sistem tidak terintegrasi dengan sistem akademik kampus secara real-time (data diisi manual oleh mahasiswa)
- Notifikasi email diasumsikan tersedia melalui SMTP kampus atau layanan pihak ketiga

---

## 11. Perkiraan Model

from datetime import datetime
from . import db  # sesuaikan import-mu

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(20), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('admin', 'staff', 'mahasiswa', name='user_roles'),
        nullable=False
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # ← tambahan
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relasi
    submissions = db.relationship(
        'BebasPustaka',
        foreign_keys='BebasPustaka.user_id',
        backref='user',
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.email}>"


class BebasPustaka(db.Model):
    __tablename__ = 'bebas_pustaka'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    nim = db.Column(db.String(20), nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    fakultas = db.Column(db.String(100), nullable=False)
    prodi = db.Column(db.String(100), nullable=False)

    file_bebas_pustaka = db.Column(db.String(255), nullable=True)
    file_kartu_mahasiswa = db.Column(db.String(255), nullable=True)
    file_deleted = db.Column(db.Boolean, default=False, nullable=False)      # ← tambahan
    file_deleted_at = db.Column(db.DateTime, nullable=True)                  # ← tambahan

    status = db.Column(
        db.Enum('pending', 'approved', 'rejected', name='status_enum'),
        default='pending',
        nullable=False
    )
    catatan_penolakan = db.Column(db.Text, nullable=True)                    # ← tambahan
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # ← tambahan

    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(                                                  # ← tambahan
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # relasi ke reviewer (staff/admin yang memproses)
    reviewer = db.relationship(                                              # ← tambahan
        'User',
        foreign_keys=[reviewed_by],
        backref='reviewed_submissions'
    )

    def is_file_available(self):
        if self.file_deleted:
            return False
        if not self.approved_at:
            return True
        return (datetime.utcnow() - self.approved_at).days <= 30

    def __repr__(self):
        return f"<BebasPustaka {self.nim} - {self.status}>"

*Dokumen ini dapat diperbarui seiring perkembangan kebutuhan. Versi terbaru selalu menjadi acuan pengembangan.*
