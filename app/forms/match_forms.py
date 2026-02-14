# ABOUTME: Forms for match management including scheduling, lineup, and result entry
# ABOUTME: Supports match CRUD, player lineup selection, and score recording

from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField, DateField,
                     TimeField, BooleanField, IntegerField, SubmitField)
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from flask_babel import lazy_gettext as _l


class MatchForm(FlaskForm):
    """Form for creating/editing matches"""

    date = DateField(_l('Date'), validators=[DataRequired()])
    kick_off_time = TimeField(_l('Kick-off Time'), validators=[Optional()])
    opponent = StringField(_l('Opponent'), validators=[DataRequired(), Length(max=200)])
    location = StringField(_l('Location'), validators=[Optional(), Length(max=200)])
    is_home = BooleanField(_l('Home Match'), default=True)
    match_type = SelectField(_l('Match Type'), choices=[
        ('league', _l('League')),
        ('friendly', _l('Friendly')),
        ('tournament', _l('Tournament')),
        ('cup', _l('Cup'))
    ], validators=[DataRequired()])
    team_id = SelectField(_l('Team'), coerce=int, validators=[DataRequired()])
    season_id = SelectField(_l('Season'),
                            coerce=lambda x: int(x) if x and str(x).strip() else None,
                            validators=[Optional()])
    notes = TextAreaField(_l('Notes'), validators=[Optional()])
    submit = SubmitField(_l('Save Match'))


class MatchResultForm(FlaskForm):
    """Form for entering/editing match results"""

    score_home = IntegerField(_l('Home Score'), validators=[DataRequired(), NumberRange(min=0)])
    score_away = IntegerField(_l('Away Score'), validators=[DataRequired(), NumberRange(min=0)])
    result = SelectField(_l('Result'), choices=[
        ('win', _l('Win')),
        ('loss', _l('Loss')),
        ('draw', _l('Draw'))
    ], validators=[DataRequired()])
    notes = TextAreaField(_l('Notes'), validators=[Optional()])
    submit = SubmitField(_l('Save Result'))


class MatchLineupForm(FlaskForm):
    """Not a standard form; lineup is handled via request.form checkboxes/inputs.
    This form provides CSRF protection only."""

    submit = SubmitField(_l('Save Lineup'))
