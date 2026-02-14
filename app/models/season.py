# ABOUTME: Season model for organizing team activities by sporting year
# ABOUTME: Tracks season dates, current status, and related teams/sessions

from datetime import datetime, date
from app import db


class Season(db.Model):
    """Sporting season for organizing team activities by year"""

    __tablename__ = 'seasons'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Season details
    name = db.Column(db.String(20), nullable=False, unique=True, index=True)  # e.g. "2025-2026"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)

    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    creator = db.relationship('User', backref=db.backref('seasons_created', lazy='dynamic'))
    teams = db.relationship('Team', backref='season_ref', lazy='dynamic')
    training_sessions = db.relationship('TrainingSession', backref='season', lazy='dynamic')

    def __repr__(self):
        return f'<Season {self.name}>'

    def is_ongoing(self):
        """Check if the season is currently active based on dates"""
        return self.start_date <= date.today() <= self.end_date

    def days_remaining(self):
        """Return number of days remaining in the season, or 0 if not ongoing"""
        if self.is_ongoing():
            return (self.end_date - date.today()).days
        return 0
