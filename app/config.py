import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-ganti-di-produksi')

    # MySQL connection via PyMySQL
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'bebas_pustaka_db')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # 5MB

    # File Retention
    FILE_RETENTION_DAYS = int(os.environ.get('FILE_RETENTION_DAYS', 30))

    # Institusi
    NOMOR_SURAT_PREFIX = os.environ.get('NOMOR_SURAT_PREFIX', 'PERPUS')
    NAMA_INSTITUSI = os.environ.get('NAMA_INSTITUSI', 'Universitas Contoh')
    NAMA_PERPUSTAKAAN = os.environ.get('NAMA_PERPUSTAKAAN', 'UPT Perpustakaan')

    # WTF CSRF
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
