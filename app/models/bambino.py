from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from app import db

class Bambino(db.Model):
    __tablename__ = 'bambini'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dati anagrafici
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    data_nascita = db.Column(db.Date, nullable=False)
    luogo_nascita = db.Column(db.String(100), nullable=False)
    codice_fiscale = db.Column(db.String(16), unique=True, nullable=False, index=True)
    
    # Indirizzo di residenza
    indirizzo_via = db.Column(db.String(200), nullable=False)
    indirizzo_civico = db.Column(db.String(10), nullable=False)
    indirizzo_cap = db.Column(db.String(5), nullable=False)
    indirizzo_comune = db.Column(db.String(100), nullable=False)
    indirizzo_provincia = db.Column(db.String(2), nullable=False)
    
    # Documento di identità
    numero_documento = db.Column(db.String(50), nullable=False)
    ente_emettitore = db.Column(db.String(100), nullable=False)
    scadenza_documento = db.Column(db.Date, nullable=False)
    
    # Certificato medico/libretto sportivo
    ha_certificato_medico = db.Column(db.Boolean, default=False, nullable=False)
    tipo_certificato = db.Column(db.String(50), nullable=True)  # 'medico' o 'libretto_sportivo'
    scadenza_certificato = db.Column(db.Date, nullable=True)
    
    # Metadati
    data_inserimento = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    inserito_da = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relazioni
    genitori = db.relationship('Genitore', backref='figlio', lazy=True, cascade='all, delete-orphan')
    inserito_da_user = db.relationship('User', backref='bambini_inseriti')
    
    def get_nome_completo(self):
        """Restituisce nome e cognome completo"""
        return f"{self.nome} {self.cognome}"
    
    def get_eta(self):
        """Calcola l'età del bambino"""
        today = date.today()
        return today.year - self.data_nascita.year - ((today.month, today.day) < (self.data_nascita.month, self.data_nascita.day))
    
    def get_indirizzo_completo(self):
        """Restituisce l'indirizzo completo formattato"""
        return f"{self.indirizzo_via} {self.indirizzo_civico}, {self.indirizzo_cap} {self.indirizzo_comune} ({self.indirizzo_provincia})"
    
    def is_certificato_scaduto(self):
        """Verifica se il certificato medico è scaduto"""
        if not self.ha_certificato_medico or not self.scadenza_certificato:
            return True
        return self.scadenza_certificato < date.today()
    
    def is_documento_scaduto(self):
        """Verifica se il documento è scaduto"""
        return self.scadenza_documento < date.today()
    
    def giorni_scadenza_certificato(self):
        """Restituisce i giorni rimanenti alla scadenza del certificato"""
        if not self.scadenza_certificato:
            return None
        return (self.scadenza_certificato - date.today()).days
    
    def giorni_scadenza_documento(self):
        """Restituisce i giorni rimanenti alla scadenza del documento"""
        return (self.scadenza_documento - date.today()).days
    
    def __repr__(self):
        return f'<Bambino {self.get_nome_completo()}>'