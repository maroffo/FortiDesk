# ABOUTME: Emergency contact model for athlete emergency and medical contacts
# ABOUTME: Tracks doctors, relatives, and other contacts with medical notes

from datetime import datetime
from flask_babel import gettext as _
from app import db


class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'

    id = db.Column(db.Integer, primary_key=True)

    # Owner
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False, index=True)

    # Contact info
    contact_name = db.Column(db.String(200), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)  # doctor, relative, other
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))

    # Medical specific
    is_primary_doctor = db.Column(db.Boolean, default=False, nullable=False)
    medical_notes = db.Column(db.Text)  # allergies, conditions, etc.

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    athlete = db.relationship('Athlete', backref=db.backref('emergency_contacts', lazy=True))

    def get_relationship_display(self):
        rel_map = {
            'doctor': _('Doctor'),
            'relative': _('Relative'),
            'other': _('Other'),
        }
        return rel_map.get(self.relationship, self.relationship)

    def __repr__(self):
        return f'<EmergencyContact {self.contact_name} for Athlete #{self.athlete_id}>'
