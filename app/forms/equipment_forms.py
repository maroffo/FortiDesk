from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from flask_babel import lazy_gettext as _l


class EquipmentForm(FlaskForm):
    """Form for creating/editing equipment"""

    name = StringField(_l('Equipment Name'), validators=[DataRequired(), Length(max=100)])
    category = SelectField(
        _l('Category'),
        choices=[
            ('ball', _l('Ball')),
            ('jersey', _l('Jersey')),
            ('protective', _l('Protective Gear')),
            ('training_aid', _l('Training Aid')),
            ('other', _l('Other'))
        ],
        validators=[DataRequired()]
    )
    size = StringField(_l('Size'), validators=[Optional(), Length(max=20)])
    code = StringField(_l('Inventory Code'), validators=[DataRequired(), Length(max=50)])
    condition = SelectField(
        _l('Condition'),
        choices=[
            ('new', _l('New')),
            ('good', _l('Good')),
            ('fair', _l('Fair')),
            ('poor', _l('Poor')),
            ('damaged', _l('Damaged'))
        ],
        validators=[DataRequired()]
    )
    status = SelectField(
        _l('Status'),
        choices=[
            ('available', _l('Available')),
            ('assigned', _l('Assigned')),
            ('maintenance', _l('In Maintenance')),
            ('retired', _l('Retired'))
        ],
        validators=[DataRequired()]
    )
    purchase_date = DateField(_l('Purchase Date'), validators=[Optional()])
    purchase_price = DecimalField(_l('Purchase Price'), validators=[Optional()], places=2)
    supplier = StringField(_l('Supplier'), validators=[Optional(), Length(max=100)])
    location = StringField(_l('Storage Location'), validators=[Optional(), Length(max=100)])
    quantity = IntegerField(_l('Quantity'), validators=[Optional(), NumberRange(min=1)], default=1)
    description = TextAreaField(_l('Description'), validators=[Optional()])
    maintenance_notes = TextAreaField(_l('Maintenance Notes'), validators=[Optional()])
    last_maintenance_date = DateField(_l('Last Maintenance'), validators=[Optional()])
    next_maintenance_date = DateField(_l('Next Maintenance'), validators=[Optional()])
    submit = SubmitField(_l('Save Equipment'))


class EquipmentAssignmentForm(FlaskForm):
    """Form for assigning equipment to athletes"""

    equipment_id = SelectField(_l('Equipment'), coerce=int, validators=[DataRequired()])
    athlete_id = SelectField(_l('Athlete'), coerce=int, validators=[DataRequired()])
    assigned_date = DateField(_l('Assignment Date'), validators=[DataRequired()])
    expected_return_date = DateField(_l('Expected Return Date'), validators=[Optional()])
    condition_at_assignment = SelectField(
        _l('Condition at Assignment'),
        choices=[
            ('new', _l('New')),
            ('good', _l('Good')),
            ('fair', _l('Fair')),
            ('poor', _l('Poor')),
            ('damaged', _l('Damaged'))
        ],
        validators=[DataRequired()]
    )
    assignment_notes = TextAreaField(_l('Assignment Notes'), validators=[Optional()])
    submit = SubmitField(_l('Assign Equipment'))


class EquipmentReturnForm(FlaskForm):
    """Form for processing equipment returns"""

    actual_return_date = DateField(_l('Return Date'), validators=[DataRequired()])
    condition_at_return = SelectField(
        _l('Condition at Return'),
        choices=[
            ('new', _l('New')),
            ('good', _l('Good')),
            ('fair', _l('Fair')),
            ('poor', _l('Poor')),
            ('damaged', _l('Damaged'))
        ],
        validators=[DataRequired()]
    )
    return_notes = TextAreaField(_l('Return Notes'), validators=[Optional()])
    submit = SubmitField(_l('Process Return'))


class EquipmentSearchForm(FlaskForm):
    """Form for filtering equipment inventory"""

    category = SelectField(
        _l('Category'),
        choices=[
            ('', _l('All')),
            ('ball', _l('Ball')),
            ('jersey', _l('Jersey')),
            ('protective', _l('Protective Gear')),
            ('training_aid', _l('Training Aid')),
            ('other', _l('Other'))
        ],
        validators=[Optional()]
    )
    status = SelectField(
        _l('Status'),
        choices=[
            ('', _l('All')),
            ('available', _l('Available')),
            ('assigned', _l('Assigned')),
            ('maintenance', _l('In Maintenance')),
            ('retired', _l('Retired'))
        ],
        validators=[Optional()]
    )
    condition = SelectField(
        _l('Condition'),
        choices=[
            ('', _l('All')),
            ('new', _l('New')),
            ('good', _l('Good')),
            ('fair', _l('Fair')),
            ('poor', _l('Poor')),
            ('damaged', _l('Damaged'))
        ],
        validators=[Optional()]
    )
    submit = SubmitField(_l('Filter'))
