import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from app.config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Buat folder upload jika belum ada
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Login manager config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.mahasiswa import mahasiswa_bp
    from app.routes.staff import staff_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mahasiswa_bp, url_prefix='/mahasiswa')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Context processor: inject 'now' dan 'config' ke semua template
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return dict(now=datetime.utcnow(), config=app.config)

    # Import models agar Migrate mengenali
    with app.app_context():
        from app.models import user, fakultas, program_studi, bebas_pustaka  # noqa

    # Jalankan scheduler
    from app.utils.scheduler import start_scheduler
    start_scheduler(app)

    return app
