# ABOUTME: Forms for training session management (create, edit, cancel, generate recurring)
# ABOUTME: Supports session scheduling with team, coach, and season selection

from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, TimeField, SelectField,
    TextAreaField, SubmitField
)
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from flask_babel import lazy_gettext as _l


class TrainingSessionForm(FlaskForm):
    """Form for creating and editing a training session"""

    title = StringField(_l('Title'), validators=[DataRequired(), Length(max=200)])
    date = DateField(_l('Date'), validators=[DataRequired()])
    start_time = TimeField(_l('Start Time'), validators=[DataRequired()])
    end_time = TimeField(_l('End Time'), validators=[DataRequired()])
    location = StringField(_l('Location'), validators=[Optional(), Length(max=200)])
    session_type = SelectField(
        _l('Session Type'),
        choices=[
            ('training', _l('Training')),
            ('friendly', _l('Friendly Match')),
            ('tournament', _l('Tournament')),
            ('event', _l('Event'))
        ],
        validators=[DataRequired()]
    )
    team_id = SelectField(_l('Team'), coerce=int, validators=[DataRequired()])
    season_id = SelectField(
        _l('Season'),
        coerce=lambda x: int(x) if x and str(x).strip() else None,
        validators=[Optional()]
    )
    coach_id = SelectField(
        _l('Coach'),
        coerce=lambda x: int(x) if x and str(x).strip() else None,
        validators=[Optional()]
    )
    notes = TextAreaField(_l('Notes'), validators=[Optional()])
    submit = SubmitField(_l('Save Session'))

    def validate_end_time(self, field):
        if self.start_time.data and field.data and field.data <= self.start_time.data:
            raise ValidationError(_l('End time must be after start time.'))


class RecurringSessionForm(FlaskForm):
    """Form for generating recurring sessions from a template"""

    recurrence_day = SelectField(
        _l('Day of Week'),
        coerce=int,
        choices=[
            (0, _l('Monday')),
            (1, _l('Tuesday')),
            (2, _l('Wednesday')),
            (3, _l('Thursday')),
            (4, _l('Friday')),
            (5, _l('Saturday')),
            (6, _l('Sunday'))
        ],
        validators=[DataRequired()]
    )
    start_date = DateField(_l('Start Date'), validators=[DataRequired()])
    end_date = DateField(_l('End Date'), validators=[DataRequired()])
    title = StringField(_l('Title'), validators=[DataRequired(), Length(max=200)])
    start_time = TimeField(_l('Start Time'), validators=[DataRequired()])
    end_time = TimeField(_l('End Time'), validators=[DataRequired()])
    location = StringField(_l('Location'), validators=[Optional(), Length(max=200)])
    session_type = SelectField(
        _l('Session Type'),
        choices=[
            ('training', _l('Training')),
            ('friendly', _l('Friendly Match')),
            ('tournament', _l('Tournament')),
            ('event', _l('Event'))
        ],
        validators=[DataRequired()]
    )
    team_id = SelectField(_l('Team'), coerce=int, validators=[DataRequired()])
    season_id = SelectField(
        _l('Season'),
        coerce=lambda x: int(x) if x and str(x).strip() else None,
        validators=[Optional()]
    )
    coach_id = SelectField(
        _l('Coach'),
        coerce=lambda x: int(x) if x and str(x).strip() else None,
        validators=[Optional()]
    )
    notes = TextAreaField(_l('Notes'), validators=[Optional()])
    submit = SubmitField(_l('Generate Sessions'))

    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError(_l('End date must not be before start date.'))

    def validate_end_time(self, field):
        if self.start_time.data and field.data and field.data <= self.start_time.data:
            raise ValidationError(_l('End time must be after start time.'))


class CancelSessionForm(FlaskForm):
    """Form for cancelling a training session"""

    cancellation_reason = TextAreaField(_l('Cancellation Reason'), validators=[Optional()])
    submit = SubmitField(_l('Cancel Session'))
