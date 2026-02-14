from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
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

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'You must be logged in to access this page.'
    login_manager.login_message_category = 'info'

    # Initialize Babel
    babel.init_app(app, locale_selector=get_locale)

    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.athletes import athletes_bp
    from app.views.staff import staff_bp
    from app.views.attendance import attendance_bp
    from app.views.equipment import equipment_bp
    from app.views.teams import teams_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(athletes_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(teams_bp)

    return app