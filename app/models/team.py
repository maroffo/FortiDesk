from datetime import datetime
from app import db


class Team(db.Model):
    """Teams/Squads for organizing athletes by age group or level"""

    __tablename__ = 'teams'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Team details
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)  # e.g. "Prime Mete", "Under 6"
    description = db.Column(db.Text)
    age_group = db.Column(db.String(50))  # e.g. "U6", "U8", "U10"
    season = db.Column(db.String(20))  # e.g. "2024-2025"

    # Head Coach (one-to-one with Staff)
    head_coach_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    head_coach = db.relationship('Staff', foreign_keys=[head_coach_id],
                                 backref=db.backref('teams_as_head_coach', lazy='dynamic'))
    creator = db.relationship('User', backref=db.backref('teams_created', lazy='dynamic'))
    athletes = db.relationship('Athlete', backref='team', lazy='dynamic')
    staff_assignments = db.relationship('TeamStaffAssignment', backref='team', lazy='dynamic',
                                        cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Team {self.name}>'

    def get_assistant_coaches(self):
        """Get all assistant coaches assigned to this team"""
        return [a.staff for a in self.staff_assignments.filter_by(
            role='assistant_coach', is_active=True
        ).all()]

    def get_escorts(self):
        """Get all escorts/accompaniers assigned to this team"""
        return [a.staff for a in self.staff_assignments.filter_by(
            role='escort', is_active=True
        ).all()]

    def get_all_staff(self):
        """Get all staff members (head coach + assistants + escorts)"""
        staff = []
        if self.head_coach:
            staff.append(self.head_coach)
        staff.extend(self.get_assistant_coaches())
        staff.extend(self.get_escorts())
        return staff

    def get_athlete_count(self):
        """Get number of athletes in team"""
        return self.athletes.filter_by(is_active=True).count()


class TeamStaffAssignment(db.Model):
    """Many-to-many relationship between teams and staff (assistant coaches, escorts)"""

    __tablename__ = 'team_staff_assignments'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)

    # Role in team
    role = db.Column(db.String(50), nullable=False)  # assistant_coach, escort

    # Assignment details
    assigned_date = db.Column(db.Date, nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Notes
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    staff = db.relationship('Staff', backref=db.backref('team_assignments', lazy='dynamic'))
    assigner = db.relationship('User', backref=db.backref('team_staff_assignments_made', lazy='dynamic'))

    # Unique constraint: same staff can't have same role in same team
    __table_args__ = (
        db.Index('idx_team_staff', 'team_id', 'staff_id', 'role'),
        db.UniqueConstraint('team_id', 'staff_id', 'role', name='uq_team_staff_role'),
    )

    def __repr__(self):
        return f'<TeamStaffAssignment {self.staff.get_full_name()} - {self.team.name} ({self.role})>'

    def get_role_display(self):
        """Return localized role display"""
        role_map = {
            'assistant_coach': 'Assistant Coach',
            'escort': 'Escort/Accompanier'
        }
        return role_map.get(self.role, self.role)
