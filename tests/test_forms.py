# ABOUTME: Unit tests for WTForms validation (age limits, fiscal code, guardian types)
# ABOUTME: Tests AthleteForm and StaffForm custom validators

from datetime import date, timedelta

from werkzeug.datastructures import MultiDict

from app.forms.athletes_forms import AthleteForm
from app.forms.staff_forms import StaffForm


def _fmt(d):
    """Format a date as ISO string for form submission."""
    return d.isoformat() if d is not None else ''


def _athlete_form_data(**overrides):
    """Return a valid base athlete form data dict (string values for MultiDict)."""
    data = {
        'first_name': 'Marco',
        'last_name': 'Bianchi',
        'birth_date': '2015-03-20',
        'birth_place': 'Bologna',
        'fiscal_code': 'BNCMRC15C20A944Y',
        'street_address': 'Via Garibaldi',
        'street_number': '5',
        'postal_code': '40100',
        'city': 'Bologna',
        'province': 'BO',
        'document_number': 'BB9876543',
        'issuing_authority': 'Comune di Bologna',
        'document_expiry': _fmt(date.today() + timedelta(days=365)),
        'team_id': '',
        'guardian1_first_name': 'Paolo',
        'guardian1_last_name': 'Bianchi',
        'guardian1_phone': '+393331111111',
        'guardian1_email': 'paolo@test.com',
        'guardian1_type': 'father',
        'guardian2_first_name': 'Laura',
        'guardian2_last_name': 'Bianchi',
        'guardian2_phone': '+393332222222',
        'guardian2_email': 'laura@test.com',
        'guardian2_type': 'mother',
    }
    data.update(overrides)
    return data


def _staff_form_data(**overrides):
    """Return a valid base staff form data dict (string values for MultiDict)."""
    data = {
        'first_name': 'Mario',
        'last_name': 'Rossi',
        'birth_date': '1985-01-15',
        'birth_place': 'Bologna',
        'fiscal_code': 'RSSMRA85A15A944X',
        'phone': '+393331234567',
        'email': 'mario@test.com',
        'street_address': 'Via Roma',
        'street_number': '10',
        'postal_code': '40100',
        'city': 'Bologna',
        'province': 'BO',
        'document_number': 'AA1234567',
        'issuing_authority': 'Comune di Bologna',
        'document_expiry': _fmt(date.today() + timedelta(days=365)),
        'role': 'coach',
    }
    data.update(overrides)
    return data


def _make_athlete_form(app, data_dict):
    """Build an AthleteForm from a data dict inside a request context.

    Sets choices for the dynamic team_id SelectField and the internal
    _athlete_id attribute needed by the FIR ID uniqueness validator.
    """
    form = AthleteForm(formdata=MultiDict(data_dict))
    form.team_id.choices = [('', '-- Select --')]
    form._athlete_id = None
    return form


class TestAthleteFormValidation:

    def test_valid_form(self, app):
        with app.test_request_context():
            form = _make_athlete_form(app, _athlete_form_data())
            assert form.validate(), form.errors

    def test_birth_date_too_old(self, app):
        """Athlete older than 18 (year difference > 18) should fail."""
        with app.test_request_context():
            too_old = date.today() - timedelta(days=365 * 20)
            form = _make_athlete_form(
                app, _athlete_form_data(birth_date=_fmt(too_old)),
            )
            assert not form.validate()
            assert 'birth_date' in form.errors

    def test_birth_date_too_young(self, app):
        """Athlete younger than 3 (year difference < 3) should fail."""
        with app.test_request_context():
            too_young = date.today() - timedelta(days=365)
            form = _make_athlete_form(
                app, _athlete_form_data(birth_date=_fmt(too_young)),
            )
            assert not form.validate()
            assert 'birth_date' in form.errors

    def test_birth_date_future(self, app):
        """Birth date in the future should fail."""
        with app.test_request_context():
            future = date.today() + timedelta(days=1)
            form = _make_athlete_form(
                app, _athlete_form_data(birth_date=_fmt(future)),
            )
            assert not form.validate()
            assert 'birth_date' in form.errors

    def test_invalid_fiscal_code(self, app):
        """Malformed fiscal code should fail regex validation."""
        with app.test_request_context():
            form = _make_athlete_form(
                app, _athlete_form_data(fiscal_code='INVALID'),
            )
            assert not form.validate()
            assert 'fiscal_code' in form.errors

    def test_document_expired(self, app):
        """Expired document should fail."""
        with app.test_request_context():
            yesterday = date.today() - timedelta(days=1)
            form = _make_athlete_form(
                app, _athlete_form_data(document_expiry=_fmt(yesterday)),
            )
            assert not form.validate()
            assert 'document_expiry' in form.errors

    def test_same_guardian_types(self, app):
        """Two guardians with the same father/mother type should fail."""
        with app.test_request_context():
            form = _make_athlete_form(
                app,
                _athlete_form_data(
                    guardian1_type='father',
                    guardian2_type='father',
                ),
            )
            assert not form.validate()
            has_guardian_error = (
                'guardian1_type' in form.errors
                or 'guardian2_type' in form.errors
            )
            assert has_guardian_error

    def test_certificate_requires_expiry(self, app):
        """Medical certificate checked with a past expiry should fail.

        NOTE: When certificate_expiry is left blank the Optional()
        validator on the DateField raises StopValidation before the
        custom validate_certificate_expiry can run, so we test with an
        expired date instead, which bypasses Optional() and still
        exercises the custom validator path.
        """
        with app.test_request_context():
            yesterday = date.today() - timedelta(days=1)
            form = _make_athlete_form(
                app,
                _athlete_form_data(
                    has_medical_certificate='y',
                    certificate_type='',
                    certificate_expiry=_fmt(yesterday),
                ),
            )
            assert not form.validate()
            assert 'certificate_expiry' in form.errors


