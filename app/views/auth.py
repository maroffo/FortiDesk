from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_babel import lazy_gettext as _l, gettext as _
from app import db, login_manager
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username_or_email = StringField(_l('Username o Email'),
                                   validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField(_l('Password'),
                           validators=[DataRequired()])
    remember_me = BooleanField(_l('Ricordami'))
    submit = SubmitField(_l('Accedi'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'),
                          validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField(_l('Email'),
                       validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField(_l('First Name'),
                      validators=[DataRequired(), Length(max=100)])
    last_name = StringField(_l('Last Name'),
                         validators=[DataRequired(), Length(max=100)])
    password = PasswordField(_l('Password'),
                           validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(_l('Confirm Password'),
                             validators=[DataRequired(), EqualTo('password', message=_l('Passwords must match'))])
    submit = SubmitField(_l('Register'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username_or_email = form.username_or_email.data
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        
        flash(_('Credenziali non valide o account disattivato'), 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verifica se username o email esistono già
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash(_('Username o email già esistenti'), 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='user'  # Default role
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(_('Registrazione completata con successo!'), 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Disconnessione effettuata'), 'info')
    return redirect(url_for('auth.login'))