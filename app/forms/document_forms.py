# ABOUTME: Forms for document upload and search/filter functionality
# ABOUTME: Handles file validation, entity type selection, and expiry date tracking

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from flask_babel import lazy_gettext as _l


class DocumentUploadForm(FlaskForm):
    """Form for uploading documents associated with athletes or staff."""

    title = StringField(_l('Title'), validators=[DataRequired(), Length(max=200)])
    document_type = SelectField(
        _l('Document Type'),
        choices=[
            ('medical_certificate', _l('Medical Certificate')),
            ('id_document', _l('ID Document')),
            ('background_check', _l('Background Check')),
            ('insurance', _l('Insurance')),
            ('consent_form', _l('Consent Form')),
            ('other', _l('Other')),
        ],
        validators=[DataRequired()]
    )
    file = FileField(
        _l('File'),
        validators=[
            FileRequired(_l('Please select a file.')),
            FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], _l('Only PDF and image files (PNG, JPG) are allowed.'))
        ]
    )
    entity_type = SelectField(
        _l('Entity Type'),
        choices=[
            ('athlete', _l('Athlete')),
            ('staff', _l('Staff')),
        ],
        validators=[DataRequired()]
    )
    entity_id = SelectField(
        _l('Entity'),
        coerce=int,
        validators=[DataRequired()]
    )
    expiry_date = DateField(_l('Expiry Date'), validators=[Optional()])
    notes = TextAreaField(_l('Notes'), validators=[Optional()])
    submit = SubmitField(_l('Upload Document'))


class DocumentSearchForm(FlaskForm):
    """Form for filtering the document list."""

    document_type = SelectField(
        _l('Document Type'),
        choices=[
            ('', _l('All')),
            ('medical_certificate', _l('Medical Certificate')),
            ('id_document', _l('ID Document')),
            ('background_check', _l('Background Check')),
            ('insurance', _l('Insurance')),
            ('consent_form', _l('Consent Form')),
            ('other', _l('Other')),
        ],
        validators=[Optional()]
    )
    entity_type = SelectField(
        _l('Entity Type'),
        choices=[
            ('', _l('All')),
            ('athlete', _l('Athlete')),
            ('staff', _l('Staff')),
        ],
        validators=[Optional()]
    )
    expiring_within = SelectField(
        _l('Expiring Within'),
        choices=[
            ('', _l('Any')),
            ('30', _l('30 days')),
            ('60', _l('60 days')),
            ('90', _l('90 days')),
        ],
        validators=[Optional()]
    )
    submit = SubmitField(_l('Filter'))
