# ABOUTME: Form for adding and editing emergency contacts for athletes
# ABOUTME: Supports doctor, relative, and other contact types with medical notes

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional
from flask_babel import lazy_gettext as _l


class EmergencyContactForm(FlaskForm):
    contact_name = StringField(_l('Contact Name'),
                               validators=[DataRequired(), Length(max=200)])
    relationship = SelectField(_l('Relationship'),
                               choices=[('doctor', _l('Doctor')),
                                        ('relative', _l('Relative')),
                                        ('other', _l('Other'))],
                               validators=[DataRequired()])
    phone = StringField(_l('Phone'),
                        validators=[DataRequired(), Length(max=20)])
    email = StringField(_l('Email'),
                        validators=[Optional(), Email(), Length(max=120)])
    is_primary_doctor = BooleanField(_l('Primary Doctor'))
    medical_notes = TextAreaField(_l('Medical Notes'),
                                 validators=[Optional(), Length(max=1000)])
    submit = SubmitField(_l('Save Contact'))
