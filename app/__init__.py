# ABOUTME: Flask application factory with extensions, locale selection, and error handlers
# ABOUTME: Registers all blueprints and configures Babel, SQLAlchemy, and Flask-Login
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, lazy_gettext as _l
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()

def get_locale():
    """Determine the best locale based on user preference or browser settings"""
    # Check if user has set a language preference in session
    if 'language' in session:
        return session['language']
    # Otherwise, try to guess the language from the browser settings
    return request.accept_languages.best_match(['en', 'it']) or 'en'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configure logging
    import logging
    from logging.handlers import RotatingFileHandler
    import os

    if not app.debug and not app.testing:
        log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/fortidesk.log'))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/fortidesk.log'),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        app.logger.info('FortiDesk startup')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = _l('You must be logged in to access this page.')
    login_manager.login_message_category = 'info'

    # Initialize Babel
    babel.init_app(app, locale_selector=get_locale)

    # Call init_app if the config class defines it (e.g. production safety checks)
    config_class = config[config_name]
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.athletes import athletes_bp
    from app.views.staff import staff_bp
    from app.views.attendance import attendance_bp
    from app.views.equipment import equipment_bp
    from app.views.teams import teams_bp
    from app.views.admin import admin_bp
    from app.views.seasons import seasons_bp
    from app.views.training import training_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(athletes_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(seasons_bp)
    app.register_blueprint(training_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app