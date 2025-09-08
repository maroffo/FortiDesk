from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Genitore(db.Model):
    __tablename__ = 'genitori'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dati anagrafici
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    
    # Contatti
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    
    # Tipo di genitore
    tipo_genitore = db.Column(db.String(10), nullable=False)  # 'padre' o 'madre' o 'tutore'
    
    # Relazione con il bambino
    bambino_id = db.Column(db.Integer, db.ForeignKey('bambini.id'), nullable=False)
    
    # Metadati
    data_inserimento = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_modifica = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def get_nome_completo(self):
        """Restituisce nome e cognome completo"""
        return f"{self.nome} {self.cognome}"
    
    def get_tipo_genitore_display(self):
        """Restituisce il tipo di genitore formattato"""
        mapping = {
            'padre': 'Padre',
            'madre': 'Madre', 
            'tutore': 'Tutore/Tutrice'
        }
        return mapping.get(self.tipo_genitore, self.tipo_genitore.title())
    
    def __repr__(self):
        return f'<Genitore {self.get_nome_completo()} ({self.get_tipo_genitore_display()})>'