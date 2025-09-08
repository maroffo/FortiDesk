from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from app import db, login_manager
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username_or_email = StringField('Username o Email', 
                                   validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', 
                           validators=[DataRequired()])
    remember_me = BooleanField('Ricordami')
    submit = SubmitField('Accedi')

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', 
                       validators=[DataRequired(), Email(), Length(max=120)])
    nome = StringField('Nome', 
                      validators=[DataRequired(), Length(max=100)])
    cognome = StringField('Cognome', 
                         validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', 
                           validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Conferma Password',
                             validators=[DataRequired(), EqualTo('password', message='Le password devono coincidere')])
    submit = SubmitField('Registrati')

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
            user.ultimo_accesso = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        
        flash('Credenziali non valide o account disattivato', 'danger')
    
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
            flash('Username o email già esistenti', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Crea nuovo utente
        user = User(
            username=form.username.data,
            email=form.email.data,
            nome=form.nome.data,
            cognome=form.cognome.data,
            ruolo='user'  # Ruolo di default
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrazione completata con successo!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Disconnessione effettuata', 'info')
    return redirect(url_for('auth.login'))