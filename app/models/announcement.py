# ABOUTME: Announcement model for team and general communications
# ABOUTME: Supports targeted team announcements with optional email delivery

from datetime import datetime
from flask_babel import gettext as _
from app import db


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)

    # Content
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    announcement_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: general, training, match, administrative

    # Targeting (null = all teams)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)

    # Email delivery
    send_email = db.Column(db.Boolean, default=False, nullable=False)
    email_sent_at = db.Column(db.DateTime)
    recipient_count = db.Column(db.Integer, default=0)

    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    team = db.relationship('Team', backref=db.backref('announcements', lazy='dynamic'))
    creator = db.relationship('User', backref=db.backref('announcements_created', lazy='dynamic'))

    def get_announcement_type_display(self):
        type_map = {
            'general': _('General'),
            'training': _('Training'),
            'match': _('Match'),
            'administrative': _('Administrative'),
        }
        return type_map.get(self.announcement_type, self.announcement_type)

    def __repr__(self):
        return f'<Announcement {self.subject}>'
