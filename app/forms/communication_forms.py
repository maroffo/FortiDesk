# ABOUTME: Forms for creating and filtering announcements
# ABOUTME: Supports team targeting and announcement type selection

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from flask_babel import lazy_gettext as _l


class AnnouncementForm(FlaskForm):
    """Form for creating announcements"""

    subject = StringField(
        _l('Subject'),
        validators=[DataRequired(), Length(max=200)]
    )
    body = TextAreaField(
        _l('Body'),
        validators=[DataRequired()]
    )
    announcement_type = SelectField(
        _l('Type'),
        choices=[
            ('general', _l('General')),
            ('training', _l('Training')),
            ('match', _l('Match')),
            ('administrative', _l('Administrative')),
        ],
        validators=[DataRequired()]
    )
    team_id = SelectField(
        _l('Team'),
        coerce=lambda x: int(x) if x and str(x).strip() else None,
        validators=[Optional()]
    )
    send_email = BooleanField(
        _l('Send email notification'),
        default=False
    )
    submit = SubmitField(_l('Create Announcement'))
