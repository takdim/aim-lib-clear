import re

# // ASVS 6.2.4: Blacklist kata sandi populer yang sangat mudah ditebak
COMMON_PASSWORDS = {
    'password', 'password123', '12345678', '123456789', 'qwertyui',
    'admin123', 'admin@123', 'unhas123', 'mahasiswa', 'mahasiswa123',
    'bebaspustaka', 'perpustakaan', 'rahasia123', 'iloveyou'
}


def is_valid_pdf(file_storage):
    """
    Validasi file upload agar benar-benar file PDF valid.
    Mengecek ekstensi .pdf serta signature magic bytes (%PDF-).
    // ASVS 5.2.2: Extension and magic bytes verification
    """
    if not file_storage or not getattr(file_storage, 'filename', None):
        return False

    filename = file_storage.filename
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() != 'pdf':
        return False

    try:
        header = file_storage.read(5)
        file_storage.seek(0)
        return header == b'%PDF-'
    except Exception:
        return False


def validate_password_strength(password: str, user_context: dict = None) -> list[str]:
    """
    Validasi kekuatan kata sandi pengguna sesuai pedoman OWASP ASVS V6.2.
    // ASVS 6.2.1: Panjang minimal 8 karakter.
    // ASVS 6.2.4: Pemeriksaan terhadap daftar kata sandi umum / rentan ditebak.
    // ASVS 6.2.11: Penolakan kata sandi yang memuat konteks spesifik pengguna (NIM/nama/email).
    """
    errors = []
    if not password:
        return ['Password wajib diisi.']

    # // ASVS 6.2.1: Minimal 8 karakter
    if len(password) < 8:
        errors.append('Password minimal 8 karakter.')

    # // ASVS 6.2.4: Blacklist common passwords
    if password.lower() in COMMON_PASSWORDS:
        errors.append('Password terlalu umum dan mudah ditebak. Harap gunakan password lain.')

    # Validasi keberagaman karakter (huruf dan angka/simbol)
    has_letter = bool(re.search(r'[A-Za-z]', password))
    has_digit_or_symbol = bool(re.search(r'[\d\W_]', password))
    if not (has_letter and has_digit_or_symbol):
        errors.append('Password harus memuat kombinasi huruf dan angka atau simbol.')

    # // ASVS 6.2.11: Pengecekan konteks spesifik
    if user_context:
        nim = (user_context.get('nim') or '').strip().lower()
        email = (user_context.get('email') or '').strip().lower()
        name = (user_context.get('name') or '').strip().lower()

        lower_pw = password.lower()
        if nim and len(nim) >= 4 and nim in lower_pw:
            errors.append('Password tidak boleh memuat NIM Anda.')
        if email and email.split('@')[0] in lower_pw:
            errors.append('Password tidak boleh memuat bagian awal email Anda.')
        if name and len(name) >= 4 and name in lower_pw:
            errors.append('Password tidak boleh memuat nama Anda.')

    return errors
