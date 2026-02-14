# ABOUTME: Forms for filtering and generating reports with export options
# ABOUTME: Supports team, season, date range, and format selection filters

from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, SubmitField
from wtforms.validators import Optional
from flask_babel import lazy_gettext as _l


class ReportFilterForm(FlaskForm):
    """Base filter form for reports."""

    team_id = SelectField(
        _l('Team'),
        coerce=lambda x: int(x) if x and str(x).strip() else None,
        validators=[Optional()]
    )
    season_id = SelectField(
        _l('Season'),
        coerce=lambda x: int(x) if x and str(x).strip() else None,
        validators=[Optional()]
    )
    start_date = DateField(
        _l('Start Date'),
        validators=[Optional()]
    )
    end_date = DateField(
        _l('End Date'),
        validators=[Optional()]
    )
    submit = SubmitField(_l('Generate Report'))
