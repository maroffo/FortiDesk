# ABOUTME: Forms for season management (create, edit)
# ABOUTME: Validates season dates and name uniqueness

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from flask_babel import lazy_gettext as _l


class SeasonForm(FlaskForm):
    """Form for creating/editing seasons"""

    name = StringField(_l('Season Name'), validators=[DataRequired(), Length(max=20)])
    start_date = DateField(_l('Start Date'), validators=[DataRequired()])
    end_date = DateField(_l('End Date'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'), validators=[Optional()])
    submit = SubmitField(_l('Save Season'))

    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data <= self.start_date.data:
            raise ValidationError(_l('End date must be after start date.'))
