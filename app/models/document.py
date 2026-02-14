# ABOUTME: Document model for tracking uploaded files (certificates, IDs, insurance, etc.)
# ABOUTME: Polymorphic design with entity_type/entity_id for athlete and staff documents

from datetime import datetime, date
from flask_babel import gettext as _
from app import db


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)

    # Document info
    title = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: medical_certificate, id_document, background_check, insurance, consent_form, other

    # File info
    file_path = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    file_size = db.Column(db.Integer)  # bytes
    mime_type = db.Column(db.String(100))

    # Polymorphic owner
    entity_type = db.Column(db.String(20), nullable=False, index=True)  # 'athlete' or 'staff'
    entity_id = db.Column(db.Integer, nullable=False, index=True)

    # Expiry tracking
    expiry_date = db.Column(db.Date)
    reminder_sent = db.Column(db.Boolean, default=False, nullable=False)

    # Notes
    notes = db.Column(db.Text)

    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (
        db.Index('idx_document_entity', 'entity_type', 'entity_id'),
    )

    # Relationships
    creator = db.relationship('User', backref=db.backref('documents_created', lazy='dynamic'))

    def get_document_type_display(self):
        type_map = {
            'medical_certificate': _('Medical Certificate'),
            'id_document': _('ID Document'),
            'background_check': _('Background Check'),
            'insurance': _('Insurance'),
            'consent_form': _('Consent Form'),
            'other': _('Other'),
        }
        return type_map.get(self.document_type, self.document_type)

    def is_expired(self):
        if not self.expiry_date:
            return False
        return self.expiry_date < date.today()

    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days

    def __repr__(self):
        return f'<Document {self.title} ({self.entity_type}:{self.entity_id})>'
