import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-ganti-di-produksi')
    APP_NAME = 'SIBESTI'
    APP_TAGLINE = 'Sistem Informasi Bebas Pustaka Terintegrasi'

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
    PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', '').rstrip('/')

    # WTF CSRF
    WTF_CSRF_ENABLED = True

    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ('1', 'true', 'yes')
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'https')

    # Rate Limiting (Flask-Limiter)
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'true').lower() in ('1', 'true', 'yes')

    # Security Headers Config
    HSTS_ENABLED = os.environ.get('HSTS_ENABLED', 'true').lower() in ('1', 'true', 'yes')

    # INLISLite integration
    INLISLITE_ENABLED = os.environ.get('INLISLITE_ENABLED', 'true').lower() in ('1', 'true', 'yes')
    INLISLITE_BASE_URL = os.environ.get('INLISLITE_BASE_URL', '').rstrip('/')
    INLISLITE_LOGIN_URL = os.environ.get('INLISLITE_LOGIN_URL', '').strip()
    INLISLITE_USERNAME = os.environ.get('INLISLITE_USERNAME', '').strip()
    INLISLITE_PASSWORD = os.environ.get('INLISLITE_PASSWORD', '').strip()
    INLISLITE_TIMEOUT = int(os.environ.get('INLISLITE_TIMEOUT', 20))
    INLISLITE_SESSION_TTL = int(os.environ.get('INLISLITE_SESSION_TTL', 900))
    INLISLITE_MEMBER_CACHE_TTL = int(os.environ.get('INLISLITE_MEMBER_CACHE_TTL', 300))


class DevelopmentConfig(Config):
    DEBUG = True
    # Di development lokal tanpa HTTPS, cookie secure dinonaktifkan kecuali disetel True via env
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ('1', 'true', 'yes')


class ProductionConfig(Config):
    DEBUG = False
    # Di environment production, defaultkan ke Secure=True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() in ('1', 'true', 'yes')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
