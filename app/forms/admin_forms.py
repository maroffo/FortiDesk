# ABOUTME: Admin panel forms for user management
# ABOUTME: User creation and editing with role assignment and uniqueness validation

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from flask_babel import lazy_gettext as _l
from app.models import User


class UserForm(FlaskForm):
    username = StringField(_l('Username'),
                          validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField(_l('Email'),
                       validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField(_l('First Name'),
                            validators=[DataRequired(), Length(max=100)])
    last_name = StringField(_l('Last Name'),
                           validators=[DataRequired(), Length(max=100)])
    role = SelectField(_l('Role'),
                      choices=[
                          ('admin', _l('Admin')),
                          ('coach', _l('Coach')),
                          ('parent', _l('Parent')),
                          ('player', _l('Player')),
                      ],
                      validators=[DataRequired()])
    password = PasswordField(_l('Password'),
                            validators=[Optional(), Length(min=6)])
    password2 = PasswordField(_l('Confirm Password'),
                             validators=[EqualTo('password',
                                                 message=_l('Passwords must match'))])
    submit = SubmitField(_l('Save'))

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, field):
        if field.data != self.original_username:
            user = User.query.filter_by(username=field.data).first()
            if user:
                raise ValidationError(_l('Username already in use.'))

    def validate_email(self, field):
        if field.data != self.original_email:
            user = User.query.filter_by(email=field.data).first()
            if user:
                raise ValidationError(_l('Email already in use.'))
