# ABOUTME: Match and lineup models for tracking games, results, and player participation
# ABOUTME: Supports league, friendly, tournament, and cup matches with full lineup management

from datetime import datetime, date
from flask_babel import gettext as _
from app import db


class Match(db.Model):
    """Match/game tracking with opponent, score, and result"""

    __tablename__ = 'matches'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Match details
    date = db.Column(db.Date, nullable=False, index=True)
    kick_off_time = db.Column(db.Time)
    opponent = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    is_home = db.Column(db.Boolean, default=True, nullable=False)
    match_type = db.Column(db.String(50), nullable=False, index=True)  # league, friendly, tournament, cup

    # Foreign keys
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'))

    # Score and result
    score_home = db.Column(db.Integer)
    score_away = db.Column(db.Integer)
    result = db.Column(db.String(20))  # win, loss, draw

    # Status
    status = db.Column(db.String(20), nullable=False, default='scheduled', index=True)  # scheduled, completed, cancelled, postponed

    # Notes
    notes = db.Column(db.Text)

    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_match_date_team', 'date', 'team_id'),
        db.Index('idx_match_season', 'season_id'),
    )

    # Relationships
    team = db.relationship('Team', backref=db.backref('matches', lazy='dynamic'))
    season = db.relationship('Season', backref=db.backref('matches', lazy='dynamic'))
    creator = db.relationship('User', backref=db.backref('matches_created', lazy='dynamic'))
    lineups = db.relationship('MatchLineup', backref='match', lazy='dynamic',
                              cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Match {self.team.name if self.team else "?"} vs {self.opponent} ({self.date})>'

    def get_match_type_display(self):
        """Return localized match type display"""
        type_map = {
            'league': _('League'),
            'friendly': _('Friendly'),
            'tournament': _('Tournament'),
            'cup': _('Cup')
        }
        return type_map.get(self.match_type, self.match_type)

    def get_status_display(self):
        """Return localized status display"""
        status_map = {
            'scheduled': _('Scheduled'),
            'completed': _('Completed'),
            'cancelled': _('Cancelled'),
            'postponed': _('Postponed')
        }
        return status_map.get(self.status, self.status)

    def get_result_display(self):
        """Return localized result display"""
        if not self.result:
            return '-'
        result_map = {
            'win': _('Win'),
            'loss': _('Loss'),
            'draw': _('Draw')
        }
        return result_map.get(self.result, self.result)

    def get_score_display(self):
        """Return formatted score or dash if no score recorded"""
        if self.score_home is not None and self.score_away is not None:
            return f'{self.score_home} - {self.score_away}'
        return '-'

    def is_past(self):
        """Check if the match date is in the past"""
        return self.date < date.today()


class MatchLineup(db.Model):
    """Player lineup entry for a match, tracking position and role"""

    __tablename__ = 'match_lineups'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False)

    # Lineup details
    position = db.Column(db.String(50))  # e.g. "Prop", "Hooker", "Fly-half"
    jersey_number = db.Column(db.Integer)
    is_starter = db.Column(db.Boolean, default=True, nullable=False)
    is_captain = db.Column(db.Boolean, default=False, nullable=False)

    # Notes
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Constraints and indexes
    __table_args__ = (
        db.UniqueConstraint('match_id', 'athlete_id', name='uq_match_athlete'),
        db.Index('idx_lineup_match', 'match_id'),
        db.Index('idx_lineup_athlete', 'athlete_id'),
    )

    # Relationships
    athlete = db.relationship('Athlete', backref=db.backref('match_lineups', lazy='dynamic'))

    def __repr__(self):
        return f'<MatchLineup {self.athlete.get_full_name() if self.athlete else "?"} - Match #{self.match_id}>'
