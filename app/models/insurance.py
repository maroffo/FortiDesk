# ABOUTME: Insurance policy model tracking sports, accident, and liability coverage per athlete
# ABOUTME: Tracks policy details, dates, amounts, and links to athletes via FK

from datetime import datetime, date
from flask_babel import gettext as _
from app import db


class Insurance(db.Model):
    __tablename__ = 'insurances'

    id = db.Column(db.Integer, primary_key=True)

    policy_number = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(200), nullable=False)
    insurance_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: sports, accident, civil_liability

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False, index=True)
    coverage_amount = db.Column(db.Numeric(10, 2))
    premium_amount = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)

    # Audit trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    athlete = db.relationship('Athlete', backref=db.backref('insurances', lazy=True))
    creator = db.relationship('User', backref='insurances_created')

    def get_insurance_type_display(self):
        types = {
            'sports': _('Sports'),
            'accident': _('Accident'),
            'civil_liability': _('Civil Liability'),
        }
        return types.get(self.insurance_type, self.insurance_type)

    def is_expired(self):
        return self.end_date < date.today()

    def days_until_expiry(self):
        return (self.end_date - date.today()).days

    def __repr__(self):
        return f'<Insurance {self.policy_number} ({self.insurance_type})>'
