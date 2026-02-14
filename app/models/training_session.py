# ABOUTME: Training session model for scheduling team practices and events
# ABOUTME: Supports recurring sessions, cancellation, and links to attendance

from datetime import datetime, date
from flask_babel import gettext as _
from app import db


class TrainingSession(db.Model):
    """Training session scheduling for team practices, friendlies, tournaments, and events"""

    __tablename__ = 'training_sessions'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Session details
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200))
    session_type = db.Column(db.String(50), nullable=False, index=True)  # training, friendly, tournament, event

    # Foreign keys
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'))
    coach_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

    # Recurrence
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_day = db.Column(db.Integer)  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    recurrence_end_date = db.Column(db.Date)

    # Cancellation
    cancelled = db.Column(db.Boolean, default=False)
    cancellation_reason = db.Column(db.Text)

    # Notes
    notes = db.Column(db.Text)

    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_training_date_team', 'date', 'team_id'),
        db.Index('idx_training_season', 'season_id'),
    )

    # Relationships
    team = db.relationship('Team', backref=db.backref('training_sessions', lazy='dynamic'))
    coach = db.relationship('Staff', backref=db.backref('training_sessions_coached', lazy='dynamic'))
    creator = db.relationship('User', backref=db.backref('training_sessions_created', lazy='dynamic'))

    def __repr__(self):
        return f'<TrainingSession {self.title} ({self.date})>'

    def get_session_type_display(self):
        """Return localized session type display"""
        type_map = {
            'training': _('Training'),
            'friendly': _('Friendly Match'),
            'tournament': _('Tournament'),
            'event': _('Event')
        }
        return type_map.get(self.session_type, self.session_type)

    def is_past(self):
        """Check if the session date is in the past"""
        return self.date < date.today()

    def duration_minutes(self):
        """Calculate session duration in minutes"""
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        return int((end_dt - start_dt).total_seconds() / 60)