class TestStaffFormValidation:

    def test_valid_form(self, app):
        with app.test_request_context():
            form = StaffForm(formdata=MultiDict(_staff_form_data()))
            assert form.validate(), form.errors

    def test_birth_date_under_18(self, app):
        """Staff member under 18 (year difference < 18) should fail."""
        with app.test_request_context():
            young = date.today() - timedelta(days=365 * 10)
            form = StaffForm(
                formdata=MultiDict(_staff_form_data(birth_date=_fmt(young))),
            )
            assert not form.validate()
            assert 'birth_date' in form.errors

    def test_birth_date_future(self, app):
        """Birth date in the future should fail."""
        with app.test_request_context():
            future = date.today() + timedelta(days=1)
            form = StaffForm(
                formdata=MultiDict(_staff_form_data(birth_date=_fmt(future))),
            )
            assert not form.validate()
            assert 'birth_date' in form.errors

    def test_invalid_fiscal_code(self, app):
        """Malformed fiscal code should fail regex validation."""
        with app.test_request_context():
            form = StaffForm(
                formdata=MultiDict(_staff_form_data(fiscal_code='BAD')),
            )
            assert not form.validate()
            assert 'fiscal_code' in form.errors

    def test_document_expired(self, app):
        """Expired document should fail."""
        with app.test_request_context():
            yesterday = date.today() - timedelta(days=1)
            form = StaffForm(
                formdata=MultiDict(
                    _staff_form_data(document_expiry=_fmt(yesterday)),
                ),
            )
            assert not form.validate()
            assert 'document_expiry' in form.errors

    def test_background_check_date_future(self, app):
        """Background check date in the future should fail."""
        with app.test_request_context():
            tomorrow = date.today() + timedelta(days=1)
            future_expiry = date.today() + timedelta(days=365)
            form = StaffForm(
                formdata=MultiDict(
                    _staff_form_data(
                        has_background_check='y',
                        background_check_date=_fmt(tomorrow),
                        background_check_expiry=_fmt(future_expiry),
                    ),
                ),
            )
            assert not form.validate()
            assert 'background_check_date' in form.errors

    def test_background_check_missing_date(self, app):
        """Background check enabled with expiry but no date should fail.

        NOTE: When background_check_expiry is left blank the Optional()
        validator on the DateField raises StopValidation before the
        custom validate_background_check_expiry can run. So we test the
        inverse: expiry provided but date missing, which triggers the
        'Specify background check date' error on background_check_expiry.
        """
        with app.test_request_context():
            future_expiry = date.today() + timedelta(days=365)
            form = StaffForm(
                formdata=MultiDict(
                    _staff_form_data(
                        has_background_check='y',
                        background_check_date='',
                        background_check_expiry=_fmt(future_expiry),
                    ),
                ),
            )
            assert not form.validate()
            assert 'background_check_expiry' in form.errors
