from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional, ValidationError
from flask_babel import lazy_gettext as _l
from datetime import date


class StaffForm(FlaskForm):
    # Personal data
    first_name = StringField(_l('First Name'),
                      validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField(_l('Last Name'),
                         validators=[DataRequired(), Length(min=2, max=100)])
    birth_date = DateField(_l('Birth Date'),
                            validators=[DataRequired()],
                            format='%Y-%m-%d')
    birth_place = StringField(_l('Birth Place'),
                               validators=[DataRequired(), Length(max=100)])
    fiscal_code = StringField(_l('Fiscal Code'),
                                validators=[DataRequired(), Length(min=16, max=16),
                                          Regexp(r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$',
                                                message=_l('Enter a valid fiscal code'))])

    # Contact information
    phone = StringField(_l('Phone Number'),
                          validators=[DataRequired(), Length(min=10, max=20),
                                    Regexp(r'^[\d\s\+\-\(\)]+$', message=_l('Enter a valid phone number'))])
    email = StringField(_l('Email'),
                       validators=[DataRequired(), Email(), Length(max=120)])

    # Address
    street_address = StringField(_l('Street Address'),
                               validators=[DataRequired(), Length(max=200)])
    street_number = StringField(_l('Street Number'),
                                  validators=[DataRequired(), Length(max=10)])
    postal_code = StringField(_l('Postal Code'),
                               validators=[DataRequired(), Length(min=5, max=5),
                                         Regexp(r'^\d{5}$', message=_l('Enter a valid postal code'))])
    city = StringField(_l('City'),
                                  validators=[DataRequired(), Length(max=100)])
    province = StringField(_l('Province'),
                                     validators=[DataRequired(), Length(min=2, max=2),
                                               Regexp(r'^[A-Z]{2}$', message=_l('Enter a valid province code (e.g., BO)'))])

    # Document
    document_number = StringField(_l('Document Number'),
                                  validators=[DataRequired(), Length(max=50)])
    issuing_authority = StringField(_l('Issuing Authority'),
                                 validators=[DataRequired(), Length(max=100)])
    document_expiry = DateField(_l('Document Expiry'),
                                  validators=[DataRequired()],
                                  format='%Y-%m-%d')

    # Role in organization
    role = SelectField(_l('Role'),
                      choices=[
                          ('coach', _l('Coach')),
                          ('assistant_coach', _l('Assistant Coach')),
                          ('escort', _l('Escort')),
                          ('manager', _l('Manager')),
                          ('president', _l('President')),
                          ('vice_president', _l('Vice President')),
                          ('secretary', _l('Secretary'))
                      ],
                      validators=[DataRequired()])
    role_notes = TextAreaField(_l('Role Notes'),
                              validators=[Optional(), Length(max=500)])

    # Medical certificate
    has_medical_certificate = BooleanField(_l('Has Medical Certificate/Sports Booklet'))
    certificate_type = SelectField(_l('Certificate Type'),
                                  choices=[('', _l('Select...')),
                                          ('medical', _l('Medical Certificate')),
                                          ('sports_booklet', _l('Sports Booklet'))],
                                  validators=[Optional()])
    certificate_expiry = DateField(_l('Certificate Expiry'),
                                    validators=[Optional()],
                                    format='%Y-%m-%d')

    # Background check
    has_background_check = BooleanField(_l('Has Background Check'))
    background_check_date = DateField(_l('Background Check Date'),
                                       validators=[Optional()],
                                       format='%Y-%m-%d')
    background_check_expiry = DateField(_l('Background Check Expiry'),
                                         validators=[Optional()],
                                         format='%Y-%m-%d')

    submit = SubmitField(_l('Save Staff Member'))

    def validate_birth_date(self, field):
        """Validate that birth date is realistic"""
        if field.data:
            today = date.today()
            if field.data > today:
                raise ValidationError(_l('Birth date cannot be in the future'))
            age = today.year - field.data.year
            if age > 100:
                raise ValidationError(_l('Birth date seems unrealistic'))
            if age < 18:
                raise ValidationError(_l('Staff member must be at least 18 years old'))

    def validate_document_expiry(self, field):
        """Validate that document is not already expired"""
        if field.data and field.data < date.today():
            raise ValidationError(_l('Document is already expired'))

    def validate_certificate_expiry(self, field):
        """Validate certificate expiry if present"""
        if self.has_medical_certificate.data:
            if not self.certificate_type.data:
                raise ValidationError(_l('Specify certificate type'))
            if not field.data:
                raise ValidationError(_l('Specify certificate expiry date'))

    def validate_background_check_expiry(self, field):
        """Validate background check expiry if present"""
        if self.has_background_check.data:
            if not self.background_check_date.data:
                raise ValidationError(_l('Specify background check date'))
            if not field.data:
                raise ValidationError(_l('Specify background check expiry date'))

    def validate_background_check_date(self, field):
        """Validate background check date is not in the future"""
        if field.data and field.data > date.today():
            raise ValidationError(_l('Background check date cannot be in the future'))
