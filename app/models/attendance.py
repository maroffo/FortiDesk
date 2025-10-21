from datetime import datetime
from app import db


class Attendance(db.Model):
    """Attendance tracking for athletes at training sessions, matches, and events"""

    __tablename__ = 'attendance'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Attendance details
    date = db.Column(db.Date, nullable=False, index=True)
    session_type = db.Column(db.String(50), nullable=False)  # training, match, event
    status = db.Column(db.String(20), nullable=False)  # present, absent, excused, late
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    athlete = db.relationship('Athlete', backref=db.backref('attendance_records', lazy='dynamic'))
    creator = db.relationship('User', backref=db.backref('attendance_created', lazy='dynamic'))

    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_attendance_athlete_date', 'athlete_id', 'date'),
        db.Index('idx_attendance_date_session', 'date', 'session_type'),
    )

    def __repr__(self):
        return f'<Attendance {self.athlete.get_full_name()} - {self.date} - {self.status}>'

    def get_status_display(self):
        """Return localized status display"""
        status_map = {
            'present': 'Present',
            'absent': 'Absent',
            'excused': 'Excused',
            'late': 'Late'
        }
        return status_map.get(self.status, self.status)

    def get_session_type_display(self):
        """Return localized session type display"""
        type_map = {
            'training': 'Training',
            'match': 'Match',
            'event': 'Event'
        }
        return type_map.get(self.session_type, self.session_type)
