# ABOUTME: Forms for creating and editing athlete insurance policies
# ABOUTME: Supports sports, accident, and civil liability insurance types

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from flask_babel import lazy_gettext as _l


class InsuranceForm(FlaskForm):
    """Form for creating/editing insurance policies."""

    policy_number = StringField(
        _l('Policy Number'),
        validators=[DataRequired(), Length(max=100)]
    )
    provider = StringField(
        _l('Provider'),
        validators=[DataRequired(), Length(max=200)]
    )
    insurance_type = SelectField(
        _l('Insurance Type'),
        choices=[
            ('sports', _l('Sports')),
            ('accident', _l('Accident')),
            ('civil_liability', _l('Civil Liability')),
        ],
        validators=[DataRequired()]
    )
    start_date = DateField(
        _l('Start Date'),
        validators=[DataRequired()]
    )
    end_date = DateField(
        _l('End Date'),
        validators=[DataRequired()]
    )
    coverage_amount = DecimalField(
        _l('Coverage Amount'),
        places=2,
        validators=[Optional()]
    )
    premium_amount = DecimalField(
        _l('Premium Amount'),
        places=2,
        validators=[Optional()]
    )
    notes = TextAreaField(
        _l('Notes'),
        validators=[Optional()]
    )
    submit = SubmitField(_l('Save'))
