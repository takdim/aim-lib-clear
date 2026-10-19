def is_valid_pdf(file_storage):
    """
    Validasi file upload agar benar-benar file PDF valid.
    Mengecek ekstensi .pdf serta signature magic bytes (%PDF-).
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
