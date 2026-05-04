from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main_bp.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404
