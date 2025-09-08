from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    ruolo = db.Column(db.String(50), nullable=False, default='user')  # admin, allenatore, genitore, giocatore
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_accesso = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash e salva la password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica se la password è corretta"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_nome_completo(self):
        """Restituisce il nome completo"""
        return f"{self.nome} {self.cognome}"
    
    def is_admin(self):
        """Verifica se l'utente è un amministratore"""
        return self.ruolo == 'admin'
    
    def is_allenatore(self):
        """Verifica se l'utente è un allenatore"""
        return self.ruolo == 'allenatore'
    
    def __repr__(self):
        return f'<User {self.username}>'