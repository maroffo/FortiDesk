from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_babel import lazy_gettext as _l
from datetime import date


class AttendanceForm(FlaskForm):
    """Form for recording individual attendance"""

    athlete_id = SelectField(_l('Athlete'), coerce=int, validators=[DataRequired()])
    date = DateField(_l('Date'), validators=[DataRequired()], default=date.today)
    session_type = SelectField(
        _l('Session Type'),
        choices=[
            ('training', _l('Training')),
            ('match', _l('Match')),
            ('event', _l('Event'))
        ],
        validators=[DataRequired()]
    )
    status = SelectField(
        _l('Status'),
        choices=[
            ('present', _l('Present')),
            ('absent', _l('Absent')),
            ('excused', _l('Excused')),
            ('late', _l('Late'))
        ],
        validators=[DataRequired()]
    )
    notes = TextAreaField(_l('Notes'), validators=[Optional()])
    submit = SubmitField(_l('Save Attendance'))


class BulkAttendanceForm(FlaskForm):
    """Form for recording attendance for multiple athletes at once"""

    training_session_id = SelectField(_l('Training Session'),
                                      coerce=lambda x: int(x) if x and str(x).strip() else None,
                                      validators=[Optional()])
    date = DateField(_l('Date'), validators=[DataRequired()], default=date.today)
    session_type = SelectField(
        _l('Session Type'),
        choices=[
            ('training', _l('Training')),
            ('match', _l('Match')),
            ('event', _l('Event'))
        ],
        validators=[DataRequired()]
    )
    notes = TextAreaField(_l('Session Notes'), validators=[Optional()])
    submit = SubmitField(_l('Save Attendance'))


class AttendanceReportForm(FlaskForm):
    """Form for filtering attendance reports"""

    team_id = SelectField(_l('Team'),
                          coerce=lambda x: int(x) if x and str(x).strip() else None,
                          validators=[Optional()])
    athlete_id = SelectField(_l('Athlete'),
                              coerce=lambda x: int(x) if x and str(x).strip() else None,
                              validators=[Optional()])
    start_date = DateField(_l('From Date'), validators=[Optional()])
    end_date = DateField(_l('To Date'), validators=[Optional()])
    session_type = SelectField(
        _l('Session Type'),
        choices=[
            ('', _l('All')),
            ('training', _l('Training')),
            ('match', _l('Match')),
            ('event', _l('Event'))
        ],
        validators=[Optional()]
    )
    status = SelectField(
        _l('Status'),
        choices=[
            ('', _l('All')),
            ('present', _l('Present')),
            ('absent', _l('Absent')),
            ('excused', _l('Excused')),
            ('late', _l('Late'))
        ],
        validators=[Optional()]
    )
    submit = SubmitField(_l('Generate Report'))
