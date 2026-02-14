from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from flask_babel import lazy_gettext as _l


class TeamForm(FlaskForm):
    """Form for creating/editing teams"""

    name = StringField(_l('Team Name'), validators=[DataRequired(), Length(max=100)])
    description = TextAreaField(_l('Description'), validators=[Optional()])
    age_group = StringField(_l('Age Group'), validators=[Optional(), Length(max=50)])
    season = StringField(_l('Season'), validators=[Optional(), Length(max=20)])
    head_coach_id = SelectField(_l('Head Coach'),
                                coerce=lambda x: int(x) if x and str(x).strip() else None,
                                validators=[Optional()])
    submit = SubmitField(_l('Save Team'))


class TeamStaffAssignmentForm(FlaskForm):
    """Form for assigning staff to teams"""

    staff_id = SelectField(_l('Staff Member'), coerce=int, validators=[DataRequired()])
    role = SelectField(
        _l('Role'),
        choices=[
            ('assistant_coach', _l('Assistant Coach')),
            ('escort', _l('Escort/Accompanier'))
        ],
        validators=[DataRequired()]
    )
    assigned_date = DateField(_l('Assignment Date'), validators=[DataRequired()])
    notes = TextAreaField(_l('Notes'), validators=[Optional()])
    submit = SubmitField(_l('Assign Staff'))
